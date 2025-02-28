from collections import OrderedDict
import sys
import hashlib
import threading
import time
from typing import Any, Optional

class LRUCache:
    """
    Implementação de um cache LRU (Least Recently Used) com controle de memória,
    versionamento e timeouts
    """
    def __init__(self, max_memory_mb=20, version=1, default_timeout=30):
        """
        Inicializa o cache com um limite máximo de memória em MB
        """
        self.max_memory = max_memory_mb * 1024 * 1024  # Converte MB para bytes
        self.cache = OrderedDict()
        self.memory_usage = 0
        self.version = version
        self.default_timeout = default_timeout
        self.lock = threading.RLock()
        self.timeouts = {}  # Armazena timestamps de expiração

    def _get_versioned_key(self, key):
        """
        Retorna a chave com a versão atual
        """
        return f"v{self.version}:{key}"

    def _is_expired(self, key):
        """
        Verifica se uma chave está expirada
        """
        if key in self.timeouts:
            return time.time() > self.timeouts[key]
        return False

    def _cleanup_expired(self):
        """
        Remove itens expirados do cache
        """
        current_time = time.time()
        expired_keys = [
            k for k, t in self.timeouts.items() 
            if current_time > t
        ]
        for key in expired_keys:
            self._remove_item(key)

    def _remove_item(self, key):
        """
        Remove um item do cache e atualiza uso de memória
        """
        if key in self.cache:
            value = self.cache.pop(key)
            self.memory_usage -= sys.getsizeof(value)
            self.timeouts.pop(key, None)

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Obtém um valor do cache com timeout. Move o item para o final (mais recentemente usado)
        """
        with self.lock:
            self._cleanup_expired()
            versioned_key = self._get_versioned_key(key)
            
            if versioned_key not in self.cache or self._is_expired(versioned_key):
                return default
            
            # Move para o final e retorna
            value = self.cache.pop(versioned_key)
            self.cache[versioned_key] = value
            return value

    def put(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Insere um valor no cache com timeout opcional.
        Se necessário, remove itens antigos para liberar memória
        """
        with self.lock:
            self._cleanup_expired()
            versioned_key = self._get_versioned_key(key)
            
            # Remove item existente se houver
            if versioned_key in self.cache:
                self._remove_item(versioned_key)
            
            # Calcula o tamanho do novo valor
            value_size = sys.getsizeof(value)
            
            # Remove itens antigos até ter espaço suficiente
            while self.memory_usage + value_size > self.max_memory and self.cache:
                _, oldest_value = self.cache.popitem(last=False)
                self.memory_usage -= sys.getsizeof(oldest_value)
            
            # Adiciona o novo item
            self.cache[versioned_key] = value
            self.memory_usage += value_size
            
            # Define timeout
            if timeout is not None:
                self.timeouts[versioned_key] = time.time() + timeout
            elif self.default_timeout:
                self.timeouts[versioned_key] = time.time() + self.default_timeout

    def force_eviction(self) -> None:
        """
        Força a remoção de itens até que o uso de memória esteja abaixo do limite
        """
        with self.lock:
            self._cleanup_expired()
            while self.memory_usage > self.max_memory and self.cache:
                self._remove_item(next(iter(self.cache)))

    def get_memory_usage(self) -> int:
        """
        Retorna o uso atual de memória em bytes
        """
        return self.memory_usage

    def clear(self) -> None:
        """
        Limpa todo o cache
        """
        with self.lock:
            self.cache.clear()
            self.memory_usage = 0
            self.timeouts.clear()

    def exists(self, key: str) -> bool:
        """
        Verifica se uma chave existe e não está expirada no cache
        """
        with self.lock:
            versioned_key = self._get_versioned_key(key)
            return (
                versioned_key in self.cache and 
                not self._is_expired(versioned_key)
            )

    def update_version(self, new_version: int) -> None:
        """
        Atualiza a versão do cache, invalidando todas as chaves antigas
        """
        with self.lock:
            self.version = new_version
            self.clear()  # Limpa o cache ao atualizar a versão 