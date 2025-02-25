"""
Provedores de IA para análise de código.
"""

from abc import ABC, abstractmethod
import json
from typing import Dict, List, Optional
import aiohttp
import structlog

logger = structlog.get_logger()

class AIProvider(ABC):
    """Classe base para provedores de IA."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Inicializa o provedor."""
        if not self._session:
            self._session = aiohttp.ClientSession()
            logger.info(f"{self.__class__.__name__}.started")
    
    async def stop(self):
        """Finaliza o provedor."""
        if self._session:
            await self._session.close()
            self._session = None
            logger.info(f"{self.__class__.__name__}.stopped")
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Gera uma completação para o prompt."""
        pass

class DeepSeekProvider(AIProvider):
    """Provedor usando DeepSeek."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.deepseek.com/v1/chat/completions",
        model: str = "deepseek-coder-33b-instruct"
    ):
        super().__init__(api_key)
        self.api_url = api_url
        self.model = model
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Gera uma completação usando DeepSeek.
        
        Args:
            prompt: O prompt para completação
            **kwargs: Argumentos adicionais (temperature, max_tokens, etc)
            
        Returns:
            A resposta gerada
        """
        if not self._session:
            await self.start()
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with self._session.post(
                self.api_url,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um especialista em análise e refatoração de código Python."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    **kwargs
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"DeepSeek API error: {error_text}")
                
                data = await response.json()
                return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error("deepseek.api_call_failed", error=str(e))
            raise

class OllamaProvider(AIProvider):
    """Provedor usando Ollama local."""
    
    def __init__(
        self,
        api_url: str = "http://localhost:11434/api/generate",
        model: str = "codellama"
    ):
        super().__init__()
        self.api_url = api_url
        self.model = model
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Gera uma completação usando Ollama.
        
        Args:
            prompt: O prompt para completação
            **kwargs: Argumentos adicionais (temperature, max_tokens, etc)
            
        Returns:
            A resposta gerada
        """
        if not self._session:
            await self.start()
        
        try:
            async with self._session.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama API error: {error_text}")
                
                data = await response.json()
                return data['response']
        except Exception as e:
            logger.error("ollama.api_call_failed", error=str(e))
            raise 