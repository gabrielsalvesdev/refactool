import random
import logging
from src.config import load_ab_config, ABTestConfig

# Certifica-se de que exista um logger configurado
logger = logging.getLogger(__name__)

def route_user(user_id: str, ab_config: ABTestConfig = None) -> str:
    """Roteia o usuário para um grupo baseado nos pesos definidos na configuração AB."""
    if ab_config is None:
        ab_config = load_ab_config()
    total_weight = sum(cohort.weight for cohort in ab_config.cohorts.values())
    rand_value = random.uniform(0, total_weight)
    cumulative = 0
    chosen = None
    for cohort_name, cohort in ab_config.cohorts.items():
        cumulative += cohort.weight
        if rand_value <= cumulative:
            chosen = cohort_name
            break
    return chosen

def route_strategy(user_id: str, ab_config: ABTestConfig = None):
    """Determina a estratégia de roteamento do usuário considerando o sanity check no peso do grupo control."""
    if ab_config is None:
        ab_config = load_ab_config()
    if "control" in ab_config.cohorts and ab_config.cohorts["control"].weight >= 1.0:
        logger.warning("Fallback para estratégia tradicional (weight=1.0)")
        try:
            from src import lru_traditional
            return lru_traditional.process_request(user_id)
        except ImportError:
            logger.error("Módulo lru_traditional não encontrado, fallback não disponível")
            return None
    else:
        # Utiliza o roteamento normal se não for caso de fallback
        return route_user(user_id, ab_config)

if __name__ == '__main__':
    # Exemplo de uso do roteamento AB
    print("Usuário roteado para o grupo:", route_user("user_exemplo"))
    # Exemplo de uso da rota com sanity check
    print("Resultado da estratégia:", route_strategy("user_exemplo")) 