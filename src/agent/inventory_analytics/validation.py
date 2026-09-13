"""Validações de parâmetros de consulta, sem interpolação de SQL."""

import re
from typing import Optional
from src.infrastructure.database import DuckDBRepository

SKU_PATTERN = re.compile(r"^SKU-\d{5}$")


def validate_limit(limit: int, maximum: int = 1000) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= maximum:
        raise ValueError(f"limit deve estar entre 1 e {maximum}.")
    return limit


def validate_category(repo: DuckDBRepository, category: Optional[str]) -> Optional[str]:
    if category is None:
        return None
    if not isinstance(category, str) or not category.strip() or len(category) > 100:
        raise ValueError("categoria inválida.")
    category = category.strip()
    valid = set(repo.execute_sql("SELECT DISTINCT categoria FROM estoque WHERE categoria IS NOT NULL")["categoria"])
    if category not in valid:
        raise ValueError("categoria não encontrada; nenhum trecho SQL é aceito nesse campo.")
    return category


def validate_sku(sku_id: str) -> str:
    if not isinstance(sku_id, str) or not SKU_PATTERN.fullmatch(sku_id.strip()):
        raise ValueError("sku_id inválido; use o formato SKU-00000.")
    return sku_id.strip()
