"""
Testes para o analisador de código.
"""

import pytest
from ..code_analyzer import CodeAnalyzer, AnalysisConfig, CodeSmellType
import hashlib
from django.test import Client
from django.core.cache import cache as redis_cache

def test_analyze_syntax_error():
    """Testa análise de código com erro de sintaxe."""
    analyzer = CodeAnalyzer()
    code = """
    def invalid_syntax:
        print('missing parentheses'
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert len(smells) == 1
    assert smells[0].type == CodeSmellType.HIGH_COMPLEXITY
    assert "sintaxe" in smells[0].message.lower()
    assert smells[0].severity == 3

def test_analyze_long_method():
    """Testa detecção de método longo."""
    analyzer = CodeAnalyzer(AnalysisConfig(max_method_lines=2))
    code = """
    def long_method():
        print(1)
        print(2)
        print(3)
        print(4)
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.LONG_METHOD for s in smells)

def test_analyze_high_complexity():
    """Testa detecção de alta complexidade."""
    analyzer = CodeAnalyzer(AnalysisConfig(max_complexity=1))
    code = """
    def complex_method(x):
        if x > 0:
            if x < 10:
                return 1
            else:
                return 2
        return 0
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.HIGH_COMPLEXITY for s in smells)

def test_analyze_many_parameters():
    """Testa detecção de muitos parâmetros."""
    analyzer = CodeAnalyzer(AnalysisConfig(max_parameters=2))
    code = """
    def many_params(a, b, c, d, e):
        return a + b + c + d + e
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.LONG_PARAMETER_LIST for s in smells)

def test_analyze_large_class():
    """Testa detecção de classe grande."""
    analyzer = CodeAnalyzer(AnalysisConfig(max_class_lines=2))
    code = """
    class LargeClass:
        def method1(self):
            pass
            
        def method2(self):
            pass
            
        def method3(self):
            pass
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.LARGE_CLASS for s in smells)

def test_analyze_data_class():
    """Testa detecção de data class."""
    analyzer = CodeAnalyzer()
    code = """
    class DataClass:
        def get_x(self):
            return self._x
            
        def set_x(self, value):
            self._x = value
            
        def get_y(self):
            return self._y
            
        def set_y(self, value):
            self._y = value
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.DATA_CLASS for s in smells)

def test_analyze_god_class():
    """Testa detecção de god class."""
    analyzer = CodeAnalyzer()
    code = """
    class GodClass:
        def __init__(self):
            self.a = 1
            self.b = 2
            self.c = 3
            self.d = 4
            self.e = 5
            self.f = 6
            self.g = 7
            self.h = 8
            self.i = 9
            self.j = 10
            self.k = 11
            self.l = 12
            self.m = 13
            self.n = 14
            self.o = 15
            self.p = 16
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.GOD_CLASS for s in smells)

def test_analyze_duplicate_code():
    """Testa detecção de código duplicado."""
    analyzer = CodeAnalyzer(AnalysisConfig(min_duplicate_lines=2, min_similarity=0.9))
    code = """
    def method1():
        print("Hello")
        print("World")
        
    def method2():
        print("Hello")
        print("World")
    """
    
    smells = analyzer.analyze_file("test.py", code)
    
    assert any(s.type == CodeSmellType.DUPLICATE_CODE for s in smells)

def test_calculate_similarity():
    """Testa cálculo de similaridade."""
    analyzer = CodeAnalyzer()
    
    text1 = "print('hello')"
    text2 = "print('hello')"
    assert analyzer._calculate_similarity(text1, text2) == 1.0
    
    text1 = "print('hello')"
    text2 = "print('world')"
    assert analyzer._calculate_similarity(text1, text2) < 1.0
    
    text1 = ""
    text2 = ""
    assert analyzer._calculate_similarity(text1, text2) == 1.0
    
    text1 = "print('hello')"
    text2 = ""
    assert analyzer._calculate_similarity(text1, text2) == 0.0

def test_normalize_code():
    """Testa normalização de código."""
    analyzer = CodeAnalyzer()
    
    code = """
    # Comentário
    def test():
        print("string")  # outro comentário
        x = 1  # número
    """
    
    normalized = analyzer._normalize_code(code)
    
    assert "#" not in normalized
    assert "string" not in normalized
    assert "Comentário" not in normalized
    assert "outro comentário" not in normalized

def test_cache_hit():
    path = "tests/sample_project"
    # Primeira execução (miss)
    task_1 = analyze_code_task.delay(path)
    result_1 = task_1.get(timeout=60)
    assert not result_1.get("cached", False), "Primeira execução deveria não ter cache"

    # Segunda execução (hit)
    task_2 = analyze_code_task.delay(path)
    result_2 = task_2.get(timeout=60)
    assert result_2.get("cached", False), "Segunda execução deveria usar cache"

def test_cache_invalidation():
    path = "tests/sample_project"
    analyze_code_task.delay(path).get(timeout=60)
    hash_val = hashlib.sha256(path.encode()).hexdigest()
    cache_key = f"analysis:{hash_val}"
    response = client.delete(f"/invalidate-cache/{cache_key}")
    assert response.json()["status"] == "deleted"
    assert redis_cache.get(cache_key) is None 