from collections import OrderedDict
import sys
import hashlib

class LRUCache:
    """
    Implementação de um cache LRU (Least Recently Used) com controle de memória e versionamento
    """
    def __init__(self, max_memory_mb=20, version=1):
        """
        Inicializa o cache com um limite máximo de memória em MB
        """
        self.max_memory = max_memory_mb * 1024 * 1024  # Converte MB para bytes
        self.cache = OrderedDict()
        self.memory_usage = 0
        self.version = version

    def _get_versioned_key(self, key):
        """
        Retorna a chave com a versão atual
        """
        return f"v{self.version}:{key}"

    def get(self, key):
        """
        Obtém um valor do cache. Move o item para o final (mais recentemente usado)
        """
        versioned_key = self._get_versioned_key(key)
        if versioned_key not in self.cache:
            return None
        
        # Move para o final
        value = self.cache.pop(versioned_key)
        self.cache[versioned_key] = value
        return value

    def put(self, key, value):
        """
        Insere um valor no cache. Se necessário, remove itens antigos para liberar memória
        """
        versioned_key = self._get_versioned_key(key)
        
        # Se a chave já existe, remove primeiro
        if versioned_key in self.cache:
            old_value = self.cache.pop(versioned_key)
            self.memory_usage -= sys.getsizeof(old_value)
        
        # Calcula o tamanho do novo valor
        value_size = sys.getsizeof(value)
        
        # Remove itens antigos até ter espaço suficiente
        while self.memory_usage + value_size > self.max_memory and self.cache:
            _, oldest_value = self.cache.popitem(last=False)
            self.memory_usage -= sys.getsizeof(oldest_value)
        
        # Adiciona o novo item
        self.cache[versioned_key] = value
        self.memory_usage += value_size

    def force_eviction(self):
        """
        Força a remoção de itens até que o uso de memória esteja abaixo do limite
        """
        while self.memory_usage > self.max_memory and self.cache:
            _, value = self.cache.popitem(last=False)
            self.memory_usage -= sys.getsizeof(value)

    def get_memory_usage(self):
        """
        Retorna o uso atual de memória em bytes
        """
        return self.memory_usage

    def clear(self):
        """
        Limpa todo o cache
        """
        self.cache.clear()
        self.memory_usage = 0

    def exists(self, key):
        """
        Verifica se uma chave existe no cache
        """
        versioned_key = self._get_versioned_key(key)
        return versioned_key in self.cache

    def update_version(self, new_version):
        """
        Atualiza a versão do cache, invalidando todas as chaves antigas
        """
        self.version = new_version
        self.clear()  # Limpa o cache ao atualizar a versão 