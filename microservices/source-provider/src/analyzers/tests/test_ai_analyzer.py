"""
Testes para o analisador baseado em IA.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..ai_analyzer import AIAnalyzer, AIAnalysisConfig, CodeSuggestion
from ..ai_providers import AIProvider

class MockProvider(AIProvider):
    """Provedor mock para testes."""
    
    def __init__(self):
        super().__init__()
        self.complete = AsyncMock()

@pytest.fixture
def mock_provider():
    """Fixture que fornece um provedor mock."""
    return MockProvider()

@pytest.fixture
def config(mock_provider):
    """Fixture que fornece uma configuração de teste."""
    return AIAnalysisConfig(
        provider=mock_provider,
        temperature=0.5,
        max_tokens=100,
        chunk_size=50
    )

@pytest.fixture
def analyzer(config):
    """Fixture que fornece um analisador configurado."""
    return AIAnalyzer(config)

@pytest.mark.asyncio
async def test_start_stop(analyzer, mock_provider):
    """Testa inicialização e finalização do analisador."""
    await analyzer.start()
    mock_provider.start.assert_called_once()
    
    await analyzer.stop()
    mock_provider.stop.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_code(analyzer, mock_provider):
    """Testa análise de código."""
    code = """
    def test():
        print("hello")
    """
    
    mock_provider.complete.return_value = json.dumps({
        "suggestions": [{
            "line": 1,
            "original_code": 'print("hello")',
            "suggested_code": 'logger.info("hello")',
            "explanation": "Use logging instead of print",
            "confidence": 0.9
        }]
    })
    
    suggestions = await analyzer.analyze_code("test.py", code)
    
    assert len(suggestions) == 1
    assert isinstance(suggestions[0], CodeSuggestion)
    assert suggestions[0].file == "test.py"
    assert suggestions[0].line == 1
    assert "print" in suggestions[0].original_code
    assert "logger" in suggestions[0].suggested_code
    assert suggestions[0].confidence == 0.9

@pytest.mark.asyncio
async def test_suggest_refactoring(analyzer, mock_provider):
    """Testa sugestão de refatoração."""
    code = """
    def old_code():
        pass
    """
    
    mock_provider.complete.return_value = json.dumps({
        "refactored_code": "def new_code():\n    return None",
        "explanation": "Added return statement",
        "benefits": ["Explicit return", "Better type hints"]
    })
    
    refactored = await analyzer.suggest_refactoring(code)
    
    assert "new_code" in refactored
    assert "return None" in refactored

@pytest.mark.asyncio
async def test_explain_code(analyzer, mock_provider):
    """Testa explicação de código."""
    code = """
    def test():
        pass
    """
    
    mock_provider.complete.return_value = "This is a test function that does nothing."
    
    explanation = await analyzer.explain_code(code)
    
    assert "test function" in explanation

@pytest.mark.asyncio
async def test_suggest_tests(analyzer, mock_provider):
    """Testa sugestão de testes."""
    code = """
    def add(a, b):
        return a + b
    """
    
    mock_provider.complete.return_value = """
    def test_add():
        assert add(1, 2) == 3
    """
    
    tests = await analyzer.suggest_tests(code)
    
    assert "test_add" in tests
    assert "assert" in tests

@pytest.mark.asyncio
async def test_provider_error(analyzer, mock_provider):
    """Testa tratamento de erro do provedor."""
    mock_provider.complete.side_effect = RuntimeError("API Error")
    
    suggestions = await analyzer.analyze_code("test.py", "test")
    assert len(suggestions) == 0

def test_split_code(analyzer):
    """Testa divisão do código em chunks."""
    code = "a" * 100 + "\n" + "b" * 100
    chunks = analyzer._split_code(code)
    
    assert len(chunks) == 4  # 2 linhas divididas em 4 chunks de 50 caracteres
    assert all(len(chunk) <= analyzer.config.chunk_size for chunk in chunks)

def test_create_prompts(analyzer):
    """Testa criação de prompts."""
    code = "test code"
    
    analysis_prompt = analyzer._create_analysis_prompt(code)
    assert "test code" in analysis_prompt
    assert "sugestões específicas" in analysis_prompt
    
    refactoring_prompt = analyzer._create_refactoring_prompt(code)
    assert "test code" in refactoring_prompt
    assert "refatoração" in refactoring_prompt
    
    explanation_prompt = analyzer._create_explanation_prompt(code)
    assert "test code" in explanation_prompt
    assert "Explique" in explanation_prompt
    
    test_prompt = analyzer._create_test_prompt(code)
    assert "test code" in test_prompt
    assert "testes unitários" in test_prompt 