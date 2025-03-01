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
        '.h': 'C/C++ Header'
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
        """
        Analisa um projeto completo e retorna um relatório
        """
        try:
            self.base_path = Path(project_path)
            files = self._scan_project_files(project_path)
            analysis_results = []
            
            for file_path in files:
                result = self._analyze_file(file_path)
                if result:
                    analysis_results.append(result)
            
            return self._generate_analysis_report(analysis_results)
            
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Erro ao acessar arquivos: {str(e)}")
            return "Erro ao acessar arquivos do projeto"
        except Exception as e:
            logger.error(f"Erro inesperado na análise: {str(e)}", exc_info=True)
            return "Erro ao analisar projeto"
    
    def _scan_project_files(self, project_path: str) -> List[str]:
        """
        Scan the project directory and return a list of file paths
        """
        files = []
        root_path = Path(project_path)
        for file_path in root_path.rglob('*'):
            if not file_path.is_file():
                continue
                
            file_ext = file_path.suffix.lower()
            if not file_ext or file_ext in self.BINARY_EXTENSIONS:
                continue
                
            files.append(str(file_path.relative_to(root_path)))
        
        return files
    
    def _analyze_file(self, file_path: str) -> Optional[CodeSmell]:
        """
        Analyze a single file and return the analysis result
        """
        try:
            path = self.base_path / file_path
            content = path.read_text(encoding='utf-8')
            analysis = self.code_analyzer.analyze_file(content, path.suffix[1:])
            analysis.file_path = file_path
            return analysis
        except Exception as e:
            logger.warning(
                "refactool_analyzer.file_read_failed",
                file=file_path,
                error=str(e)
            )
            return None
    
    def _generate_analysis_report(self, analysis_results: List[CodeSmell]) -> str:
        """
        Generate a report from the analysis results
        """
        report = [
            "# Relatório de Análise do Projeto",
            "",
            "## Visão Geral",
            f"- Total de arquivos: {len(analysis_results)}",
            f"- Total de linhas de código: {sum(analysis.total_lines for analysis in analysis_results)}",
            f"- Total de funções: {sum(analysis.total_functions for analysis in analysis_results)}", 
            f"- Total de classes: {sum(analysis.total_classes for analysis in analysis_results)}",
            "",
            "## Linguagens Utilizadas"
        ]
        
        languages = {}
        for analysis in analysis_results:
            if hasattr(analysis, 'file_path'):
                ext = Path(analysis.file_path).suffix
                lang = self.LANGUAGE_EXTENSIONS.get(ext, 'Unknown')
                if lang in languages:
                    languages[lang] += 1
                else:
                    languages[lang] = 1
            
        for lang, count in languages.items():
            report.append(f"- {lang}: {count} arquivo(s)")
            
        if analysis_results:
            report.extend([
                "",
                "## Análises de Arquivos"
            ])
            
            for analysis in analysis_results:
                if hasattr(analysis, 'file_path'):
                    report.extend([
                        f"\n### {analysis.file_path}",
                        f"- Linhas totais: {analysis.total_lines}",
                        f"- Linhas em branco: {analysis.metrics.blank_lines}",
                        f"- Linhas de código: {analysis.metrics.code_lines}",
                        f"- Tamanho máximo de linha: {analysis.metrics.max_line_length}",
                        f"- Tamanho médio de linha: {analysis.metrics.avg_line_length:.1f}",
                        f"- Complexidade: {analysis.metrics.complexity:.1f}"
                    ])
                    
                    if analysis.functions:
                        report.append("\nFunções:")
                        for func in analysis.functions:
                            report.append(f"- {func}")
                            
                    if analysis.classes:
                        report.append("\nClasses:")
                        for cls in analysis.classes:
                            report.append(f"- {cls}")
        
        return "\n".join(report)

async def analyze_refactool():
    """Função principal para análise da Refactool."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project()

if __name__ == "__main__":
    asyncio.run(analyze_refactool()) 