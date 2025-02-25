"""
Analisador de código com detecção avançada de problemas.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import ast
import re

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

class CodeAnalyzer:
    """
    Analisador de código que detecta problemas e sugere melhorias.
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
    
    def analyze_file(self, file_path: str, content: str) -> List[CodeSmell]:
        """
        Analisa um arquivo e retorna os problemas encontrados.
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo do arquivo
            
        Returns:
            Lista de problemas encontrados
        """
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return [CodeSmell(
                type=CodeSmellType.HIGH_COMPLEXITY,
                file=file_path,
                line=e.lineno or 1,
                message=f"Erro de sintaxe: {str(e)}",
                severity=3,
                suggestion="Corrija o erro de sintaxe no código"
            )]
        
        smells = []
        
        # Análise de métodos
        smells.extend(self._analyze_methods(file_path, tree))
        
        # Análise de classes
        smells.extend(self._analyze_classes(file_path, tree))
        
        # Análise de código duplicado
        smells.extend(self._find_duplicates(file_path, content))
        
        return smells
    
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
                        message="Classe apenas com getters/setters",
                        severity=1,
                        suggestion="Adicione comportamento à classe ou use @dataclass"
                    ))
                
                # Detecta God Class
                if self._is_god_class(node):
                    smells.append(CodeSmell(
                        type=CodeSmellType.GOD_CLASS,
                        file=file_path,
                        line=node.lineno,
                        message="Classe com muitas responsabilidades",
                        severity=3,
                        suggestion="Aplique o princípio de Responsabilidade Única (SRP)"
                    ))
        
        return smells
    
    def _find_duplicates(self, file_path: str, content: str) -> List[CodeSmell]:
        """Detecta código duplicado."""
        smells = []
        lines = content.split('\n')
        
        for i in range(len(lines) - self.config.min_duplicate_lines + 1):
            chunk1 = '\n'.join(lines[i:i + self.config.min_duplicate_lines])
            
            for j in range(i + self.config.min_duplicate_lines, len(lines) - self.config.min_duplicate_lines + 1):
                chunk2 = '\n'.join(lines[j:j + self.config.min_duplicate_lines])
                similarity = self._calculate_similarity(chunk1, chunk2)
                
                if similarity >= self.config.min_similarity:
                    smells.append(CodeSmell(
                        type=CodeSmellType.DUPLICATE_CODE,
                        file=file_path,
                        line=i + 1,
                        message=f"Código duplicado encontrado (similaridade: {similarity:.2f})",
                        severity=2,
                        suggestion="Extraia o código duplicado para um método reutilizável"
                    ))
                    break  # Evita reportar o mesmo trecho múltiplas vezes
        
        return smells
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calcula a complexidade ciclomática de um nó AST."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.ExceptHandler, ast.With, ast.AsyncWith,
                               ast.Assert, ast.BoolOp)):
                complexity += 1
        
        return complexity
    
    def _is_data_class(self, node: ast.ClassDef) -> bool:
        """Verifica se uma classe é apenas uma data class."""
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        getters_setters = 0
        
        for method in methods:
            if method.name.startswith(('get_', 'set_', '__get', '__set')):
                getters_setters += 1
        
        return len(methods) > 0 and getters_setters == len(methods)
    
    def _is_god_class(self, node: ast.ClassDef) -> bool:
        """Verifica se uma classe é uma God Class."""
        methods = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
        attributes = len([n for n in node.body if isinstance(n, ast.AnnAssign)])
        
        return methods > 20 or attributes > 15
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula a similaridade entre dois trechos de texto usando distância de Levenshtein.
        Retorna um valor entre 0 e 1, onde 1 significa textos idênticos.
        """
        if not text1 or not text2:
            return 0.0
        
        # Remove espaços em branco e comentários para comparação
        text1 = self._normalize_code(text1)
        text2 = self._normalize_code(text2)
        
        if not text1 or not text2:
            return 0.0
        
        # Calcula distância de Levenshtein
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        max_len = max(m, n)
        if max_len == 0:
            return 1.0
        
        similarity = 1 - (dp[m][n] / max_len)
        return similarity
    
    def _normalize_code(self, text: str) -> str:
        """Remove espaços em branco e comentários do código."""
        # Remove comentários
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        
        # Remove strings
        text = re.sub(r'["\'].*?["\']', '""', text)
        
        # Remove espaços em branco
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip() 