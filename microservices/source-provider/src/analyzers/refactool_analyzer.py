"""
Analisador de código para o Refactool.
"""

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import structlog
from collections import defaultdict

from .code_analyzer import CodeAnalyzer, AnalysisConfig, CodeSmell
from .ai_analyzer import AIAnalyzer, AIAnalysisConfig, CodeSuggestion
from .ai_providers import OpenAIProvider, OllamaProvider
from .github_manager import GitHubManager

logger = structlog.get_logger()

class ProjectContext:
    """Contexto do projeto para análise."""
    
    def __init__(self):
        self.languages: Dict[str, int] = {}  # Linguagens usadas e quantidade de arquivos
        self.dependencies: Dict[str, List[str]] = {}  # Dependências por linguagem
        self.frameworks: Dict[str, List[str]] = {}  # Frameworks por linguagem
        self.file_types: Dict[str, int] = {}  # Tipos de arquivo e quantidade
        self.architecture: Dict[str, List[str]] = {}  # Componentes arquiteturais
        self.test_coverage: Dict[str, float] = {}  # Cobertura de testes por componente
        self.documentation: Dict[str, str] = {}  # Documentação encontrada
        self.entry_points: List[str] = []  # Pontos de entrada da aplicação
        self.build_files: List[str] = []  # Arquivos de build/configuração
        self.config_files: List[str] = []  # Arquivos de configuração
        self.api_definitions: List[str] = []  # Definições de API
        self.database_schemas: List[str] = []  # Esquemas de banco de dados
        self.docs_files: List[str] = []  # Arquivos de documentação
        self.text_files: List[str] = []  # Arquivos de texto

