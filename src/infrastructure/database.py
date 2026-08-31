"""
src/infrastructure/database.py
Repositório de dados analítico com DuckDB (Serverless In-Memory OLAP).
Utiliza como esquema principal os nomes e dados originais em Português dos CSVs,
com suporte total a consultas ANSI SQL de alta performance e auditoria.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import duckdb
import pandas as pd

from src.config import DB_PATH, PROCESSED_DATA_DIR
from src.domain.models import (
    ExecutiveKPIs,
    ChannelPerformance,
    CategoryPerformance,
    CustomerSegmentSummary,
    InventoryAlert,
)


class DuckDBRepository:
    def __init__(self, db_path: Optional[Path] = None, processed_dir: Path = PROCESSED_DATA_DIR):
        self.db_path = db_path or DB_PATH
        self.processed_dir = processed_dir
        
        # Conexão em memória: permite CREATE VIEW sobre os Parquets sem conflito de locks
        self.conn = duckdb.connect(":memory:")
        self._init_views()

    def _init_views(self):
        """Cria ou atualiza views SQL apontando diretamente para os arquivos Parquet processados em Português."""
        tables = ["vendas", "marketing", "estoque", "clientes", "atendimento"]
        for table in tables:
            parquet_file = self.processed_dir / f"{table}.parquet"
            if parquet_file.exists():
                self.conn.execute(f"""
                    CREATE OR REPLACE VIEW {table} AS 
                    SELECT * FROM read_parquet('{parquet_file.as_posix()}');
                """)

    def execute_sql(self, query: str) -> pd.DataFrame:
        """Executa qualquer consulta SQL ANSI diretamente no DuckDB e retorna DataFrame."""
        return self.conn.execute(query).df()

    def get_executive_kpis(self) -> ExecutiveKPIs:
        """Calcula os KPIs executivos consolidados utilizando as colunas em Português."""
        query_vendas = """
            SELECT 
                COALESCE(SUM(receita_bruta), 0) AS gross_revenue,
                COALESCE(SUM(receita_liquida), 0) AS net_revenue,
                COALESCE(SUM(margem_calculada), 0) AS contribution_margin,
                COALESCE(COUNT(order_id), 0) AS total_orders,
                COALESCE(AVG(receita_liquida), 0) AS average_ticket,
                COALESCE(AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0, 0) AS return_rate_pct
            FROM vendas
            WHERE status_pagamento = 'Aprovado';
        """
        df_v = self.conn.execute(query_vendas).df()
        
        query_mkt = """
            SELECT 
                COALESCE(SUM(investimento_reais), 0) AS investment_mkt,
                COALESCE(SUM(receita_gerada), 0) AS revenue_mkt,
                COALESCE(SUM(investimento_reais) / NULLIF(SUM(conversoes), 0), 0) AS average_cac
            FROM marketing;
        """
        df_m = self.conn.execute(query_mkt).df()

        query_csat = """
            SELECT COALESCE(AVG(nota_csat), 0) AS average_csat FROM atendimento;
        """
        df_c = self.conn.execute(query_csat).df()

        query_estoque = """
            SELECT COUNT(*) AS stockout_skus FROM estoque WHERE em_ruptura = true;
        """
        df_e = self.conn.execute(query_estoque).df()

        net_rev = float(df_v["net_revenue"].iloc[0])
        margin = float(df_v["contribution_margin"].iloc[0])
        margin_pct = (margin / net_rev * 100.0) if net_rev > 0 else 0.0
        inv_mkt = float(df_m["investment_mkt"].iloc[0])
        rec_mkt = float(df_m["revenue_mkt"].iloc[0])
        roas = (rec_mkt / inv_mkt) if inv_mkt > 0 else 0.0

        return ExecutiveKPIs(
            gross_revenue=float(df_v["gross_revenue"].iloc[0]),
            net_revenue=net_rev,
            contribution_margin=margin,
            contribution_margin_pct=margin_pct,
            total_orders=int(df_v["total_orders"].iloc[0]),
            average_ticket=float(df_v["average_ticket"].iloc[0]),
            return_rate_pct=float(df_v["return_rate_pct"].iloc[0]),
            marketing_investment=inv_mkt,
            average_cac=float(df_m["average_cac"].iloc[0]),
            overall_roas=roas,
            average_csat=float(df_c["average_csat"].iloc[0]),
            stockout_skus=int(df_e["stockout_skus"].iloc[0]),
        )

    def get_channel_performance(self) -> List[ChannelPerformance]:
        query = """
            WITH v AS (
                SELECT 
                    canal AS channel,
                    SUM(receita_liquida) AS net_revenue,
                    SUM(margem_calculada) AS margin,
                    COUNT(order_id) AS orders,
                    AVG(receita_liquida) AS average_ticket,
                    AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0 AS return_rate
                FROM vendas
                WHERE status_pagamento = 'Aprovado'
                GROUP BY canal
            ),
            m AS (
                SELECT 
                    canal AS channel,
                    SUM(investimento_reais) AS investment,
                    SUM(receita_gerada) AS rec_mkt,
                    SUM(conversoes) AS conversions
                FROM marketing
                GROUP BY canal
            )
            SELECT 
                v.channel,
                v.net_revenue,
                v.margin,
                (v.margin / NULLIF(v.net_revenue, 0)) * 100.0 AS margin_pct,
                v.orders,
                v.average_ticket,
                COALESCE(m.investment, 0) AS investment,
                COALESCE(m.investment / NULLIF(m.conversions, 0), 0) AS cac,
                COALESCE(m.rec_mkt / NULLIF(m.investment, 0), 0) AS roas,
                v.return_rate
            FROM v
            LEFT JOIN m ON v.channel = m.channel
            ORDER BY v.net_revenue DESC;
        """
        df = self.conn.execute(query).df()
        results = []
        for _, row in df.iterrows():
            results.append(ChannelPerformance(
                channel=str(row["channel"]),
                net_revenue=float(row["net_revenue"]),
                contribution_margin=float(row["margin"]),
                margin_pct=float(row["margin_pct"]) if pd.notnull(row["margin_pct"]) else 0.0,
                orders=int(row["orders"]),
                average_ticket=float(row["average_ticket"]),
                investment=float(row["investment"]),
                cac=float(row["cac"]),
                roas=float(row["roas"]),
                return_rate_pct=float(row["return_rate"]),
            ))
        return results

    def get_category_performance(self) -> List[CategoryPerformance]:
        query = """
            SELECT 
                categoria AS category,
                SUM(receita_liquida) AS net_revenue,
                SUM(custo_produto) AS product_cost,
                SUM(custo_frete) AS shipping_cost,
                SUM(desconto_reais) AS discounts,
                SUM(margem_calculada) AS margin,
                (SUM(margem_calculada) / NULLIF(SUM(receita_liquida), 0)) * 100.0 AS margin_pct,
                COUNT(order_id) AS orders,
                AVG(CASE WHEN devolvido = true THEN 1.0 ELSE 0.0 END) * 100.0 AS return_rate
            FROM vendas
            WHERE status_pagamento = 'Aprovado'
            GROUP BY categoria
            ORDER BY net_revenue DESC;
        """
        df = self.conn.execute(query).df()
        results = []
        for _, row in df.iterrows():
            results.append(CategoryPerformance(
                category=str(row["category"]),
                net_revenue=float(row["net_revenue"]),
                product_cost=float(row["product_cost"]),
                shipping_cost=float(row["shipping_cost"]),
                discounts=float(row["discounts"]),
                contribution_margin=float(row["margin"]),
                margin_pct=float(row["margin_pct"]) if pd.notnull(row["margin_pct"]) else 0.0,
                orders=int(row["orders"]),
                return_rate_pct=float(row["return_rate"]),
            ))
        return results

    def get_customer_segments(self) -> List[CustomerSegmentSummary]:
        query = """
            SELECT 
                COALESCE(segmento_rfm, 'Não Definido') AS rfm_segment,
                COUNT(*) AS total_customers,
                (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clientes)) AS pct_base,
                AVG(ltv_acumulado) AS average_ltv,
                AVG(total_pedidos_historico) AS average_orders,
                AVG(renda_estimada) AS average_income
            FROM clientes
            GROUP BY segmento_rfm
            ORDER BY total_customers DESC;
        """
        df = self.conn.execute(query).df()
        results = []
        for _, row in df.iterrows():
            results.append(CustomerSegmentSummary(
                rfm_segment=str(row["rfm_segment"]),
                total_customers=int(row["total_customers"]),
                pct_base=float(row["pct_base"]),
                average_ltv=float(row["average_ltv"]),
                average_orders=float(row["average_orders"]),
                average_income=float(row["average_income"]),
            ))
        return results

    def get_inventory_alerts(self, limit: int = 50) -> List[InventoryAlert]:
        query = f"""
            SELECT 
                sku_id,
                nome_produto AS product_name,
                categoria AS category,
                estoque_disponivel AS available_stock,
                ponto_pedido AS reorder_point,
                lead_time_reposicao AS lead_time,
                status_disponibilidade AS status,
                custo_unitario AS unit_cost,
                preco_venda_sugerido AS selling_price
            FROM estoque
            WHERE em_ruptura = true
            ORDER BY (ponto_pedido - estoque_disponivel) DESC
            LIMIT {limit};
        """
        df = self.conn.execute(query).df()
        results = []
        for _, row in df.iterrows():
            results.append(InventoryAlert(
                sku_id=str(row["sku_id"]),
                product_name=str(row["product_name"]),
                category=str(row["category"]),
                available_stock=int(row["available_stock"]),
                reorder_point=int(row["reorder_point"]),
                lead_time=int(row["lead_time"]),
                status=str(row["status"]),
                unit_cost=float(row["unit_cost"]),
                selling_price=float(row["selling_price"]),
            ))
        return results

    def get_support_tickets_sample(self, limit: int = 100) -> pd.DataFrame:
        query = f"""
            SELECT * FROM atendimento
            ORDER BY data_abertura DESC
            LIMIT {limit};
        """
        return self.conn.execute(query).df()
