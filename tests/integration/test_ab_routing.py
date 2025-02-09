import random
import pytest

from src.ab_routing import route_user
from src.config import ABTestConfig, CohortConfig


def test_route_user_valid_cohorts():
    """Teste para verificar se o usuário é roteado para um dos grupos definidos."""
    config = ABTestConfig(
        name="test_ab",
        cohorts={
            "A": CohortConfig(description="Grupo A", weight=0.5, params={}),
            "B": CohortConfig(description="Grupo B", weight=0.5, params={})
        }
    )
    result = route_user("user123", config)
    assert result in config.cohorts.keys()


def test_route_user_edge_weight():
    """Teste para garantir que, se um grupo tem peso 0, o outro sempre seja selecionado."""
    config = ABTestConfig(
        name="test_ab",
        cohorts={
            "A": CohortConfig(description="Grupo A", weight=0, params={}),
            "B": CohortConfig(description="Grupo B", weight=1.0, params={})
        }
    )
    result = route_user("user456", config)
    # Como o grupo A tem peso zero, o resultado deve ser sempre 'B'
    assert result == "B"


def test_route_user_randomness():
    """Teste para verificar a tendência probabilística com pesos desiguais."""
    config = ABTestConfig(
        name="test_ab",
        cohorts={
            "A": CohortConfig(description="Grupo A", weight=0.1, params={}),
            "B": CohortConfig(description="Grupo B", weight=0.9, params={})
        }
    )
    outcomes = {"A": 0, "B": 0}
    for _ in range(1000):
        chosen = route_user("user789", config)
        outcomes[chosen] += 1
    # Verificar que, estatisticamente, o grupo B é escolhido com mais frequência
    assert outcomes["B"] > outcomes["A"] 