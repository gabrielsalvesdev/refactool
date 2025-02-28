import pytest
from unittest.mock import patch, MagicMock

def test_cluster_slot_distribution():
    """
    Testa a distribuição de slots no cluster usando um mock
    """
    with patch('redis.Redis') as mock_redis:
        # Configura o mock para simular um cluster
        mock_cluster = MagicMock()
        mock_cluster.cluster.return_value = {
            'cluster_enabled': True,
            'cluster_slots': 16384,
            'cluster_known_nodes': 3
        }
        mock_redis.return_value = mock_cluster
        
        # Importa o módulo que usa o Redis
        from api.src.cache.cluster import get_slot_distribution
        
        # Executa o teste
        distribution = get_slot_distribution()
        
        # Verifica se a distribuição é válida
        assert distribution['total_slots'] == 16384
        assert distribution['nodes'] == 3
        assert distribution['slots_per_node'] == 16384 / 3 