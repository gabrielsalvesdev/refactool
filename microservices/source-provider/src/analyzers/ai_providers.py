"""
Provedores de IA para análise de código.
"""

from abc import ABC, abstractmethod
import json
from typing import Dict, List, Optional
import aiohttp
import structlog
import asyncio
import logging
import os

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
        api_url: str = "https://api.deepseek.com/v1/completions",
        model: str = "deepseek-coder-33b-instruct"
    ):
        super().__init__(api_key)
        self.api_url = api_url
        self.model = model
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Gera uma completação usando DeepSeek."""
        if not self._session:
            await self.start()
            
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        data = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.95),
            "stream": False
        }
        
        try:
            async with self._session.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=kwargs.get("timeout", 30)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result["choices"][0]["text"]
                
        except Exception as e:
            logger.error(
                "deepseek_provider.completion_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

class OllamaProvider(AIProvider):
    """Provedor usando Ollama."""
    
    def __init__(
        self,
        model: str = "llama2:13b",
        api_url: str = "http://localhost:11434/api/generate",
        timeout: int = 60
    ):
        super().__init__()
        self.api_url = api_url
        self.model = model
        self.timeout = timeout
        
    async def complete(self, prompt: str, **kwargs) -> str:
        """Gera uma completação usando Ollama."""
        if not self._session:
            await self.start()
            
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        logger.info(
            "OllamaProvider.sending_request",
            model=self.model,
            prompt_length=len(prompt)
        )
        
        try:
            async with self._session.post(
                self.api_url,
                json=data,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result["response"]
                
        except Exception as e:
            logger.error(
                "ollama_provider.completion_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

class OpenAIProvider(AIProvider):
    """Provedor usando OpenAI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.openai.com/v1/completions",
        model: str = "gpt-3.5-turbo-instruct"
    ):
        super().__init__(api_key)
        self.api_url = api_url
        self.model = model
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Gera uma completação usando OpenAI."""
        if not self._session:
            await self.start()
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.95),
            "stream": False
        }
        
        try:
            async with self._session.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=kwargs.get("timeout", 30)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result["choices"][0]["text"]
                
        except Exception as e:
            logger.error(
                "openai_provider.completion_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

class GeminiProvider(AIProvider):
    """Provedor usando Google Gemini."""
    
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        model: str = "gemini-2.0-flash"
    ):
        super().__init__(api_key)
        self.api_url = f"{api_url}?key={api_key}"
        self.model = model
        
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """Gera uma completação usando Gemini."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json"
                }
                
                data = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                        "topP": 0.8,
                        "topK": 40
                    }
                }
                
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status != 200:
                        raise Exception(f"Erro na API do Gemini: {response.status}")
                        
                    result = await response.json()
                    
                    if "error" in result:
                        raise Exception(f"Erro na API do Gemini: {result['error']}")
                        
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                    
        except Exception as e:
            logger.error(
                "gemini_provider.completion_failed",
                error=str(e)
            )
            raise 