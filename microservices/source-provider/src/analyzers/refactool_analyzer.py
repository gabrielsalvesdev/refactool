"""
Analisador específico para o projeto Refactool.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import structlog

from .code_analyzer import CodeAnalyzer, AnalysisConfig, CodeSmell
from .ai_analyzer import AIAnalyzer, AIAnalysisConfig, CodeSuggestion
from .ai_providers import DeepSeekProvider, OllamaProvider

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
    """
    Analisador especializado para o projeto Refactool.
    Combina análise estática e IA para fornecer insights sobre o código.
    """
    
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
    
    def __init__(self):
        # Configuração do analisador estático
        self.code_analyzer = CodeAnalyzer(AnalysisConfig(
            max_method_lines=30,
            max_complexity=10,
            max_class_lines=300,
            max_parameters=5,
            min_duplicate_lines=6,
            min_similarity=0.8
        ))
        
        # Configuração dos analisadores de IA
        self.deepseek_analyzer = self._setup_deepseek() if os.getenv("DEEPSEEK_API_KEY") else None
        self.ollama_analyzer = self._setup_ollama()
        
        # Cache de arquivos analisados
        self._analyzed_files: Set[str] = set()
        self._analysis_results: Dict[str, List[CodeSmell]] = {}
        self._suggestions: Dict[str, List[CodeSuggestion]] = {}
        
        # Contexto do projeto
        self.context = ProjectContext()
    
    def _setup_deepseek(self) -> AIAnalyzer:
        """Configura o analisador DeepSeek."""
        deepseek = DeepSeekProvider(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-coder-33b-instruct")
        )
        
        return AIAnalyzer(AIAnalysisConfig(
            provider=deepseek,
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "2000")),
            chunk_size=int(os.getenv("DEEPSEEK_CHUNK_SIZE", "1000"))
        ))
    
    def _setup_ollama(self) -> AIAnalyzer:
        """Configura o analisador Ollama."""
        ollama = OllamaProvider(
            api_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate"),
            model=os.getenv("OLLAMA_MODEL", "codellama")
        )
        
        return AIAnalyzer(AIAnalysisConfig(
            provider=ollama,
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", "2000")),
            chunk_size=int(os.getenv("OLLAMA_CHUNK_SIZE", "1000"))
        ))
    
    async def start(self):
        """Inicializa os analisadores."""
        if self.deepseek_analyzer:
            await self.deepseek_analyzer.start()
        await self.ollama_analyzer.start()
    
    async def stop(self):
        """Finaliza os analisadores."""
        if self.deepseek_analyzer:
            await self.deepseek_analyzer.stop()
        await self.ollama_analyzer.stop()
    
    async def analyze_project(self, root_dir: Optional[str] = None) -> None:
        """
        Analisa todo o projeto Refactool.
        
        Args:
            root_dir: Diretório raiz do projeto (opcional)
        """
        if not root_dir:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        try:
            await self.start()
            
            logger.info("refactool_analyzer.starting", root_dir=root_dir)
            
            # Primeira fase: Descoberta do projeto
            await self._discover_project_structure(root_dir)
            
            # Segunda fase: Análise de arquivos importantes
            await self._analyze_important_files()
            
            # Terceira fase: Análise de código
            await self._analyze_code_files()
            
            # Quarta fase: Análise de dependências
            await self._analyze_dependencies()
            
            # Quinta fase: Análise de arquitetura
            await self._analyze_architecture()
            
            # Sexta fase: Geração de relatório
            self._generate_report()
            
        finally:
            await self.stop()
    
    async def _discover_project_structure(self, root_dir: str) -> None:
        """Descobre a estrutura do projeto."""
        logger.info("refactool_analyzer.discovering_structure")
        
        for root, dirs, files in os.walk(root_dir):
            # Ignora diretórios que devem ser pulados
            dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self._should_skip_file(file_path):
                    continue
                
                # Identifica o tipo de arquivo
                ext = os.path.splitext(file)[1].lower()
                self.context.file_types[ext] = self.context.file_types.get(ext, 0) + 1
                
                # Identifica a linguagem
                if ext in self.LANGUAGE_EXTENSIONS:
                    lang = self.LANGUAGE_EXTENSIONS[ext]
                    self.context.languages[lang] = self.context.languages.get(lang, 0) + 1
                
                # Identifica arquivos importantes
                self._categorize_important_file(file_path)
    
    def _categorize_important_file(self, file_path: str) -> None:
        """Categoriza arquivos importantes do projeto."""
        file_name = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path)
        
        for category, patterns in self.IMPORTANT_FILES.items():
            for pattern in patterns:
                if pattern.endswith('/'):
                    if pattern[:-1] in rel_path.split(os.sep):
                        self._add_to_category(category, rel_path)
                        break
                elif file_name == pattern or rel_path.endswith(pattern):
                    self._add_to_category(category, rel_path)
                    break
    
    def _add_to_category(self, category: str, file_path: str) -> None:
        """Adiciona um arquivo à sua categoria no contexto."""
        if category == 'build':
            self.context.build_files.append(file_path)
        elif category == 'config':
            self.context.config_files.append(file_path)
        elif category == 'docs':
            self.context.documentation[file_path] = ''  # Será preenchido depois
    
    async def _analyze_important_files(self) -> None:
        """Analisa arquivos importantes do projeto."""
        logger.info("refactool_analyzer.analyzing_important_files")
        
        # Analisa arquivos de build para descobrir dependências
        for file_path in self.context.build_files:
            await self._analyze_build_file(file_path)
        
        # Analisa arquivos de configuração
        for file_path in self.context.config_files:
            await self._analyze_config_file(file_path)
        
        # Analisa documentação
        for file_path in self.context.documentation.keys():
            await self._analyze_documentation(file_path)
    
    async def _analyze_code_files(self) -> None:
        """Analisa arquivos de código."""
        logger.info("refactool_analyzer.analyzing_code")
        
        for lang, count in self.context.languages.items():
            logger.info(f"refactool_analyzer.analyzing_language", language=lang, files=count)
            
            # Encontra arquivos da linguagem
            files = self._find_files_by_language(lang)
            
            # Analisa cada arquivo
            for file_path in files:
                await self._analyze_file(file_path)
    
    def _find_files_by_language(self, language: str) -> List[str]:
        """Encontra arquivos de uma determinada linguagem."""
        extensions = [ext for ext, lang in self.LANGUAGE_EXTENSIONS.items() if lang == language]
        files = []
        
        for ext in extensions:
            for file_path in self._analyzed_files:
                if file_path.endswith(ext):
                    files.append(file_path)
        
        return files
    
    async def _analyze_dependencies(self) -> None:
        """Analisa dependências entre componentes."""
        logger.info("refactool_analyzer.analyzing_dependencies")
        
        # Análise será implementada aqui
        pass
    
    async def _analyze_architecture(self) -> None:
        """Analisa a arquitetura do projeto."""
        logger.info("refactool_analyzer.analyzing_architecture")
        
        # Análise será implementada aqui
        pass
    
    def _should_skip_directory(self, dir_name: str) -> bool:
        """Verifica se um diretório deve ser ignorado."""
        skip_patterns = {
            '__pycache__',
            '.venv',
            'venv',
            '.git',
            'node_modules',
            'dist',
            'build',
            'target',
            'bin',
            'obj'
        }
        return dir_name in skip_patterns
    
    def _should_skip_file(self, file_path: str) -> bool:
        """Verifica se um arquivo deve ser ignorado."""
        skip_patterns = [
            '__pycache__',
            '.pyc',
            '.pyo',
            '.pyd',
            '.so',
            '.dll',
            '.class',
            '.exe',
            '.obj',
            '.cache'
        ]
        
        return any(pattern in file_path for pattern in skip_patterns)
    
    async def _analyze_file(self, file_path: str) -> None:
        """Analisa um arquivo específico."""
        if file_path in self._analyzed_files:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = os.path.relpath(file_path)
            logger.info("refactool_analyzer.analyzing_file", file=rel_path)
            
            # Análise estática (se suportada para a linguagem)
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.py':
                code_smells = self.code_analyzer.analyze_file(file_path, content)
                self._analysis_results[file_path] = code_smells
            
            # Análise com IA
            suggestions = []
            if self.deepseek_analyzer:
                try:
                    deepseek_suggestions = await self.deepseek_analyzer.analyze_code(file_path, content)
                    suggestions.extend(deepseek_suggestions)
                except Exception as e:
                    logger.error("refactool_analyzer.deepseek_error", file=rel_path, error=str(e))
            
            try:
                ollama_suggestions = await self.ollama_analyzer.analyze_code(file_path, content)
                suggestions.extend(ollama_suggestions)
            except Exception as e:
                logger.error("refactool_analyzer.ollama_error", file=rel_path, error=str(e))
            
            self._suggestions[file_path] = suggestions
            self._analyzed_files.add(file_path)
            
        except Exception as e:
            logger.error("refactool_analyzer.file_analysis_error", file=file_path, error=str(e))
    
    async def _analyze_build_file(self, file_path: str) -> None:
        """Analisa um arquivo de build."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Identifica dependências baseado no tipo de arquivo
            if file_path.endswith('requirements.txt'):
                self._parse_python_requirements(content)
            elif file_path.endswith('package.json'):
                self._parse_npm_dependencies(content)
            elif file_path.endswith('pom.xml'):
                self._parse_maven_dependencies(content)
            # Adicionar mais parsers conforme necessário
            
        except Exception as e:
            logger.error("refactool_analyzer.build_file_error", file=file_path, error=str(e))
    
    def _parse_python_requirements(self, content: str) -> None:
        """Analisa arquivo requirements.txt."""
        deps = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                deps.append(line)
        self.context.dependencies['Python'] = deps
    
    def _parse_npm_dependencies(self, content: str) -> None:
        """Analisa arquivo package.json."""
        try:
            data = json.loads(content)
            deps = list(data.get('dependencies', {}).keys())
            dev_deps = list(data.get('devDependencies', {}).keys())
            self.context.dependencies['JavaScript'] = deps
            self.context.dependencies['JavaScript (dev)'] = dev_deps
        except json.JSONDecodeError:
            logger.error("refactool_analyzer.invalid_package_json")
    
    async def _analyze_config_file(self, file_path: str) -> None:
        """Analisa um arquivo de configuração."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analisa o arquivo com IA para entender sua função
            if self.deepseek_analyzer:
                prompt = f"""
                Analise este arquivo de configuração e explique:
                1. Qual é o propósito deste arquivo?
                2. Quais configurações importantes ele contém?
                3. Como ele afeta o funcionamento do projeto?
                
                Arquivo: {os.path.basename(file_path)}
                
                ```
                {content}
                ```
                """
                
                explanation = await self.deepseek_analyzer.explain_code(prompt)
                logger.info(
                    "refactool_analyzer.config_analysis",
                    file=file_path,
                    explanation=explanation
                )
            
        except Exception as e:
            logger.error("refactool_analyzer.config_file_error", file=file_path, error=str(e))
    
    async def _analyze_documentation(self, file_path: str) -> None:
        """Analisa um arquivo de documentação."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.context.documentation[file_path] = content
            
            # Analisa a documentação com IA
            if self.deepseek_analyzer:
                prompt = f"""
                Analise esta documentação e extraia:
                1. Principais funcionalidades descritas
                2. Arquitetura do sistema
                3. Requisitos técnicos
                4. Instruções de configuração
                5. Guias de desenvolvimento
                
                Arquivo: {os.path.basename(file_path)}
                
                ```
                {content}
                ```
                """
                
                analysis = await self.deepseek_analyzer.explain_code(prompt)
                logger.info(
                    "refactool_analyzer.documentation_analysis",
                    file=file_path,
                    analysis=analysis
                )
            
        except Exception as e:
            logger.error("refactool_analyzer.documentation_error", file=file_path, error=str(e))
    
    def _generate_report(self) -> None:
        """Gera um relatório completo da análise."""
        print("\n=== Relatório de Análise da Refactool ===")
        
        # Visão geral do projeto
        print("\n=== Visão Geral do Projeto ===")
        print(f"Total de arquivos analisados: {len(self._analyzed_files)}")
        
        # Linguagens utilizadas
        print("\n=== Linguagens Utilizadas ===")
        for lang, count in sorted(self.context.languages.items(), key=lambda x: x[1], reverse=True):
            print(f"- {lang}: {count} arquivos")
        
        # Dependências
        print("\n=== Dependências ===")
        for lang, deps in self.context.dependencies.items():
            print(f"\n{lang}:")
            for dep in deps:
                print(f"  - {dep}")
        
        # Arquivos importantes
        print("\n=== Arquivos Importantes ===")
        if self.context.build_files:
            print("\nArquivos de Build:")
            for file in self.context.build_files:
                print(f"  - {file}")
        
        if self.context.config_files:
            print("\nArquivos de Configuração:")
            for file in self.context.config_files:
                print(f"  - {file}")
        
        # Problemas encontrados
        total_smells = sum(len(smells) for smells in self._analysis_results.values())
        total_suggestions = sum(len(sugs) for sugs in self._suggestions.values())
        
        print("\n=== Problemas e Sugestões ===")
        print(f"Total de problemas encontrados: {total_smells}")
        print(f"Total de sugestões de melhoria: {total_suggestions}")
        
        # Problemas mais comuns
        smell_types = {}
        for smells in self._analysis_results.values():
            for smell in smells:
                smell_types[smell.type.value] = smell_types.get(smell.type.value, 0) + 1
        
        if smell_types:
            print("\nProblemas mais comuns:")
            for smell_type, count in sorted(smell_types.items(), key=lambda x: x[1], reverse=True):
                print(f"- {smell_type}: {count} ocorrências")
        
        # Detalhes por arquivo
        print("\n=== Detalhes por Arquivo ===")
        for file_path in sorted(self._analyzed_files):
            rel_path = os.path.relpath(file_path)
            smells = self._analysis_results.get(file_path, [])
            suggestions = self._suggestions.get(file_path, [])
            
            if smells or suggestions:
                print(f"\n{rel_path}:")
                if smells:
                    print(f"  Problemas encontrados: {len(smells)}")
                    for smell in smells:
                        print(f"  - Linha {smell.line}: {smell.message}")
                
                if suggestions:
                    print(f"  Sugestões de melhoria: {len(suggestions)}")
                    for suggestion in suggestions:
                        print(f"  - Linha {suggestion.line}: {suggestion.explanation}")

async def analyze_refactool():
    """Função principal para análise da Refactool."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project()

if __name__ == "__main__":
    asyncio.run(analyze_refactool()) 