"""
Analisador estático de código.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import ast
import re
import structlog

logger = structlog.get_logger()

class CodeSmellType(Enum):
    """Tipos de problemas que podem ser encontrados no código."""
    LONG_METHOD = "long_method"
    HIGH_COMPLEXITY = "high_complexity"
    DUPLICATE_CODE = "duplicate_code"
    LARGE_CLASS = "large_class"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DATA_CLASS = "data_class"
    DEAD_CODE = "dead_code"
    FEATURE_ENVY = "feature_envy"
    GOD_CLASS = "god_class"
    PRIMITIVE_OBSESSION = "primitive_obsession"

@dataclass
class AnalysisConfig:
    """Configuração para análise de código."""
    max_method_lines: int = 30
    max_complexity: int = 10
    max_class_lines: int = 300
    max_parameters: int = 5
    min_duplicate_lines: int = 6
    min_similarity: float = 0.8

@dataclass
class CodeSmell:
    """Representa um problema encontrado no código."""
    type: CodeSmellType
    file: str
    line: int
    message: str
    severity: int  # 1 = baixa, 2 = média, 3 = alta
    suggestion: str

@dataclass
class CodeMetrics:
    """Métricas do código."""
    total_lines: int = 0
    blank_lines: int = 0
    code_lines: int = 0
    max_line_length: int = 0
    avg_line_length: float = 0.0
    complexity: float = 0.0

@dataclass
class CodeAnalysis:
    """Representa a análise de um arquivo de código."""
    file_path: str = ""
    language: Optional[str] = None
    total_lines: int = 0
    code_lines: int = 0
    blank_lines: int = 0
    max_line_length: int = 0
    avg_line_length: float = 0.0
    complexity: float = 0.0
    functions: list = field(default_factory=list)
    classes: list = field(default_factory=list)
    metrics: CodeMetrics = field(default_factory=CodeMetrics)

class CodeAnalyzer:
    """Analisador estático de código."""
    
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
        '.rst': 'reStructuredText'
    }
    
    def analyze_file(self, content: str, file_ext: str) -> CodeAnalysis:
        """
        Analisa um arquivo de código.
        
        Args:
            content: Conteúdo do arquivo
            file_ext: Extensão do arquivo
            
        Returns:
            Análise do arquivo
        """
        # Detecta a linguagem
        language = self.LANGUAGE_EXTENSIONS.get(file_ext.lower(), 'Unknown')
        
        # Se for um arquivo de texto, usa a análise de texto
        if language in ['Text', 'Markdown', 'reStructuredText']:
            return self.analyze_text(content, language)
        
        # Para arquivos de código, faz a análise específica da linguagem
        if language == 'Python':
            return self._analyze_python(content, file_ext)
        elif language in ['JavaScript', 'TypeScript']:
            return self._analyze_javascript(content, file_ext)
        else:
            # Para outras linguagens, faz uma análise básica
            return self._analyze_generic(content, file_ext)
    
    def analyze_text(self, content: str, language: str = 'Text') -> CodeAnalysis:
        """
        Analisa um arquivo de texto.
        
        Args:
            content: Conteúdo do arquivo
            language: Linguagem do arquivo
            
        Returns:
            Análise do arquivo
        """
        # Divide o conteúdo em linhas
        lines = content.split('\n')
        
        # Calcula métricas básicas
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        code_lines = total_lines - blank_lines
        
        # Calcula métricas de linha
        line_lengths = [len(line) for line in lines]
        max_line_length = max(line_lengths) if line_lengths else 0
        avg_line_length = sum(line_lengths) / total_lines if total_lines > 0 else 0
        
        # Cria a análise
        analysis = CodeAnalysis(
            language=language,
            total_lines=total_lines,
            code_lines=code_lines,
            blank_lines=blank_lines,
            max_line_length=max_line_length,
            avg_line_length=avg_line_length,
            complexity=0.0,  # Arquivos de texto não têm complexidade
            functions=[],    # Arquivos de texto não têm funções
            classes=[]       # Arquivos de texto não têm classes
        )
        
        # Atualiza as métricas
        analysis.metrics = CodeMetrics(
            total_lines=total_lines,
            blank_lines=blank_lines,
            code_lines=code_lines,
            max_line_length=max_line_length,
            avg_line_length=avg_line_length,
            complexity=0.0
        )
        
        return analysis
    
    def _analyze_python(self, content: str, file_ext: str) -> CodeAnalysis:
        """Analisa um arquivo Python."""
        try:
            # Parse o código
            tree = ast.parse(content)
            
            # Calcula métricas básicas
            lines = content.split('\n')
            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            code_lines = total_lines - blank_lines
            
            # Calcula métricas de linha
            line_lengths = [len(line) for line in lines]
            max_line_length = max(line_lengths) if line_lengths else 0
            avg_line_length = sum(line_lengths) / total_lines if total_lines > 0 else 0
            
            # Extrai funções e classes
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            # Calcula complexidade
            complexity = self._calculate_complexity(tree)
            
            # Cria a análise
            analysis = CodeAnalysis(
                language='Python',
                total_lines=total_lines,
                code_lines=code_lines,
                blank_lines=blank_lines,
                max_line_length=max_line_length,
                avg_line_length=avg_line_length,
                complexity=complexity,
                functions=functions,
                classes=classes
            )
            
            # Atualiza as métricas
            analysis.metrics = CodeMetrics(
                total_lines=total_lines,
                blank_lines=blank_lines,
                code_lines=code_lines,
                max_line_length=max_line_length,
                avg_line_length=avg_line_length,
                complexity=complexity
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo Python: {str(e)}")
            return self._analyze_generic(content, file_ext)
    
    def _analyze_javascript(self, content: str, file_ext: str) -> CodeAnalysis:
        """Analisa um arquivo JavaScript/TypeScript."""
        # Por enquanto, faz uma análise genérica
        return self._analyze_generic(content, file_ext)
    
    def _analyze_generic(self, content: str, file_ext: str) -> CodeAnalysis:
        """Faz uma análise genérica de um arquivo."""
        # Divide o conteúdo em linhas
        lines = content.split('\n')
        
        # Calcula métricas básicas
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        code_lines = total_lines - blank_lines
        
        # Calcula métricas de linha
        line_lengths = [len(line) for line in lines]
        max_line_length = max(line_lengths) if line_lengths else 0
        avg_line_length = sum(line_lengths) / total_lines if total_lines > 0 else 0
        
        # Detecta funções e classes usando regex
        functions = self._detect_functions(content)
        classes = self._detect_classes(content)
        
        # Calcula complexidade básica
        complexity = self._calculate_basic_complexity(content)
        
        # Cria a análise
        analysis = CodeAnalysis(
            language=self.LANGUAGE_EXTENSIONS.get(file_ext.lower(), 'Unknown'),
            total_lines=total_lines,
            code_lines=code_lines,
            blank_lines=blank_lines,
            max_line_length=max_line_length,
            avg_line_length=avg_line_length,
            complexity=complexity,
            functions=functions,
            classes=classes
        )
        
        # Atualiza as métricas
        analysis.metrics = CodeMetrics(
            total_lines=total_lines,
            blank_lines=blank_lines,
            code_lines=code_lines,
            max_line_length=max_line_length,
            avg_line_length=avg_line_length,
            complexity=complexity
        )
        
        return analysis
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calcula a complexidade ciclomática de um AST Python."""
        complexity = 1  # Complexidade base
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _calculate_basic_complexity(self, content: str) -> float:
        """Calcula uma complexidade básica baseada em estruturas de controle."""
        complexity = 1  # Complexidade base
        
        # Padrões de estruturas de controle
        patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\bdo\b',
            r'\bswitch\b', r'\bcase\b',
            r'\bcatch\b', r'\bfinally\b',
            r'\b&&\b', r'\b\|\|\b'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            complexity += sum(1 for _ in matches)
        
        return complexity
    
    def _detect_functions(self, content: str) -> List[str]:
        """Detecta funções no código usando regex."""
        functions = []
        
        # Padrões comuns de declaração de funções
        patterns = [
            r'def\s+(\w+)\s*\(',  # Python
            r'function\s+(\w+)\s*\(',  # JavaScript
            r'(\w+)\s*:\s*function\s*\(',  # JavaScript
            r'(\w+)\s*=\s*function\s*\(',  # JavaScript
            r'(\w+)\s*=\s*\([^)]*\)\s*=>',  # JavaScript arrow function
            r'public\s+(\w+)\s+(\w+)\s*\(',  # Java
            r'private\s+(\w+)\s+(\w+)\s*\(',  # Java
            r'protected\s+(\w+)\s+(\w+)\s*\(',  # Java
            r'(\w+)\s+(\w+)\s*\(',  # C/C++
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Pega o nome da função do grupo apropriado
                func_name = match.group(2) if len(match.groups()) > 1 else match.group(1)
                if func_name not in functions:
                    functions.append(func_name)
        
        return functions
    
    def _detect_classes(self, content: str) -> List[str]:
        """Detecta classes no código usando regex."""
        classes = []
        
        # Padrões comuns de declaração de classes
        patterns = [
            r'class\s+(\w+)',  # Python
            r'class\s+(\w+)\s*{',  # JavaScript/Java/C++
            r'interface\s+(\w+)',  # Java/TypeScript
            r'struct\s+(\w+)',  # C/C++
            r'enum\s+(\w+)',  # C/C++/Java
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                class_name = match.group(1)
                if class_name not in classes:
                    classes.append(class_name)
        
        return classes 