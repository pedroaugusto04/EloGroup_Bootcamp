import pytest
from src.infrastructure.database import DuckDBRepository
from src.api.routes.audit import calculate_iqr_stats

TABLE_CONFIGS = {
    "vendas": {
        "metrics": ["margem_pct", "margem_calculada", "receita_liquida", "desconto_reais"],
        "where": "status_pagamento = 'Aprovado'"
    },
    "estoque": {
        "metrics": ["valor_total_estoque", "lead_time_reposicao", "custo_unitario"],
        "where": ""
    },
    "clientes": {
        "metrics": ["ltv_acumulado", "total_pedidos_historico", "renda_estimada"],
        "where": ""
    },
    "atendimento": {
        "metrics": ["tempo_resolucao_horas", "tempo_primeira_resposta_minutos", "nota_csat"],
        "where": ""
    },
    "marketing": {
        "metrics": ["cac", "roas", "investimento_reais"],
        "where": ""
    }
}

@pytest.fixture
def repo():
    return DuckDBRepository()

def test_table_configs_and_metrics(repo):
    for table_name, cfg in TABLE_CONFIGS.items():
        where_c = f"WHERE {cfg['where']}" if cfg['where'] else ''
        df = repo.execute_sql(f"SELECT * FROM {table_name} {where_c}")
        assert not df.empty
        for metric_key in cfg['metrics']:
            assert metric_key in df.columns
            stats = calculate_iqr_stats(df, metric_key)
            assert stats['total_records'] == len(df[metric_key].dropna())
            assert stats['lower_bound'] <= stats['upper_bound']
