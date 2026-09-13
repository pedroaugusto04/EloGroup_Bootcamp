"""Janelas temporais tipadas do copiloto de estoque."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Literal

from src.infrastructure.database import DuckDBRepository

PeriodKey = Literal["full_history", "calendar_2023", "last_90d_observed"]
VALID_PERIOD_KEYS = ("full_history", "calendar_2023", "last_90d_observed")


@dataclass(frozen=True)
class SalesPeriod:
    key: str
    start: date
    end: date

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def label(self) -> str:
        labels = {
            "full_history": "Histórico completo observado",
            "calendar_2023": "Ano-calendário 2023",
            "last_90d_observed": "Últimos 90 dias observados",
        }
        return labels[self.key]


def resolve_period(repo: DuckDBRepository, period_key: str = "full_history") -> SalesPeriod:
    """Resolve datas no backend; rótulos nunca são recebidos separadamente."""
    if period_key not in VALID_PERIOD_KEYS:
        raise ValueError(
            f"period_key inválido: {period_key!r}. Valores aceitos: {', '.join(VALID_PERIOD_KEYS)}"
        )
    bounds = repo.execute_sql(
        "SELECT MIN(CAST(data_pedido AS DATE)) AS start, "
        "MAX(CAST(data_pedido AS DATE)) AS end FROM vendas WHERE data_pedido IS NOT NULL"
    ).iloc[0]
    observed_start = bounds["start"]
    observed_end = bounds["end"]
    if observed_start is None or observed_end is None:
        raise ValueError("A base de Vendas não possui datas válidas para resolver o período.")
    if isinstance(observed_start, datetime):
        observed_start = observed_start.date()
    elif not isinstance(observed_start, date):
        observed_start = observed_start.date()
    if isinstance(observed_end, datetime):
        observed_end = observed_end.date()
    elif not isinstance(observed_end, date):
        observed_end = observed_end.date()

    if period_key == "calendar_2023":
        start, end = date(2023, 1, 1), date(2023, 12, 31)
    elif period_key == "last_90d_observed":
        end = observed_end
        start = end - timedelta(days=89)
    else:
        start, end = observed_start, observed_end
    return SalesPeriod(period_key, start, end)


def build_meta(period: SalesPeriod, warnings=None) -> Dict[str, object]:
    return {
        "period_key": period.key,
        "sales_start": period.start.isoformat(),
        "sales_end": period.end.isoformat(),
        "days": period.days,
        "sales_role": "historical_trend",
        "stock_as_of": None,
        "financial_source": "vendas",
        "operational_source": "estoque",
        "warnings": list(warnings or []),
    }


def methodology_banner(period: SalesPeriod) -> str:
    return (
        "Posição de estoque fornecida — data de referência não informada. "
        f"Tendência de vendas observada entre {period.start:%d/%m/%Y} e {period.end:%d/%m/%Y}."
    )
