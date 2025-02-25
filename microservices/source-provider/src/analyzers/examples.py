"""
Exemplos de uso dos analisadores de código.
"""

import asyncio
import os
from typing import List

from .code_analyzer import CodeAnalyzer, AnalysisConfig, CodeSmell
from .ai_analyzer import AIAnalyzer, AIAnalysisConfig
from .ai_providers import DeepSeekProvider, OllamaProvider

async def analyze_file_with_deepseek(file_path: str) -> None:
    """
    Analisa um arquivo usando o analisador estático e DeepSeek.
    
    Args:
        file_path: Caminho do arquivo a ser analisado
    """
    # Configuração do analisador estático
    code_analyzer = CodeAnalyzer(AnalysisConfig(
        max_method_lines=30,
        max_complexity=10,
        max_class_lines=300,
        max_parameters=5,
        min_duplicate_lines=6,
        min_similarity=0.8
    ))
    
    # Configuração do analisador de IA com DeepSeek
    deepseek = DeepSeekProvider(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-coder-33b-instruct"
    )
    
    ai_analyzer = AIAnalyzer(AIAnalysisConfig(
        provider=deepseek,
        temperature=0.3,
        max_tokens=2000
    ))
    
    try:
        # Lê o arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Análise estática
        print("\n=== Análise Estática ===")
        code_smells = code_analyzer.analyze_file(file_path, content)
        print_code_smells(code_smells)
        
        # Análise com IA
        print("\n=== Análise com DeepSeek ===")
        await ai_analyzer.start()
        
        print("\nAnalisando código...")
        suggestions = await ai_analyzer.analyze_code(file_path, content)
        for suggestion in suggestions:
            print(f"\nLinha {suggestion.line}:")
            print(f"Código original: {suggestion.original_code}")
            print(f"Sugestão: {suggestion.suggested_code}")
            print(f"Explicação: {suggestion.explanation}")
            print(f"Confiança: {suggestion.confidence:.2f}")
        
        print("\nGerando refatoração...")
        refactored = await ai_analyzer.suggest_refactoring(content)
        print("\nCódigo refatorado:")
        print(refactored)
        
        print("\nGerando explicação...")
        explanation = await ai_analyzer.explain_code(content)
        print("\nExplicação do código:")
        print(explanation)
        
        print("\nGerando testes...")
        tests = await ai_analyzer.suggest_tests(content)
        print("\nTestes sugeridos:")
        print(tests)
        
        await ai_analyzer.stop()
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        await ai_analyzer.stop()
        raise

async def analyze_file_with_ollama(file_path: str) -> None:
    """
    Analisa um arquivo usando o analisador estático e Ollama local.
    
    Args:
        file_path: Caminho do arquivo a ser analisado
    """
    # Configuração do analisador estático
    code_analyzer = CodeAnalyzer(AnalysisConfig(
        max_method_lines=30,
        max_complexity=10,
        max_class_lines=300,
        max_parameters=5,
        min_duplicate_lines=6,
        min_similarity=0.8
    ))
    
    # Configuração do analisador de IA com Ollama
    ollama = OllamaProvider(
        model="codellama"  # ou outro modelo instalado localmente
    )
    
    ai_analyzer = AIAnalyzer(AIAnalysisConfig(
        provider=ollama,
        temperature=0.3,
        max_tokens=2000
    ))
    
    try:
        # Lê o arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Análise estática
        print("\n=== Análise Estática ===")
        code_smells = code_analyzer.analyze_file(file_path, content)
        print_code_smells(code_smells)
        
        # Análise com IA
        print("\n=== Análise com Ollama ===")
        await ai_analyzer.start()
        
        print("\nAnalisando código...")
        suggestions = await ai_analyzer.analyze_code(file_path, content)
        for suggestion in suggestions:
            print(f"\nLinha {suggestion.line}:")
            print(f"Código original: {suggestion.original_code}")
            print(f"Sugestão: {suggestion.suggested_code}")
            print(f"Explicação: {suggestion.explanation}")
            print(f"Confiança: {suggestion.confidence:.2f}")
        
        print("\nGerando refatoração...")
        refactored = await ai_analyzer.suggest_refactoring(content)
        print("\nCódigo refatorado:")
        print(refactored)
        
        print("\nGerando explicação...")
        explanation = await ai_analyzer.explain_code(content)
        print("\nExplicação do código:")
        print(explanation)
        
        print("\nGerando testes...")
        tests = await ai_analyzer.suggest_tests(content)
        print("\nTestes sugeridos:")
        print(tests)
        
        await ai_analyzer.stop()
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        await ai_analyzer.stop()
        raise

def print_code_smells(smells: List[CodeSmell]) -> None:
    """Imprime os problemas encontrados no código."""
    if not smells:
        print("Nenhum problema encontrado!")
        return
    
    for smell in smells:
        print(f"\nTipo: {smell.type.value}")
        print(f"Arquivo: {smell.file}")
        print(f"Linha: {smell.line}")
        print(f"Mensagem: {smell.message}")
        print(f"Severidade: {smell.severity}")
        print(f"Sugestão: {smell.suggestion}")

async def main():
    """Função principal com exemplos de uso."""
    # Exemplo com arquivo de teste
    test_code = """
class ExampleClass:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3
    
    def long_method(self, a, b, c, d, e):
        result = 0
        if a > 0:
            if b > 0:
                if c > 0:
                    result = (a + b + c) * (d + e)
                else:
                    result = (a + b) * (d + e)
            else:
                result = a * (d + e)
        return result
    
    def duplicate_code_1(self):
        print("This is some duplicate code")
        print("That will be detected")
        print("By the analyzer")
    
    def duplicate_code_2(self):
        print("This is some duplicate code")
        print("That will be detected")
        print("By the analyzer")
"""
    
    # Salva o código em um arquivo temporário
    test_file = "test_example.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    try:
        # Análise com DeepSeek (se a chave API estiver configurada)
        if os.getenv("DEEPSEEK_API_KEY"):
            print("\n=== Análise com DeepSeek ===")
            await analyze_file_with_deepseek(test_file)
        
        # Análise com Ollama
        print("\n=== Análise com Ollama ===")
        await analyze_file_with_ollama(test_file)
    
    finally:
        # Remove o arquivo temporário
        os.remove(test_file)

if __name__ == "__main__":
    asyncio.run(main()) 