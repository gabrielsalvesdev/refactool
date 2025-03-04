"""
Analisador de código usando IA.
"""

from dataclasses import dataclass
from typing import List, Optional
import structlog

logger = structlog.get_logger()

@dataclass
class AIAnalysisConfig:
    """Configuração para análise de IA."""
    provider: any
    temperature: float = 0.3
    max_tokens: int = 1000
    chunk_size: int = 1000

@dataclass
class CodeSuggestion:
    """Sugestão de melhoria para o código."""
    line: int
    message: str
    original_code: Optional[str] = None
    suggested_code: Optional[str] = None
    explanation: Optional[str] = None

class AIAnalyzer:
    """Analisador de código usando IA."""
    
    def __init__(self, config: AIAnalysisConfig):
        self.config = config
        self.provider = config.provider
    
    async def analyze_code(self, content: str, language: str) -> List[CodeSuggestion]:
        """
        Analisa código usando IA.
        
        Args:
            content: Conteúdo do código
            language: Linguagem do código
            
        Returns:
            Lista de sugestões
        """
        try:
            # Divide o código em chunks se necessário
            chunks = self._split_into_chunks(content)
            suggestions = []
            
            for chunk in chunks:
                # Gera prompt para análise
                prompt = self._generate_code_prompt(chunk, language)
                
                # Obtém resposta do provedor
                response = await self.provider.complete(prompt)
                
                # Processa a resposta
                chunk_suggestions = self._process_code_response(response, chunk)
                suggestions.extend(chunk_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Erro ao analisar código: {str(e)}")
            return []
    
    async def analyze_text(self, content: str, file_type: str = None) -> str:
        """
        Analisa texto usando IA.
        
        Args:
            content: Conteúdo do texto
            file_type: Tipo do arquivo (opcional)
            
        Returns:
            Resumo do texto
        """
        try:
            # Gera prompt específico baseado no tipo de arquivo
            prompt = self._generate_text_prompt(content, file_type)
            
            # Obtém resposta do provedor
            response = await self.provider.complete(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao analisar texto: {str(e)}")
            return "Não foi possível gerar um resumo do texto."
    
    def _split_into_chunks(self, content: str) -> List[str]:
        """Divide o conteúdo em chunks menores."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > self.config.chunk_size:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _generate_code_prompt(self, code: str, language: str) -> str:
        """Gera prompt para análise de código."""
        return f"""Analise o seguinte código {language} e forneça sugestões de melhorias:

{code}

Por favor, forneça sugestões específicas para melhorar:
1. Legibilidade
2. Performance
3. Boas práticas
4. Segurança
5. Manutenibilidade

Formato da resposta:
- Linha X: Descrição do problema
  Sugestão: Código sugerido
  Explicação: Por que essa mudança é importante
"""
    
    def _generate_text_prompt(self, content: str, file_type: str = None) -> str:
        """Gera prompt para análise de texto."""
        if file_type == 'Arduino':
            return f"""Analise o seguinte código Arduino e forneça um resumo detalhado:

{content}

O resumo deve incluir:
1. Propósito do código
2. Funcionalidades principais
3. Componentes e periféricos utilizados
4. Considerações de hardware
5. Possíveis melhorias

Por favor, forneça o resumo em português do Brasil.
"""
        elif file_type == 'PowerShell':
            return f"""Analise o seguinte script PowerShell e forneça um resumo detalhado:

{content}

O resumo deve incluir:
1. Objetivo do script
2. Comandos principais
3. Interações com o sistema
4. Considerações de segurança
5. Possíveis melhorias

Por favor, forneça o resumo em português do Brasil.
"""
        elif file_type == 'C/C++ Header':
            return f"""Analise o seguinte arquivo de cabeçalho C/C++ e forneça um resumo detalhado:

{content}

O resumo deve incluir:
1. Propósito do arquivo
2. Definições e estruturas principais
3. Funções e macros
4. Dependências
5. Possíveis melhorias

Por favor, forneça o resumo em português do Brasil.
"""
        else:
            return f"""Analise o seguinte texto e forneça um resumo conciso e informativo:

{content}

O resumo deve incluir:
1. Tema principal
2. Pontos chave
3. Conclusões ou recomendações (se houver)

Por favor, forneça o resumo em português do Brasil.
"""
    
    def _process_code_response(self, response: str, code: str) -> List[CodeSuggestion]:
        """Processa a resposta do provedor de IA."""
        suggestions = []
        lines = response.split('\n')
        current_suggestion = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('- Linha'):
                # Finaliza sugestão anterior se existir
                if current_suggestion:
                    suggestions.append(current_suggestion)
                
                # Inicia nova sugestão
                try:
                    line_number = int(line.split(':')[0].split()[-1])
                    message = line.split(':', 1)[1].strip()
                    current_suggestion = CodeSuggestion(
                        line=line_number,
                        message=message
                    )
                except:
                    continue
                    
            elif line.startswith('Sugestão:'):
                if current_suggestion:
                    current_suggestion.suggested_code = line.split(':', 1)[1].strip()
                    
            elif line.startswith('Explicação:'):
                if current_suggestion:
                    current_suggestion.explanation = line.split(':', 1)[1].strip()
        
        # Adiciona última sugestão se existir
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions 