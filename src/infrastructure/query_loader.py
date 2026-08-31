"""
src/infrastructure/query_loader.py
Carregador e gerenciador de consultas SQL a partir de arquivos dedicados (.sql).
Permite manter queries organizadas, comentadas e desacopladas do código Python.
"""

from pathlib import Path
from typing import Dict, Any, Optional

QUERIES_DIR = Path(__file__).resolve().parent.parent / "queries"


def load_query(relative_path: str, **params: Any) -> str:
    """
    Carrega o conteúdo de um arquivo SQL e formata parâmetros dinâmicos se fornecidos.

    Exemplo de uso:
        query = load_query("vendas/decomposicao_margem.sql", where_sql="WHERE status_pagamento = 'Aprovado'")
    """
    sql_file = QUERIES_DIR / relative_path
    if not sql_file.exists():
        raise FileNotFoundError(f"Arquivo de query SQL não encontrado: {sql_file}")

    with open(sql_file, "r", encoding="utf-8") as f:
        query_text = f.read()

    if params:
        # Substitui parâmetros com segurança
        try:
            return query_text.format(**params)
        except KeyError as e:
            raise KeyError(f"Parâmetro esperado não fornecido para a query '{relative_path}': {e}")

    return query_text
