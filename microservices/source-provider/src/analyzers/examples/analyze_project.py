"""
Exemplo de uso do RefactoolAnalyzer para análise de projetos.

Este script demonstra como utilizar o RefactoolAnalyzer para analisar
um projeto completo e gerar relatórios detalhados.
"""

import asyncio
import os
import sys
from pathlib import Path
import structlog
from dotenv import load_dotenv

# Adiciona o diretório pai ao PYTHONPATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from refactool_analyzer import RefactoolAnalyzer

# Configura logging estruturado
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger()

async def analyze_project(project_path: str):
    """
    Analisa um projeto usando o RefactoolAnalyzer.
    
    Args:
        project_path: Caminho para o diretório do projeto
    """
    try:
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Verifica se as chaves necessárias estão configuradas
        if not os.getenv("DEEPSEEK_API_KEY"):
            logger.warning("analyze_project.no_deepseek_key", 
                         message="DEEPSEEK_API_KEY não configurada. Análise será limitada.")
        
        if not os.getenv("OLLAMA_API_URL"):
            logger.warning("analyze_project.no_ollama_url",
                         message="OLLAMA_API_URL não configurada. Usando URL padrão.")
        
        # Inicializa o analisador
        analyzer = RefactoolAnalyzer()
        
        # Inicia a análise
        logger.info("analyze_project.starting", 
                   project_path=project_path)
        
        await analyzer.analyze_project(project_path)
        
        # Gera relatório em arquivo
        output_dir = os.path.join(project_path, "reports")
        os.makedirs(output_dir, exist_ok=True)
        
        report_file = os.path.join(output_dir, "refactool_analysis.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            # Redireciona temporariamente a saída padrão para o arquivo
            old_stdout = sys.stdout
            sys.stdout = f
            analyzer._generate_report()
            sys.stdout = old_stdout
        
        logger.info("analyze_project.completed",
                   report_file=report_file,
                   languages=list(analyzer.context.languages.keys()),
                   total_files=len(analyzer._analyzed_files))
        
        # Imprime um resumo no console
        print("\n=== Resumo da Análise ===")
        print(f"Projeto analisado: {project_path}")
        print(f"Total de arquivos: {len(analyzer._analyzed_files)}")
        print("\nLinguagens encontradas:")
        for lang, count in analyzer.context.languages.items():
            print(f"- {lang}: {count} arquivos")
        print(f"\nRelatório completo salvo em: {report_file}")
        
    except Exception as e:
        logger.error("analyze_project.error",
                    error=str(e),
                    exc_info=True)
        raise

def main():
    """Função principal."""
    if len(sys.argv) != 2:
        print("Uso: python analyze_project.py <caminho_do_projeto>")
        sys.exit(1)
    
    project_path = os.path.abspath(sys.argv[1])
    if not os.path.isdir(project_path):
        print(f"Erro: O diretório '{project_path}' não existe.")
        sys.exit(1)
    
    asyncio.run(analyze_project(project_path))

if __name__ == "__main__":
    main() 