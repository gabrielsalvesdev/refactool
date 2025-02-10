class Client:
    def __init__(self):
        # Usar um dicionário para simular armazenamento, se necessário
        self.filters = {}
    
    def bfExists(self, key, item):
        # Sempre retorna False para um item que não foi adicionado
        # Esta implementação simples faz sempre retornar False
        return False
    
    def bfAdd(self, key, item):
        # Simplesmente retorna True para indicar que a operação foi bem-sucedida
        return True 