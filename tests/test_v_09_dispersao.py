import pytest
from src.infrastructure.database import DuckDBRepository
from app.views.v_09_dispersao_outliers import TABLE_CONFIGS, calculate_iqr_stats

@pytest.fixture
def repo():
    return DuckDBRepository()

def test_table_configs_and_metrics(repo):
    for base_name, cfg in TABLE_CONFIGS.items():
        where_c = f"WHERE {cfg['default_where']}" if cfg['default_where'] else ''
        df = repo.execute_sql(f"SELECT * FROM {cfg['table']} {where_c}")
        assert not df.empty
        for metric_key in cfg['metrics']:
            assert metric_key in df.columns
            stats = calculate_iqr_stats(df[metric_key])
            assert stats['n'] == len(df[metric_key].dropna())
            assert stats['lower_bound'] <= stats['upper_bound']
