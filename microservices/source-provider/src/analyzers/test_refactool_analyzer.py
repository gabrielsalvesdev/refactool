"""
Testes para o analisador da Refactool.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil
from pathlib import Path

from .refactool_analyzer import RefactoolAnalyzer, ProjectContext
from .code_analyzer import CodeSmell, SmellType
from .ai_analyzer import CodeSuggestion

@pytest.fixture
def temp_project_dir():
    """Cria uma estrutura temporária de projeto para testes."""
    temp_dir = tempfile.mkdtemp()
    
    # Cria estrutura básica do projeto
    os.makedirs(os.path.join(temp_dir, "src"))
    os.makedirs(os.path.join(temp_dir, "tests"))
    os.makedirs(os.path.join(temp_dir, "docs"))
    
    # Cria alguns arquivos de exemplo
    files = {
        "src/main.py": "def main():\n    print('Hello')\n",
        "src/helper.js": "function helper() { return true; }",
        "tests/test_main.py": "def test_main(): pass",
        "docs/README.md": "# Projeto Teste",
        "requirements.txt": "pytest>=7.0.0\nrequests>=2.0.0",
        "package.json": '{"dependencies": {"express": "^4.0.0"}}',
        ".env": "API_KEY=test",
    }
    
    for path, content in files.items():
        full_path = os.path.join(temp_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
    
    yield temp_dir
    
    # Limpa diretório temporário
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_analyzers():
    """Mock para os analisadores."""
    with patch("analyzers.refactool_analyzer.CodeAnalyzer") as mock_code_analyzer, \
         patch("analyzers.refactool_analyzer.AIAnalyzer") as mock_ai_analyzer:
        
        # Configura mock do analisador de código
        mock_code_analyzer_instance = MagicMock()
        mock_code_analyzer_instance.analyze_file.return_value = [
            CodeSmell(
                type=SmellType.COMPLEXITY,
                message="Complexidade muito alta",
                file="test.py",
                line=1
            )
        ]
        mock_code_analyzer.return_value = mock_code_analyzer_instance
        
        # Configura mock do analisador de IA
        mock_ai_analyzer_instance = AsyncMock()
        mock_ai_analyzer_instance.analyze_code.return_value = [
            CodeSuggestion(
                explanation="Sugestão de melhoria",
                file="test.py",
                line=1,
                code="# código sugerido"
            )
        ]
        mock_ai_analyzer.return_value = mock_ai_analyzer_instance
        
        yield mock_code_analyzer_instance, mock_ai_analyzer_instance

@pytest.mark.asyncio
async def test_project_discovery(temp_project_dir, mock_analyzers):
    """Testa a descoberta da estrutura do projeto."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project(temp_project_dir)
    
    # Verifica se as linguagens foram detectadas
    assert "Python" in analyzer.context.languages
    assert "JavaScript" in analyzer.context.languages
    
    # Verifica se os arquivos importantes foram categorizados
    assert any("requirements.txt" in f for f in analyzer.context.build_files)
    assert any("package.json" in f for f in analyzer.context.build_files)
    assert any(".env" in f for f in analyzer.context.config_files)
    assert any("README.md" in f for f in analyzer.context.documentation)

