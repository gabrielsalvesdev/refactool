"""
Script para análise de repositórios.
"""

import argparse
import asyncio
import json
import os
import shutil
import stat
from pathlib import Path
import structlog
from config import DEFAULT_CONFIG
from analyzers.code_analyzer import CodeAnalyzer
from analyzers.ai_analyzer import AIAnalyzer, AIAnalysisConfig
from analyzers.ai_providers import OllamaProvider, OpenAIProvider, DeepSeekProvider, GeminiProvider
from analyzers.refactool_analyzer import RefactoolAnalyzer
from analyzers.github_manager import GitHubManager
import git
import logging

logger = structlog.get_logger()

def remove_readonly(func, path, _):
    """Remove atributo somente leitura e tenta a operação novamente."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def load_config(config_file: str = None) -> dict:
    """Carrega configuração do arquivo ou usa padrão."""
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG

async def setup_ai_provider(config: dict, provider_override: str = None) -> AIAnalyzer:
    """Configura o provedor de IA baseado nas configurações."""
    # Se o provedor foi especificado via linha de comando, use-o
    if provider_override:
        config['ai_provider'] = provider_override
    
    # Tenta usar Gemini se a chave estiver disponível
    if os.getenv("GEMINI_API_KEY"):
        provider = GeminiProvider(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        logger.info("Usando Gemini como provedor de IA")
    # Tenta usar OpenAI se a chave estiver disponível
    elif os.getenv("OPENAI_API_KEY"):
        provider = OpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_url=config["openai_url"],
            model=config["openai_model"]
        )
        logger.info("Usando OpenAI como provedor de IA")
    # Tenta usar DeepSeek se a chave estiver disponível
    elif os.getenv("DEEPSEEK_API_KEY"):
        provider = DeepSeekProvider(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_url=config["deepseek_url"],
            model=config["deepseek_model"]
        )
        logger.info("Usando DeepSeek como provedor de IA")
    # Usa Ollama como fallback
    else:
        provider = OllamaProvider(
            model=config["ollama_model"],
            api_url=config["ollama_url"],
            timeout=config["ollama_timeout"]
        )
        logger.info("Usando Ollama como provedor de IA")
    
    return AIAnalyzer(AIAnalysisConfig(
        provider=provider,
        temperature=config.get("temperature", 0.3),
        max_tokens=config.get("max_tokens", 1000),
        chunk_size=config.get("chunk_size", 1000)
    ))

async def analyze_repository(
    repo_url: str,
    output_file: str = None,
    config_file: str = None,
    provider: str = None
) -> str:
    """
    Analisa um repositório do GitHub.
    
    Args:
        repo_url: URL do repositório
        output_file: Arquivo para salvar o relatório (opcional)
        config_file: Arquivo de configuração (opcional)
        provider: Provedor de IA a ser usado (opcional)
        
    Returns:
        Relatório da análise
    """
    github = None
    temp_dir = None
    try:
        # Carrega configuração
        config = load_config(config_file)
        
        # Configura o provedor de IA
        ai_analyzer = await setup_ai_provider(config, provider)
        
        # Configura o analisador de código
        code_analyzer = CodeAnalyzer()
        
        # Configura o analisador do Refactool
        refactool_analyzer = RefactoolAnalyzer(code_analyzer, ai_analyzer)
        
        # Configura o gerenciador do GitHub
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            logger.warning("Token do GitHub não encontrado. Alguns repositórios podem não ser acessíveis.")
        
        github = GitHubManager(token=github_token)
        await github.start()
        
        # Cria diretório temporário
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        temp_dir = os.path.join('temp', repo_name)
        
        logger.info("Iniciando clonagem do repositório", url=repo_url, target_dir=temp_dir)
        
        # Clona o repositório
        await github.clone_repository(repo_url, temp_dir)
        
        # Verifica se o diretório foi criado e tem arquivos
        if not os.path.exists(temp_dir):
            raise Exception(f"Diretório {temp_dir} não foi criado após clonagem")
            
        files = os.listdir(temp_dir)
        if not files:
            raise Exception(f"Diretório {temp_dir} está vazio após clonagem")
            
        logger.info(f"Repositório clonado com sucesso. {len(files)} arquivos encontrados.")
        
        # Analisa o repositório
        logger.info("Iniciando análise do repositório")
        report = await refactool_analyzer.analyze_project(temp_dir)
        
        # Salva o relatório se um arquivo de saída foi especificado
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Relatório salvo em {output_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"Erro durante a análise: {str(e)}")
        raise
    finally:
        # Limpa recursos
        if github:
            await github.stop()
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, onerror=remove_readonly)
            except Exception as e:
                logger.error(f"Erro ao remover diretório temporário: {str(e)}")

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description='Analisa um repositório do GitHub')
    parser.add_argument('repo_url', help='URL do repositório do GitHub')
    parser.add_argument('-o', '--output', help='Arquivo para salvar o relatório')
    parser.add_argument('-c', '--config', help='Arquivo de configuração')
    parser.add_argument('-p', '--provider', help='Provedor de IA a ser usado')
    
    args = parser.parse_args()
    
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Executa a análise
    report = asyncio.run(analyze_repository(
        args.repo_url,
        args.output,
        args.config,
        args.provider
    ))
    
    # Imprime o relatório se nenhum arquivo de saída foi especificado
    if not args.output:
        print(report)

if __name__ == '__main__':
    main() 