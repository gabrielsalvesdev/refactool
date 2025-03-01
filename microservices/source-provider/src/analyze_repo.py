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
    config_file: str = None
) -> str:
    """
    Analisa um repositório do GitHub.
    
    Args:
        repo_url: URL do repositório
        output_file: Arquivo para salvar o relatório (opcional)
        config_file: Arquivo de configuração (opcional)
        
    Returns:
        Relatório da análise
    """
    github = None
    try:
        # Carrega configuração
        config = load_config(config_file)
        
        # Configura logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer()
            ]
        )
        
        # Prepara diretório temporário
        repo_name = repo_url.split('/')[-1]
        temp_dir = os.path.join(config["temp_dir"], repo_name)
        
        # Limpa diretório temporário se existir
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, onerror=remove_readonly)
            except Exception as e:
                logger.error(f"Erro ao limpar diretório temporário: {str(e)}")
                
        # Cria diretório temporário
        os.makedirs(temp_dir, exist_ok=True)
            
        # Clona repositório
        github = GitHubManager()
        await github.start()
        await github.clone_repository(repo_url, temp_dir)
        
        # Inicializa analisadores
        code_analyzer = CodeAnalyzer()
        ai_analyzer = await setup_ai_provider(config)
        
        # Inicializa analisador principal
        analyzer = RefactoolAnalyzer(code_analyzer, ai_analyzer)
        
        # Executa análise com timeout
        result = await asyncio.wait_for(
            analyzer.analyze_project(temp_dir),
            timeout=config["timeout"]
        )
        
        # Salva resultado se necessário
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
        
        return result
        
    except asyncio.TimeoutError:
        logger.error("Timeout durante análise")
        return "Erro: A análise excedeu o tempo limite."
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        return f"Erro fatal: {str(e)}"
    finally:
        # Finaliza GitHub
        if github:
            await github.stop()
            
        # Limpa diretório temporário
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, onerror=remove_readonly)
            except Exception as e:
                logger.error(f"Erro ao limpar diretório temporário: {str(e)}")

async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Analisa um repositório do GitHub.')
    parser.add_argument('url', help='URL do repositório')
    parser.add_argument('-o', '--output', help='Arquivo de saída')
    parser.add_argument('--provider', choices=['gemini', 'openai', 'deepseek', 'ollama'], 
                       help='Provedor de IA a ser usado (gemini, openai, deepseek, ollama)')
    parser.add_argument('--config', help='Arquivo de configuração opcional')
    args = parser.parse_args()
    
    # Configura o logger
    logging.basicConfig(level=logging.INFO)
    
    # Clona o repositório
    target_dir = os.path.join('temp', 'captool')
    try:
        if os.path.exists(target_dir):
            # Tenta remover o diretório, ignorando erros
            for root, dirs, files in os.walk(target_dir, topdown=False):
                for name in files:
                    try:
                        os.chmod(os.path.join(root, name), 0o777)
                        os.unlink(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.chmod(os.path.join(root, name), 0o777)
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
            try:
                os.rmdir(target_dir)
            except:
                pass
        
        os.makedirs(target_dir, exist_ok=True)
        
        repo = git.Repo.clone_from(args.url, target_dir)
        logger.info('Repositório clonado com sucesso', target_dir=target_dir, url=args.url)
        
        # Configura os analisadores
        config = load_config(args.config)
        ai_analyzer = await setup_ai_provider(config, args.provider)
        code_analyzer = CodeAnalyzer()
        
        # Cria o analisador principal
        analyzer = RefactoolAnalyzer(code_analyzer, ai_analyzer)
        
        # Analisa o projeto
        report = await analyzer.analyze_project(target_dir)
        
        # Salva o relatório
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
        else:
            print(report)
            
    except Exception as e:
        logger.error(f"Erro durante a análise: {str(e)}")
        raise
    finally:
        # Tenta limpar o diretório temporário
        try:
            if os.path.exists(target_dir):
                for root, dirs, files in os.walk(target_dir, topdown=False):
                    for name in files:
                        try:
                            os.chmod(os.path.join(root, name), 0o777)
                            os.unlink(os.path.join(root, name))
                        except:
                            pass
                    for name in dirs:
                        try:
                            os.chmod(os.path.join(root, name), 0o777)
                            os.rmdir(os.path.join(root, name))
                        except:
                            pass
                try:
                    os.rmdir(target_dir)
                except:
                    pass
        except:
            pass

if __name__ == '__main__':
    asyncio.run(main()) 