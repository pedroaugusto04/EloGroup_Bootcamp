import pytest
from src.infrastructure.database import DuckDBRepository
from src.infrastructure.query_loader import load_query

@pytest.fixture
def repo():
    return DuckDBRepository()

def test_mkt_vs_vendas_query(repo):
    q = load_query('relacional/mkt_vs_vendas_real.sql')
    df = repo.execute_sql(q)
    assert not df.empty
    assert 'canal' in df.columns
    assert 'investimento_mkt' in df.columns
    assert 'receita_liquida_real' in df.columns
    assert df['receita_liquida_real'].sum() > 0

def test_estoque_vs_vendas_query(repo):
    q = load_query('relacional/estoque_vs_vendas_giro.sql')
    df = repo.execute_sql(q)
    assert not df.empty
    assert 'categoria' in df.columns
    assert 'capital_imobilizado_estoque' in df.columns
    assert 'receita_real' in df.columns
    assert df['capital_imobilizado_estoque'].sum() > 0

def test_vendas_vs_atendimento_query(repo):
    q = load_query('relacional/vendas_vs_atendimento_atrito.sql')
    df = repo.execute_sql(q)
    assert not df.empty
    assert 'faixa_entrega' in df.columns
    assert 'total_pedidos' in df.columns
    assert 'csat_medio' in df.columns

def test_clientes_ciclo_atrito_query(repo):
    q = load_query('relacional/clientes_ciclo_atrito.sql')
    df = repo.execute_sql(q)
    assert not df.empty
    assert 'segmento_rfm' in df.columns
    assert 'ltv_medio' in df.columns
    assert 'clientes_com_csat_critico' in df.columns
