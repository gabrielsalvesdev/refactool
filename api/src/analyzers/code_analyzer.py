"""
Analisador estático de código.
"""

from dataclasses import dataclass
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
    """Resultado da análise de código."""
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    functions: List[str] = None
    classes: List[str] = None
    metrics: CodeMetrics = None
    
    def __post_init__(self):
        if self.functions is None:
            self.functions = []
        if self.classes is None:
            self.classes = []
        if self.metrics is None:
            self.metrics = CodeMetrics()

class CodeAnalyzer:
    """Analisador estático de código."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
    
    def analyze_file(self, file_path: str, content: str) -> List[CodeSmell]:
        """
        Analisa um arquivo de código.
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo do arquivo
            
        Returns:
            Lista de problemas encontrados
        """
        try:
            smells = []
            
            # Análise de código Python
            tree = ast.parse(content)
            
            # Análise de métodos
            smells.extend(self._analyze_methods(file_path, tree))
            
            # Análise de classes
            smells.extend(self._analyze_classes(file_path, tree))
            
            # Análise de código duplicado
            smells.extend(self._find_duplicates(file_path, content))
            
            return smells
            
        except Exception as e:
            logger.error(
                "code_analyzer.analysis_failed",
                error=str(e),
                error_type=type(e).__name__,
                file=file_path
            )
            return []
    
    def _analyze_methods(self, file_path: str, tree: ast.AST) -> List[CodeSmell]:
        """Analisa métodos buscando problemas comuns."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Verifica tamanho do método
                method_lines = node.end_lineno - node.lineno
                if method_lines > self.config.max_method_lines:
                    smells.append(CodeSmell(
                        type=CodeSmellType.LONG_METHOD,
                        file=file_path,
                        line=node.lineno,
                        message=f"Método muito longo ({method_lines} linhas)",
                        severity=2,
                        suggestion="Divida o método em funções menores e mais específicas"
                    ))
                
                # Verifica número de parâmetros
                params = len(node.args.args)
                if params > self.config.max_parameters:
                    smells.append(CodeSmell(
                        type=CodeSmellType.LONG_PARAMETER_LIST,
                        file=file_path,
                        line=node.lineno,
                        message=f"Método com muitos parâmetros ({params})",
                        severity=1,
                        suggestion="Agrupe parâmetros relacionados em uma classe ou use padrão Builder"
                    ))
                
                # Análise de complexidade ciclomática
                complexity = self._calculate_complexity(node)
                if complexity > self.config.max_complexity:
                    smells.append(CodeSmell(
                        type=CodeSmellType.HIGH_COMPLEXITY,
                        file=file_path,
                        line=node.lineno,
                        message=f"Complexidade muito alta ({complexity})",
                        severity=3,
                        suggestion="Simplifique o método dividindo em partes menores"
                    ))
        
        return smells
    
    def _analyze_classes(self, file_path: str, tree: ast.AST) -> List[CodeSmell]:
        """Analisa classes buscando problemas de design."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Verifica tamanho da classe
                class_lines = node.end_lineno - node.lineno
                if class_lines > self.config.max_class_lines:
                    smells.append(CodeSmell(
                        type=CodeSmellType.LARGE_CLASS,
                        file=file_path,
                        line=node.lineno,
                        message=f"Classe muito grande ({class_lines} linhas)",
                        severity=2,
                        suggestion="Divida a classe em classes menores com responsabilidades específicas"
                    ))
                
                # Detecta Data Class
                if self._is_data_class(node):
                    smells.append(CodeSmell(
                        type=CodeSmellType.DATA_CLASS,
                        file=file_path,
                        line=node.lineno,
                        message="Classe apenas com atributos e getters/setters",
                        severity=1,
                        suggestion="Adicione comportamento à classe ou considere usar @dataclass"
                    ))
                
                # Detecta God Class
                if self._is_god_class(node):
                    smells.append(CodeSmell(
                        type=CodeSmellType.GOD_CLASS,
                        file=file_path,
                        line=node.lineno,
                        message="Classe com muitas responsabilidades",
                        severity=3,
                        suggestion="Divida a classe em classes menores com responsabilidades únicas"
                    ))
        
        return smells
    
    def _find_duplicates(self, file_path: str, content: str) -> List[CodeSmell]:
        """Detecta código duplicado."""
        smells = []
        lines = content.split('\n')
        
        for i in range(len(lines)):
            for j in range(i + self.config.min_duplicate_lines, len(lines)):
                block1 = '\n'.join(lines[i:i + self.config.min_duplicate_lines])
                block2 = '\n'.join(lines[j:j + self.config.min_duplicate_lines])
                
                if self._calculate_similarity(block1, block2) >= self.config.min_similarity:
                    smells.append(CodeSmell(
                        type=CodeSmellType.DUPLICATE_CODE,
                        file=file_path,
                        line=i + 1,
                        message=f"Código duplicado (linhas {i+1}-{i+self.config.min_duplicate_lines})",
                        severity=2,
                        suggestion="Extraia o código duplicado para um método reutilizável"
                    ))
                    break
        
        return smells
    
    def _calculate_complexity(self, node: ast.AST) -> float:
        """Calcula a complexidade do código."""
        complexity = 0
        
        for n in ast.walk(node):
            # Incrementa para cada estrutura de controle
            if isinstance(n, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            # Incrementa para cada operador booleano
            elif isinstance(n, ast.BoolOp):
                complexity += len(n.values) - 1
        
        return complexity
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula a similaridade entre dois textos."""
        text1 = self._normalize_code(text1)
        text2 = self._normalize_code(text2)
        
        if not text1 or not text2:
            return 0.0
        
        # Usa distância de Levenshtein normalizada
        distance = self._levenshtein_distance(text1, text2)
        max_length = max(len(text1), len(text2))
        
        if max_length == 0:
            return 1.0
            
        return 1.0 - (distance / max_length)
    
    def _normalize_code(self, text: str) -> str:
        """Normaliza o código para comparação."""
        # Remove espaços em branco e comentários
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        return ' '.join(lines)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calcula a distância de Levenshtein entre duas strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _is_data_class(self, node: ast.ClassDef) -> bool:
        """Verifica se uma classe é uma Data Class."""
        has_methods = False
        for n in node.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not n.name.startswith('__'):
                    has_methods = True
                    break
        return not has_methods
    
    def _is_god_class(self, node: ast.ClassDef) -> bool:
        """Verifica se uma classe é uma God Class."""
        method_count = 0
        attribute_count = 0
        
        for n in node.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_count += 1
            elif isinstance(n, ast.Assign):
                attribute_count += len(n.targets)
        
        return method_count > 20 or attribute_count > 15 