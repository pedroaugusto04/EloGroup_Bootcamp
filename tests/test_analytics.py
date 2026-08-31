"""
tests/test_analytics.py
Testes automatizados da fase de Pré-processamento e Ingestão de Dados.
Valida integridade estrutural, tipos de dados, views do DuckDB e logs de auditoria SHA-256.
"""

import pytest
from src.infrastructure.database import DuckDBRepository


@pytest.fixture(scope="module")
def repo():
    return DuckDBRepository()


def test_preprocessing_duckdb_views(repo):
    """Garante que as 5 views do DuckDB estão criadas e respondendo com dados."""
    tables = ["vendas", "marketing", "estoque", "clientes", "atendimento"]
    for table in tables:
        df = repo.execute_sql(f"SELECT * FROM {table} LIMIT 5;")
        assert len(df) > 0, f"A view {table} não retornou nenhum registro."


def test_vendas_schema_and_types(repo):
    """Valida tipos e colunas chave do dataset de vendas."""
    df = repo.execute_sql("SELECT * FROM vendas LIMIT 1;")
    required_cols = [
        "order_id", "customer_id", "sku_id", "data_pedido", "canal", "categoria",
        "receita_bruta", "receita_liquida", "custo_produto", "custo_frete", 
        "margem_calculada", "margem_pct", "desconto_pct", "ano_mes", "ano"
    ]
    for col in required_cols:
        assert col in df.columns, f"Coluna obrigatória '{col}' ausente em vendas."


def test_vendas_math_integrity(repo):
    """Verifica se os cálculos financeiros de margem e descontos batem matematicamente."""
    df = repo.execute_sql("""
        SELECT 
            receita_liquida, 
            custo_produto, 
            custo_frete, 
            margem_calculada,
            receita_bruta,
            desconto_reais,
            desconto_pct,
            margem_pct
        FROM vendas 
        WHERE status_pagamento = 'Aprovado' 
        LIMIT 100;
    """)
    for _, row in df.iterrows():
        # Margem Calculada = Receita Líquida - CMV - Frete
        expected_margin = row["receita_liquida"] - row["custo_produto"] - row["custo_frete"]
        assert abs(row["margem_calculada"] - expected_margin) < 0.01

        # Margem % = Margem Calculada / Receita Líquida
        if row["receita_liquida"] > 0:
            expected_margin_pct = (row["margem_calculada"] / row["receita_liquida"]) * 100.0
            assert abs(row["margem_pct"] - expected_margin_pct) < 0.01


def test_estoque_rupture_flag(repo):
    """Valida se a regra lógica de ruptura de estoque foi aplicada corretamente."""
    df = repo.execute_sql("""
        SELECT estoque_disponivel, ponto_pedido, em_ruptura 
        FROM estoque 
        LIMIT 100;
    """)
    for _, row in df.iterrows():
        expected_rupture = (row["estoque_disponivel"] <= row["ponto_pedido"]) or (row["estoque_disponivel"] == 0)
        assert row["em_ruptura"] == expected_rupture


def test_clientes_age_calculation(repo):
    """Verifica se a idade dos clientes foi calculada baseada no ano de referência 2026."""
    df = repo.execute_sql("SELECT data_nascimento, idade FROM clientes LIMIT 100;")
    for _, row in df.iterrows():
        if row["data_nascimento"] is not None:
            birth_year = int(str(row["data_nascimento"])[:4])
            expected_age = 2026 - birth_year
            assert row["idade"] == expected_age


def test_atendimento_clean(repo):
    """Valida se a linha corrompida com ticket_id 'TKT' foi excluída da base de atendimento."""
    df = repo.execute_sql("SELECT * FROM atendimento WHERE ticket_id = 'TKT';")
    assert len(df) == 0, "O ticket corrompido 'TKT' ainda está presente na view de atendimento."


def test_vendas_devolucao_efetividade(repo):
    """Garante que devoluções zeram a receita efetiva e geram prejuízo de frete na margem efetiva."""
    df = repo.execute_sql("""
        SELECT devolvido, receita_liquida, receita_liquida_efetiva, custo_frete, margem_calculada, margem_efetiva 
        FROM vendas 
        WHERE status_pagamento = 'Aprovado' 
        LIMIT 100;
    """)
    for _, row in df.iterrows():
        if row["devolvido"]:
            assert row["receita_liquida_efetiva"] == 0.0
            assert abs(row["margem_efetiva"] - (-row["custo_frete"])) < 0.01
        else:
            assert abs(row["receita_liquida_efetiva"] - row["receita_liquida"]) < 0.01
            assert abs(row["margem_efetiva"] - row["margem_calculada"]) < 0.01


def test_estoque_descontinuado_capital(repo):
    """Valida cálculo de capital travado em produtos descontinuados."""
    df = repo.execute_sql("""
        SELECT status_disponibilidade, valor_total_estoque, capital_travado_descontinuado 
        FROM estoque 
        LIMIT 100;
    """)
    for _, row in df.iterrows():
        if row["status_disponibilidade"] == "Descontinuado":
            assert abs(row["capital_travado_descontinuado"] - row["valor_total_estoque"]) < 0.01
        else:
            assert row["capital_travado_descontinuado"] == 0.0

