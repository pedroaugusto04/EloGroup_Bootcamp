"""
src/infrastructure/preprocessor.py
Pipeline direto de ingestão, saneamento, tipagem e enriquecimento dos 5 datasets.
Carrega os CSVs brutos de data/raw/, aplica transformações e salva em data/processed/*.parquet.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np
import json

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    RAW_FILES,
    ROOT_DIR,
)


class DataPreprocessor:
    def __init__(self, raw_dir: Path = RAW_DATA_DIR, processed_dir: Path = PROCESSED_DATA_DIR):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.quality_report: Dict[str, Any] = {}

    def _save_quality_report(self) -> None:
        path = self.processed_dir / "data_quality_report.json"
        with open(path, "w", encoding="utf-8") as target:
            json.dump(self.quality_report, target, ensure_ascii=False, indent=2)

    def _resolve_raw_path(self, key: str) -> Path:
        filename = RAW_FILES[key]
        p1 = self.raw_dir / filename
        if p1.exists():
            return p1
        p2 = ROOT_DIR / filename
        if p2.exists():
            return p2
        raise FileNotFoundError(f"Arquivo bruto para '{key}' não encontrado: {filename}")

    def _strip_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove espaços sobressalentes nas extremidades de todas as colunas de texto (strip)."""
        str_cols = df.select_dtypes(include=["object", "string"]).columns
        for col in str_cols:
            df[col] = df[col].astype("string").str.strip()
        return df

    def process_vendas(self) -> pd.DataFrame:
        raw_path = self._resolve_raw_path("vendas")
        df = pd.read_csv(raw_path)

        # Quarentena explícita: a linha curta não participa de nenhuma métrica.
        malformed = df["preco_unitario"].isna() | df["status_pagamento"].isna()
        self.quality_report["vendas"] = {
            "raw_rows": int(len(df)),
            "malformed_rows_excluded": int(malformed.sum()),
            "malformed_order_ids": df.loc[malformed, "order_id"].dropna().astype(str).tolist(),
        }
        df = df.loc[~malformed].copy()

        # Padronização de strings (remoção de espaços nas extremidades)
        df = self._strip_strings(df)

        # Padroniza tipos de dados
        df["data_pedido"] = pd.to_datetime(df["data_pedido"], errors="coerce")
        df["devolvido"] = df["devolvido"].map(
            lambda value: pd.NA if pd.isna(value) else str(value).strip().upper() == "TRUE"
        ).astype("boolean")

        # Padroniza colunas numéricas
        numeric_cols = [
            "quantidade", "preco_unitario", "receita_bruta",
            "desconto_reais", "receita_liquida", "custo_produto",
            "custo_frete", "margem_contribuicao", "tempo_entrega_real"
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Métricas calculadas padrão
        df["margem_calculada"] = df["receita_liquida"] - df["custo_produto"] - df["custo_frete"]
        df["margem_pct"] = np.where(df["receita_liquida"] > 0, (df["margem_calculada"] / df["receita_liquida"]) * 100.0, 0.0)
        df["desconto_pct"] = np.where(df["receita_bruta"] > 0, (df["desconto_reais"] / df["receita_bruta"]) * 100.0, 0.0)
        df["ano_mes"] = df["data_pedido"].dt.strftime("%Y-%m")
        df["ano"] = df["data_pedido"].dt.year

        # Flags e Métricas de Efetividade e Impacto Financeiro de Devoluções/Cancelamentos
        df["is_aprovado"] = df["status_pagamento"] == "Aprovado"
        df["is_venda_efetiva"] = (df["status_pagamento"] == "Aprovado") & df["devolvido"].eq(False)
        unknown_return = df["is_aprovado"] & df["devolvido"].isna()
        df["receita_liquida_efetiva"] = 0.0
        df.loc[df["is_venda_efetiva"].fillna(False), "receita_liquida_efetiva"] = df["receita_liquida"]
        df.loc[unknown_return, "receita_liquida_efetiva"] = np.nan
        # Margem efetiva: se devolvido, a receita é estornada e o frete de envio é prejuízo
        df["margem_efetiva"] = 0.0
        df.loc[df["is_venda_efetiva"].fillna(False), "margem_efetiva"] = df["margem_calculada"]
        returned = df["is_aprovado"] & df["devolvido"].eq(True)
        df.loc[returned.fillna(False), "margem_efetiva"] = -df["custo_frete"]
        df.loc[unknown_return, "margem_efetiva"] = np.nan
        df["receita_devolvida"] = 0.0
        df["custo_frete_perdido"] = 0.0
        df.loc[returned.fillna(False), "receita_devolvida"] = df["receita_liquida"]
        df.loc[returned.fillna(False), "custo_frete_perdido"] = df["custo_frete"]
        df.loc[unknown_return, ["receita_devolvida", "custo_frete_perdido"]] = np.nan

        parquet_path = self.processed_dir / "vendas.parquet"
        df.to_parquet(parquet_path, index=False)
        self._save_quality_report()
        return df

    def process_marketing(self) -> pd.DataFrame:
        raw_path = self._resolve_raw_path("marketing")
        df = pd.read_csv(raw_path)

        # Padronização de strings (remoção de espaços nas extremidades)
        df = self._strip_strings(df)

        # Padroniza tipos de dados
        df["data_inicio"] = pd.to_datetime(df["data_inicio"], errors="coerce")
        df["data_fim"] = pd.to_datetime(df["data_fim"], errors="coerce")

        # Padroniza colunas numéricas
        num_cols = ["investimento_reais", "impressoes", "cliques", "conversoes", "roas", "receita_gerada", "cac"]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Calcula métricas adicionais
        df["ctr_pct"] = np.where(df["impressoes"] > 0, (df["cliques"] / df["impressoes"]) * 100.0, 0.0)
        df["taxa_conversao_pct"] = np.where(df["cliques"] > 0, (df["conversoes"] / df["cliques"]) * 100.0, 0.0)
        df["cpc_reais"] = np.where(df["cliques"] > 0, df["investimento_reais"] / df["cliques"], 0.0)
        df["lucro_bruto_mkt"] = df["receita_gerada"] - df["investimento_reais"]
        df["duracao_dias"] = (df["data_fim"] - df["data_inicio"]).dt.days
        df["cpa_calculado"] = np.where(df["conversoes"] > 0, df["investimento_reais"] / df["conversoes"], 0.0)
        df["is_ativa"] = df["status"] == "Ativa"

        parquet_path = self.processed_dir / "marketing.parquet"
        df.to_parquet(parquet_path, index=False)
        return df

    def process_estoque(self) -> pd.DataFrame:
        raw_path = self._resolve_raw_path("estoque")
        df = pd.read_csv(raw_path)

        # Padronização de strings (remoção de espaços nas extremidades)
        df = self._strip_strings(df)

        # Padroniza tipos de dados
        df["data_ultima_entrada"] = pd.to_datetime(df["data_ultima_entrada"], errors="coerce")

        # Padroniza colunas numéricas
        num_cols = [
            "lead_time_reposicao", "custo_unitario", "preco_venda_sugerido",
            "estoque_fisico", "estoque_reservado", "estoque_disponivel",
            "ponto_pedido", "shelf_life_dias", "volume_m3"
        ]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Calcula métricas adicionais
        df["is_ruptura_real"] = df["estoque_disponivel"] == 0
        df["is_estoque_critico"] = (df["estoque_disponivel"] > 0) & (df["estoque_disponivel"] <= df["ponto_pedido"])
        df["precisa_reposicao"] = df["is_ruptura_real"] | df["is_estoque_critico"]
        df["em_ruptura"] = df["is_ruptura_real"]
        df["margem_unitaria_sugerida"] = df["preco_venda_sugerido"] - df["custo_unitario"]
        df["markup_sugerido_pct"] = np.where(df["custo_unitario"] > 0, (df["margem_unitaria_sugerida"] / df["custo_unitario"]) * 100.0, 0.0)
        df["valor_total_estoque"] = df["estoque_disponivel"] * df["custo_unitario"]
        df["is_descontinuado"] = df["status_disponibilidade"] == "Descontinuado"
        df["capital_travado_descontinuado"] = np.where(df["status_disponibilidade"] == "Descontinuado", df["valor_total_estoque"], 0.0)
        df["capital_em_risco_ruptura"] = np.where(df["is_estoque_critico"], df["valor_total_estoque"], 0.0)

        parquet_path = self.processed_dir / "estoque.parquet"
        df.to_parquet(parquet_path, index=False)
        self.quality_report["estoque"] = {
            "rows": int(len(df)),
            "missing_sku": int(df["sku_id"].isna().sum()),
            "duplicate_sku": int(df["sku_id"].duplicated(keep=False).sum()),
            "missing_operational_balance": int(
                df[["estoque_fisico", "estoque_reservado", "estoque_disponivel"]].isna().any(axis=1).sum()
            ),
        }
        self._save_quality_report()
        return df

    def process_clientes(self) -> pd.DataFrame:
        raw_path = self._resolve_raw_path("clientes")
        df = pd.read_csv(raw_path)

        # Padronização de strings (remoção de espaços nas extremidades)
        df = self._strip_strings(df)

        # Padroniza tipos de dados
        df["data_cadastro"] = pd.to_datetime(df["data_cadastro"], errors="coerce")
        df["data_nascimento"] = pd.to_datetime(df["data_nascimento"], errors="coerce")

        # Padroniza colunas numéricas   
        num_cols = ["renda_estimada", "total_pedidos_historico", "ltv_acumulado"]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Calcula métricas adicionais
        ref_year = 2026
        df["idade"] = ref_year - df["data_nascimento"].dt.year
        df["opt_in_newsletter"] = df["opt_in_newsletter"].astype(str).str.upper() == "TRUE"
        df["ticket_medio_historico"] = np.where(df["total_pedidos_historico"] > 0, df["ltv_acumulado"] / df["total_pedidos_historico"], 0.0)
        df["dias_desde_cadastro"] = (pd.to_datetime("2026-01-01") - df["data_cadastro"]).dt.days

        parquet_path = self.processed_dir / "clientes.parquet"
        df.to_parquet(parquet_path, index=False)
        return df

    def process_atendimento(self) -> pd.DataFrame:
        raw_path = self._resolve_raw_path("atendimento")
        df = pd.read_csv(raw_path)

        # Remove registro com dados faltantes (linha com id 'TKT')
        id_linha = "TKT"
        df = df[df["ticket_id"].astype(str).str.strip().str.upper() != id_linha].copy()

        # Padronização de strings (remoção de espaços nas extremidades)
        df = self._strip_strings(df)

        # Padroniza tipos de dados
        df["data_abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
        df["data_fechamento"] = pd.to_datetime(df["data_fechamento"], errors="coerce")

        # Padroniza colunas numéricas
        num_cols = ["nota_csat", "tempo_primeira_resposta_minutos", "custo_operacional_ticket"]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Calcula métricas adicionais
        df["tempo_resolucao_horas"] = (df["data_fechamento"] - df["data_abertura"]).dt.total_seconds() / 3600.0
        df["tempo_resolucao_horas"] = df["tempo_resolucao_horas"].clip(lower=0.0)
        df["csat_critico"] = df["nota_csat"] <= 2.0
        df["is_automatizavel"] = df["categoria_problema"].isin(["Onde está meu pedido?", "Dúvida Técnica"])
        df["custo_evitavel_automacao"] = np.where(df["is_automatizavel"], df["custo_operacional_ticket"], 0.0)
        df["sla_resposta_estourado"] = df["tempo_primeira_resposta_minutos"] > 60.0

        parquet_path = self.processed_dir / "atendimento.parquet"
        df.to_parquet(parquet_path, index=False)
        return df

    def run_all(self) -> Dict[str, pd.DataFrame]:
        """Executa o pipeline completo de saneamento e gera os arquivos Parquet."""
        print("Iniciando pipeline de pré-processamento...")
        data = {
            "vendas": self.process_vendas(),
            "marketing": self.process_marketing(),
            "estoque": self.process_estoque(),
            "clientes": self.process_clientes(),
            "atendimento": self.process_atendimento(),
        }
        print("Tabelas Parquet geradas com sucesso.")
        return data


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.run_all()
