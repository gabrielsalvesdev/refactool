"""
Testes para o analisador baseado em IA.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import aiohttp

from ..ai_analyzer import AIAnalyzer, AIAnalysisConfig, CodeSuggestion

@pytest.fixture
def config():
    """Fixture que fornece uma configuração de teste."""
    return AIAnalysisConfig(
        api_key="test-key",
        model="test-model",
        temperature=0.5,
        max_tokens=100,
        chunk_size=50
    )

@pytest.fixture
def analyzer(config):
    """Fixture que fornece um analisador configurado."""
    return AIAnalyzer(config)

@pytest.mark.asyncio
async def test_start_stop(analyzer):
    """Testa inicialização e finalização do analisador."""
    assert analyzer._session is None
    
    await analyzer.start()
    assert isinstance(analyzer._session, aiohttp.ClientSession)
    
    await analyzer.stop()
    assert analyzer._session is None

@pytest.mark.asyncio
async def test_analyze_code(analyzer):
    """Testa análise de código."""
    code = """
    def test():
        print("hello")
    """
    
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "suggestions": [{
                        "line": 1,
                        "original_code": 'print("hello")',
                        "suggested_code": 'logger.info("hello")',
                        "explanation": "Use logging instead of print",
                        "confidence": 0.9
                    }]
                })
            }
        }]
    }
    
    mock_session = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value.status = 200
    mock_session.post.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await analyzer.start()
        suggestions = await analyzer.analyze_code("test.py", code)
        
        assert len(suggestions) == 1
        assert isinstance(suggestions[0], CodeSuggestion)
        assert suggestions[0].file == "test.py"
        assert suggestions[0].line == 1
        assert "print" in suggestions[0].original_code
        assert "logger" in suggestions[0].suggested_code
        assert suggestions[0].confidence == 0.9

@pytest.mark.asyncio
async def test_suggest_refactoring(analyzer):
    """Testa sugestão de refatoração."""
    code = """
    def old_code():
        pass
    """
    
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "refactored_code": "def new_code():\n    return None",
                    "explanation": "Added return statement",
                    "benefits": ["Explicit return", "Better type hints"]
                })
            }
        }]
    }
    
    mock_session = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value.status = 200
    mock_session.post.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await analyzer.start()
        refactored = await analyzer.suggest_refactoring(code)
        
        assert "new_code" in refactored
        assert "return None" in refactored

@pytest.mark.asyncio
async def test_explain_code(analyzer):
    """Testa explicação de código."""
    code = """
    def test():
        pass
    """
    
    mock_response = {
        "choices": [{
            "message": {
                "content": "This is a test function that does nothing."
            }
        }]
    }
    
    mock_session = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value.status = 200
    mock_session.post.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await analyzer.start()
        explanation = await analyzer.explain_code(code)
        
        assert "test function" in explanation

@pytest.mark.asyncio
async def test_suggest_tests(analyzer):
    """Testa sugestão de testes."""
    code = """
    def add(a, b):
        return a + b
    """
    
    mock_response = {
        "choices": [{
            "message": {
                "content": """
                def test_add():
                    assert add(1, 2) == 3
                """
            }
        }]
    }
    
    mock_session = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value.status = 200
    mock_session.post.return_value.__aenter__.return_value.json = AsyncMock(
        return_value=mock_response
    )
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await analyzer.start()
        tests = await analyzer.suggest_tests(code)
        
        assert "test_add" in tests
        assert "assert" in tests

@pytest.mark.asyncio
async def test_api_error(analyzer):
    """Testa tratamento de erro da API."""
    mock_session = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value.status = 400
    mock_session.post.return_value.__aenter__.return_value.text = AsyncMock(
        return_value="API Error"
    )
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await analyzer.start()
        with pytest.raises(RuntimeError, match="OpenAI API error"):
            await analyzer.explain_code("test")

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