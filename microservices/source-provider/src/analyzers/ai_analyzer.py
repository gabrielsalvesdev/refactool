"""
Analisador baseado em IA para sugestões inteligentes.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import structlog

from .ai_providers import AIProvider, OpenAIProvider, OllamaProvider

logger = structlog.get_logger()

@dataclass
class AIAnalysisConfig:
    """Configuração para análise com IA."""
    provider: Union[OpenAIProvider, OllamaProvider]
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
    """Analisador baseado em IA que fornece sugestões inteligentes."""
    
    def __init__(self, config: AIAnalysisConfig):
        self.config = config
    
    async def start(self):
        """Inicializa o analisador."""
        await self.config.provider.start()
    
    async def stop(self):
        """Finaliza o analisador."""
        await self.config.provider.stop()
    
    async def analyze_code(self, file_path: str, content: str) -> List[CodeSuggestion]:
        """Analisa código usando IA e retorna sugestões."""
        try:
            prompt = self._create_analysis_prompt(content)
            response = await self.config.provider.complete(
                prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return self._parse_analysis_response(file_path, content, response, 1)
        except Exception as e:
            logger.error(f"Erro na análise AI: {str(e)}")
            return None
    
    def _create_analysis_prompt(self, code: str) -> str:
        """Cria o prompt para análise de código."""
        return f"""Analise este código Python e sugira melhorias em português:

{code}

Forneça sugestões no seguinte formato:

Linha X:
Original: <código original>
Sugestão: <código sugerido>
Explicação: <explicação da melhoria>

Exemplo:
Linha 10:
Original: def func():
Sugestão: def process_data():
Explicação: Nome da função mais descritivo para melhor legibilidade"""
    
    def _parse_analysis_response(
        self,
        file_path: str,
        original_code: str,
        response: str,
        start_line: int
    ) -> List[CodeSuggestion]:
        """Processa a resposta da análise."""
        try:
            suggestions = []
            lines = response.split('\n')
            current_suggestion = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('Linha ') or line.startswith('Line '):
                    # Finaliza sugestão anterior se existir
                    if current_suggestion:
                        try:
                            suggestions.append(CodeSuggestion(
                                file=file_path,
                                line=current_suggestion.get('line', 0),
                                original_code=current_suggestion.get('original', ''),
                                suggested_code=current_suggestion.get('suggested', ''),
                                explanation=current_suggestion.get('explanation', ''),
                                confidence=0.8
                            ))
                        except Exception as e:
                            logger.error(
                                "ai_analyzer.suggestion_creation_error",
                                file=file_path,
                                error=str(e),
                                suggestion=current_suggestion
                            )
                        
                        current_suggestion = {}
                    
                    # Extrai número da linha
                    try:
                        line_num = int(''.join(filter(str.isdigit, line.split(':')[0])))
                        current_suggestion['line'] = line_num
                    except:
                        current_suggestion['line'] = 0
                
                elif line.lower().startswith('original:'):
                    current_suggestion['original'] = line.split(':', 1)[1].strip()
                
                elif line.lower().startswith('sugestão:'):
                    current_suggestion['suggested'] = line.split(':', 1)[1].strip()
                
                elif line.lower().startswith('explicação:'):
                    current_suggestion['explanation'] = line.split(':', 1)[1].strip()
            
            # Adiciona última sugestão se existir
            if current_suggestion:
                try:
                    suggestions.append(CodeSuggestion(
                        file=file_path,
                        line=current_suggestion.get('line', 0),
                        original_code=current_suggestion.get('original', ''),
                        suggested_code=current_suggestion.get('suggested', ''),
                        explanation=current_suggestion.get('explanation', ''),
                        confidence=0.8
                    ))
                except Exception as e:
                    logger.error(
                        "ai_analyzer.suggestion_creation_error",
                        file=file_path,
                        error=str(e),
                        suggestion=current_suggestion
                    )
            
            return suggestions
        except Exception as e:
            logger.error(
                "ai_analyzer.parse_error",
                file=file_path,
                error=str(e),
                error_type=type(e).__name__
            )
            return [] 