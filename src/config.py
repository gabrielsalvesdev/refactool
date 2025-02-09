import yaml
import logging
from pydantic import BaseModel, ValidationError, confloat, HttpUrl
from typing import Dict, Union

logger = logging.getLogger(__name__)

class CohortConfig(BaseModel):
    description: str
    weight: confloat(ge=0, le=1)
    params: Dict[str, Union[float, int, str]]
    documentation_url: HttpUrl = "https://example.com/ab-docs"


class ABTestConfig(BaseModel):
    name: str
    cohorts: Dict[str, CohortConfig]


def load_ab_config(config_file: str = "configs/ab_lru.yaml") -> ABTestConfig:
    try:
        with open(config_file, "r") as f:
            raw_config = yaml.safe_load(f)
        return ABTestConfig(**raw_config)  # Validação automática
    except FileNotFoundError:
        logger.critical(f"Arquivo de configuração {config_file} não encontrado")
        raise
    except ValidationError as e:
        logger.error(f"Configuração inválida: {e.errors()}")
        raise 