class RefactoolAnalyzer:
    """Analisador principal do Refactool."""
    
    # Mapeamento de extensões para linguagens
    LANGUAGE_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.m': 'Objective-C',
        '.h': 'C/C++ Header',
        '.txt': 'Text',
        '.md': 'Markdown',
        '.rst': 'reStructuredText',
        '.ino': 'Arduino',
        '.ps1': 'PowerShell'
    }
    
    # Arquivos importantes para análise
    IMPORTANT_FILES = {
        'build': [
            'setup.py', 'requirements.txt', 'package.json', 'Cargo.toml',
            'build.gradle', 'pom.xml', 'Makefile', 'CMakeLists.txt'
        ],
        'config': [
            '.env', 'config.yaml', 'config.json', '.gitignore', 'docker-compose.yml',
            'Dockerfile', 'nginx.conf', 'webpack.config.js', 'tsconfig.json'
        ],
        'docs': [
            'README.md', 'CONTRIBUTING.md', 'API.md', 'CHANGELOG.md',
            'docs/', 'wiki/', 'specifications/'
        ],
        'tests': [
            'test/', 'tests/', 'spec/', '__tests__/',
            'pytest.ini', 'jest.config.js', 'phpunit.xml'
        ],
        'ci': [
            '.github/workflows/', '.gitlab-ci.yml', 'Jenkinsfile',
            'azure-pipelines.yml', '.travis.yml', '.circleci/'
        ]
    }
    
    # Extensões de arquivos binários para ignorar
    BINARY_EXTENSIONS = {'.deb', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.dll',
                        '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite', '.pyc', '.pyo',
                        '.idx', '.pack', '.rev'}
    
    def __init__(self, code_analyzer: CodeAnalyzer, ai_analyzer: AIAnalyzer):
        self.code_analyzer = code_analyzer
        self.ai_analyzer = ai_analyzer
        
        # Cache de arquivos analisados
        self._analyzed_files: Set[str] = set()
        self._analysis_results: Dict[str, List[CodeSmell]] = {}
        self._suggestions: Dict[str, List[CodeSuggestion]] = {}
        self._file_summaries: Dict[str, str] = {}
        
        # Contexto do projeto
        self.context = ProjectContext()
        
        self.ollama_provider = OllamaProvider()
        self.github = GitHubManager()
    
    async def start(self):
        """Inicializa os analisadores."""
        await self.ollama_provider.start()
        await self.github.start()
    
    async def stop(self):
        """Finaliza os analisadores."""
        await self.ollama_provider.stop()
        await self.github.stop()
    
    async def analyze_project(self, project_path: str) -> str:
        """Analisa um projeto e gera um relatório."""
        logger.info("Iniciando análise do projeto")
        
        total_files = 0
        total_lines = 0
        total_functions = 0
        total_classes = 0
        language_counts = defaultdict(int)
        file_analyses = []
        
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if not self._should_analyze_file(file_path):
                        continue
                        
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    relative_path = os.path.relpath(file_path, project_path)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # Analisa o arquivo
                    analysis = self.code_analyzer.analyze_file(content, file_ext)
                    analysis.file_path = relative_path
                    analysis.language = self.code_analyzer.LANGUAGE_EXTENSIONS.get(file_ext, 'Unknown')
                    
                    # Atualiza estatísticas de linguagem
                    language_counts[analysis.language] += 1
                    
                    # Gera resumo para todos os arquivos
                    try:
                        summary = await self.ai_analyzer.analyze_text(content)
                        self._file_summaries[relative_path] = summary
                        if analysis.language in ['Text', 'Markdown', 'reStructuredText']:
                            self.context.text_files.append(relative_path)
                    except Exception as e:
                        logger.error(f"Erro ao gerar resumo para {relative_path}: {e}")
                    
                    # Para arquivos de código, gera sugestões
                    if analysis.language not in ['Text', 'Markdown', 'reStructuredText']:
                        try:
                            suggestions = await self.ai_analyzer.analyze_code(content, analysis.language)
                            self._suggestions[relative_path] = suggestions
                        except Exception as e:
                            logger.error(f"Erro ao gerar sugestões para {relative_path}: {e}")
                    
                    # Atualiza métricas
                    analysis.total_lines = analysis.code_lines
                    analysis.blank_lines = analysis.code_lines - analysis.code_lines
                    analysis.max_line_length = analysis.max_line_length
                    analysis.avg_line_length = analysis.avg_line_length
                    analysis.complexity = analysis.complexity
                    analysis.functions = analysis.functions if isinstance(analysis.functions, list) else []
                    analysis.classes = analysis.classes if isinstance(analysis.classes, list) else []
                    
                    # Adiciona à lista de análises
                    file_analyses.append(analysis)
                    total_files += 1
                    total_lines += analysis.code_lines
                    total_functions += len(analysis.functions)
                    total_classes += len(analysis.classes)
                    
                except Exception as e:
                    logger.error(f"Erro ao analisar {file_path}: {e}")
                    continue
        
        # Gera o relatório em formato markdown
        report = "# Relatório de Análise do Projeto\n\n"
        
        # Visão Geral
        report += "## Visão Geral\n"
        report += f"- Total de arquivos: {total_files}\n"
        report += f"- Total de linhas: {total_lines}\n"
        report += f"- Total de funções: {total_functions}\n"
        report += f"- Total de classes: {total_classes}\n\n"
        
        # Linguagens
        report += "## Linguagens Utilizadas\n"
        for lang, count in language_counts.items():
            report += f"- {lang}: {count} arquivo(s)\n"
        report += "\n"
        
        # Análises detalhadas
        report += "## Análises de Arquivos\n\n"
        for analysis in file_analyses:
            report += f"### {analysis.file_path}\n"
            report += f"- Linguagem: {analysis.language}\n"
            report += f"- Linhas totais: {analysis.total_lines}\n"
            report += f"- Linhas em branco: {analysis.blank_lines}\n"
            report += f"- Linhas de conteúdo: {analysis.code_lines}\n"
            report += f"- Tamanho máximo de linha: {analysis.max_line_length}\n"
            report += f"- Tamanho médio de linha: {analysis.avg_line_length:.1f}\n"
            
            # Adiciona complexidade apenas para arquivos de código
            if analysis.language not in ['Text', 'Markdown', 'reStructuredText']:
                report += f"- Complexidade: {analysis.complexity:.1f}\n"
            
            # Adiciona resumo para todos os arquivos
            if analysis.file_path in self._file_summaries:
                report += "\n#### Resumo do Arquivo\n"
                report += self._file_summaries[analysis.file_path] + "\n"
            
            # Adiciona sugestões para arquivos de código
            if analysis.file_path in self._suggestions:
                suggestions = self._suggestions[analysis.file_path]
                if suggestions:
                    report += "\n#### Sugestões de Melhoria\n"
                    for suggestion in suggestions:
                        report += f"- Linha {suggestion.line}: {suggestion.message}\n"
                        if suggestion.suggested_code:
                            report += f"  Sugestão: {suggestion.suggested_code}\n"
                        if suggestion.explanation:
                            report += f"  Explicação: {suggestion.explanation}\n"
            
            report += "\n"
        
        return report
    
    def _should_analyze_file(self, file_path: str) -> bool:
        """Verifica se um arquivo deve ser analisado."""
        # Ignora arquivos binários conhecidos
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in self.BINARY_EXTENSIONS:
            return False
            
        # Ignora arquivos do git
        if os.path.sep + '.git' + os.path.sep in file_path:
            return False
            
        # Ignora arquivos muito grandes (mais de 5MB)
        try:
            if os.path.getsize(file_path) > 5 * 1024 * 1024:
                return False
        except OSError:
            return False
            
        return True

async def analyze_refactool():
    """Função principal para análise da Refactool."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project()

if __name__ == "__main__":
    asyncio.run(analyze_refactool()) 