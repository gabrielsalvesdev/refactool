"""
Analisador baseado em IA para sugestões inteligentes.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import structlog

from .ai_providers import AIProvider, DeepSeekProvider, OllamaProvider

logger = structlog.get_logger()

@dataclass
class AIAnalysisConfig:
    """Configuração para análise com IA."""
    provider: Union[DeepSeekProvider, OllamaProvider]
    temperature: float = 0.3
    max_tokens: int = 1000
    chunk_size: int = 1000

@dataclass
class CodeSuggestion:
    """Sugestão de melhoria gerada pela IA."""
    file: str
    line: int
    original_code: str
    suggested_code: str
    explanation: str
    confidence: float

class AIAnalyzer:
    """
    Analisador baseado em IA que fornece sugestões inteligentes.
    """
    
    def __init__(self, config: AIAnalysisConfig):
        self.config = config
    
    async def start(self):
        """Inicializa o analisador."""
        await self.config.provider.start()
    
    async def stop(self):
        """Finaliza o analisador."""
        await self.config.provider.stop()
    
    async def analyze_code(self, file_path: str, content: str) -> List[CodeSuggestion]:
        """
        Analisa código usando IA e retorna sugestões.
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo do arquivo
            
        Returns:
            Lista de sugestões de melhoria
        """
        # Divide o código em chunks para análise
        chunks = self._split_code(content)
        suggestions = []
        
        for i, chunk in enumerate(chunks):
            try:
                chunk_suggestions = await self._analyze_chunk(file_path, chunk, i * self.config.chunk_size)
                suggestions.extend(chunk_suggestions)
            except Exception as e:
                logger.error(
                    "ai_analyzer.chunk_analysis_failed",
                    file=file_path,
                    chunk=i,
                    error=str(e)
                )
        
        return suggestions
    
    async def suggest_refactoring(self, code: str) -> str:
        """
        Sugere refatoração para um trecho de código.
        
        Args:
            code: Código a ser refatorado
            
        Returns:
            Sugestão de refatoração
        """
        prompt = self._create_refactoring_prompt(code)
        response = await self.config.provider.complete(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return self._parse_refactoring_response(response)
    
    async def explain_code(self, code: str) -> str:
        """
        Gera uma explicação detalhada do código.
        
        Args:
            code: Código a ser explicado
            
        Returns:
            Explicação do código
        """
        prompt = self._create_explanation_prompt(code)
        return await self.config.provider.complete(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    async def suggest_tests(self, code: str) -> str:
        """
        Sugere testes unitários para o código.
        
        Args:
            code: Código para gerar testes
            
        Returns:
            Sugestão de testes unitários
        """
        prompt = self._create_test_prompt(code)
        return await self.config.provider.complete(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    async def _analyze_chunk(self, file_path: str, code: str, start_line: int) -> List[CodeSuggestion]:
        """Analisa um trecho de código usando IA."""
        prompt = self._create_analysis_prompt(code)
        
        try:
            response = await self.config.provider.complete(
                prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return self._parse_analysis_response(file_path, code, response, start_line)
        except Exception as e:
            logger.error(
                "ai_analyzer.chunk_analysis_error",
                file=file_path,
                start_line=start_line,
                error=str(e)
            )
            return []
    
    def _split_code(self, content: str) -> List[str]:
        """Divide o código em chunks para análise."""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > self.config.chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _create_analysis_prompt(self, code: str) -> str:
        """Cria o prompt para análise de código."""
        return f"""
        Analise o seguinte código Python e sugira melhorias:
        
        ```python
        {code}
        ```
        
        Por favor, forneça sugestões específicas para:
        1. Melhorias de design e arquitetura
        2. Otimizações de performance
        3. Melhorias de legibilidade
        4. Possíveis bugs ou problemas de segurança
        
        Formate a resposta como JSON com os campos:
        - suggestions: lista de sugestões, cada uma com:
          - line: número da linha
          - original_code: código original
          - suggested_code: código sugerido
          - explanation: explicação da melhoria
          - confidence: nível de confiança (0.0 a 1.0)
        """
    
    def _create_refactoring_prompt(self, code: str) -> str:
        """Cria o prompt para sugestão de refatoração."""
        return f"""
        Sugira uma refatoração para o seguinte código Python:
        
        ```python
        {code}
        ```
        
        Por favor, forneça:
        1. O código refatorado
        2. Explicação das mudanças
        3. Benefícios da refatoração
        
        Formate a resposta como JSON com os campos:
        - refactored_code: código refatorado
        - explanation: explicação das mudanças
        - benefits: lista de benefícios
        """
    
    def _create_explanation_prompt(self, code: str) -> str:
        """Cria o prompt para explicação de código."""
        return f"""
        Explique o seguinte código Python em detalhes:
        
        ```python
        {code}
        ```
        
        Por favor, inclua:
        1. Visão geral do funcionamento
        2. Detalhes de implementação importantes
        3. Padrões de design utilizados
        4. Possíveis casos de uso
        
        Formate a resposta como texto estruturado com seções claras.
        """
    
    def _create_test_prompt(self, code: str) -> str:
        """Cria o prompt para sugestão de testes."""
        return f"""
        Sugira testes unitários para o seguinte código Python:
        
        ```python
        {code}
        ```
        
        Por favor, inclua:
        1. Casos de teste importantes
        2. Mocks necessários
        3. Cenários de erro
        4. Cobertura de código
        
        Formate a resposta como código Python com testes usando pytest.
        """
    
    def _parse_analysis_response(
        self,
        file_path: str,
        original_code: str,
        response: str,
        start_line: int
    ) -> List[CodeSuggestion]:
        """Processa a resposta da API e retorna sugestões estruturadas."""
        try:
            data = json.loads(response)
            suggestions = []
            
            for suggestion in data.get('suggestions', []):
                suggestions.append(CodeSuggestion(
                    file=file_path,
                    line=start_line + suggestion.get('line', 1),
                    original_code=suggestion.get('original_code', ''),
                    suggested_code=suggestion.get('suggested_code', ''),
                    explanation=suggestion.get('explanation', ''),
                    confidence=suggestion.get('confidence', 0.0)
                ))
            
            return suggestions
        except json.JSONDecodeError as e:
            logger.error(
                "ai_analyzer.response_parse_failed",
                file=file_path,
                error=str(e),
                response=response
            )
            return []
    
    def _parse_refactoring_response(self, response: str) -> str:
        """Processa a resposta de refatoração."""
        try:
            data = json.loads(response)
            return data.get('refactored_code', '')
        except json.JSONDecodeError as e:
            logger.error(
                "ai_analyzer.response_parse_failed",
                error=str(e),
                response=response
            )
            raise 