"""
tests/test_database_repository.py
Testes unitários para validar todos os métodos de agregação e queries desacopladas do DuckDBRepository.
"""

import pytest
from src.infrastructure.database import DuckDBRepository


@pytest.fixture(scope="module")
def repo():
    return DuckDBRepository()


def test_repository_get_executive_kpis(repo):
    kpis = repo.get_executive_kpis()
    assert kpis.net_revenue > 0
    assert kpis.gross_revenue >= kpis.net_revenue
    assert kpis.total_orders > 0
    assert kpis.average_csat > 0
    assert kpis.stockout_skus > 0


def test_repository_get_channel_performance(repo):
    channels = repo.get_channel_performance()
    assert len(channels) > 0
    for ch in channels:
        assert ch.channel != ""
        assert ch.orders > 0
        assert ch.net_revenue > 0


def test_repository_get_category_performance(repo):
    categories = repo.get_category_performance()
    assert len(categories) > 0
    for cat in categories:
        assert cat.category != ""
        assert cat.net_revenue > 0


def test_repository_get_customer_segments(repo):
    segments = repo.get_customer_segments()
    assert len(segments) > 0
    for seg in segments:
        assert seg.rfm_segment != ""
        assert seg.total_customers > 0


def test_repository_get_inventory_alerts(repo):
    alerts = repo.get_inventory_alerts(limit=10)
    assert len(alerts) <= 10
    assert len(alerts) > 0
    for item in alerts:
        assert item.sku_id != ""
        assert item.available_stock == 0


def test_repository_get_support_tickets_sample(repo):
    df_tickets = repo.get_support_tickets_sample(limit=15)
    assert len(df_tickets) == 15
    assert "ticket_id" in df_tickets.columns