@pytest.mark.asyncio
async def test_dependency_analysis(temp_project_dir, mock_analyzers):
    """Testa a análise de dependências."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project(temp_project_dir)
    
    # Verifica dependências Python
    assert "Python" in analyzer.context.dependencies
    python_deps = analyzer.context.dependencies["Python"]
    assert "pytest>=7.0.0" in python_deps
    assert "requests>=2.0.0" in python_deps
    
    # Verifica dependências JavaScript
    assert "JavaScript" in analyzer.context.dependencies
    js_deps = analyzer.context.dependencies["JavaScript"]
    assert "express" in js_deps

@pytest.mark.asyncio
async def test_code_analysis(temp_project_dir, mock_analyzers):
    """Testa a análise de código."""
    mock_code_analyzer, mock_ai_analyzer = mock_analyzers
    analyzer = RefactoolAnalyzer()
    
    await analyzer.analyze_project(temp_project_dir)
    
    # Verifica se o analisador estático foi chamado para arquivos Python
    python_files = [f for f in analyzer._analyzed_files if f.endswith('.py')]
    assert len(python_files) > 0
    for file in python_files:
        mock_code_analyzer.analyze_file.assert_any_call(file, pytest.ANY)
    
    # Verifica se o analisador de IA foi chamado para todos os arquivos
    for file in analyzer._analyzed_files:
        await mock_ai_analyzer.analyze_code.assert_any_call(file, pytest.ANY)

@pytest.mark.asyncio
async def test_documentation_analysis(temp_project_dir, mock_analyzers):
    """Testa a análise de documentação."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project(temp_project_dir)
    
    # Verifica se a documentação foi carregada
    assert any("README.md" in f for f in analyzer.context.documentation.keys())
    
    # Verifica o conteúdo da documentação
    readme_path = next(f for f in analyzer.context.documentation.keys() if "README.md" in f)
    assert analyzer.context.documentation[readme_path] == "# Projeto Teste"

@pytest.mark.asyncio
async def test_skip_patterns(temp_project_dir):
    """Testa os padrões de arquivos e diretórios ignorados."""
    # Cria alguns arquivos que devem ser ignorados
    skip_files = [
        "__pycache__/cache.pyc",
        ".git/HEAD",
        "venv/lib/python3.8/site-packages/pytest.py",
        "node_modules/express/index.js"
    ]
    
    for file_path in skip_files:
        full_path = os.path.join(temp_project_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        Path(full_path).touch()
    
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project(temp_project_dir)
    
    # Verifica se os arquivos foram ignorados
    analyzed_files = {os.path.relpath(f, temp_project_dir) for f in analyzer._analyzed_files}
    for skip_file in skip_files:
        assert skip_file not in analyzed_files

@pytest.mark.asyncio
async def test_report_generation(temp_project_dir, capsys):
    """Testa a geração do relatório."""
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project(temp_project_dir)
    
    # Captura a saída do relatório
    captured = capsys.readouterr()
    report = captured.out
    
    # Verifica seções importantes do relatório
    assert "=== Relatório de Análise da Refactool ===" in report
    assert "=== Visão Geral do Projeto ===" in report
    assert "=== Linguagens Utilizadas ===" in report
    assert "=== Dependências ===" in report
    assert "=== Arquivos Importantes ===" in report
    assert "=== Problemas e Sugestões ===" in report

@pytest.mark.asyncio
async def test_error_handling(temp_project_dir, mock_analyzers):
    """Testa o tratamento de erros durante a análise."""
    mock_code_analyzer, mock_ai_analyzer = mock_analyzers
    
    # Simula erro no analisador de IA
    mock_ai_analyzer.analyze_code.side_effect = Exception("Erro de análise")
    
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project(temp_project_dir)
    
    # Verifica se a análise continua mesmo com erro
    assert len(analyzer._analyzed_files) > 0
    assert len(analyzer.context.languages) > 0

@pytest.mark.asyncio
async def test_project_context():
    """Testa a inicialização do contexto do projeto."""
    context = ProjectContext()
    
    # Verifica se todos os atributos foram inicializados corretamente
    assert isinstance(context.languages, dict)
    assert isinstance(context.dependencies, dict)
    assert isinstance(context.frameworks, dict)
    assert isinstance(context.file_types, dict)
    assert isinstance(context.architecture, dict)
    assert isinstance(context.test_coverage, dict)
    assert isinstance(context.documentation, dict)
    assert isinstance(context.entry_points, list)
    assert isinstance(context.build_files, list)
    assert isinstance(context.config_files, list)
    assert isinstance(context.api_definitions, list)
    assert isinstance(context.database_schemas, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 