"""
app/views/v_09_dispersao_outliers.py
Diagnóstico de Dispersão & Detecção de Outliers (Boxplots).
Visualização simplificada de dispersão, quartis e anomalias estatísticas (método Tukey / IQR).
"""

from typing import Dict, Any
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.infrastructure.database import DuckDBRepository


TABLE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Vendas": {
        "table": "vendas",
        "default_metric": "margem_pct",
        "default_cat": "canal",
        "default_where": "status_pagamento = 'Aprovado'",
        "metrics": {
            "margem_pct": {"label": "Margem de Contribuição (%)", "format": "{:.1f}%", "is_pct": True},
            "margem_calculada": {"label": "Margem de Contribuição (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "receita_liquida": {"label": "Receita Líquida (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "desconto_pct": {"label": "Percentual de Desconto (%)", "format": "{:.1f}%", "is_pct": True},
            "custo_frete": {"label": "Custo de Frete (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "custo_produto": {"label": "Custo do Produto CMV (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "tempo_entrega_real": {"label": "Tempo de Entrega Real (Dias)", "format": "{:.1f} dias", "is_pct": False},
            "quantidade": {"label": "Quantidade de Itens", "format": "{:.0f}", "is_pct": False},
        },
        "dimensions": {
            "canal": "Canal de Venda",
            "categoria": "Categoria",
            "metodo_pagamento": "Método de Pagamento",
            "devolvido": "Devolvido (Sim/Não)",
        },
        "sample_cols": ["order_id", "data_pedido", "canal", "categoria", "produto", "receita_liquida", "margem_calculada", "margem_pct", "desconto_pct", "tempo_entrega_real", "devolvido"]
    },
    "Estoque": {
        "table": "estoque",
        "default_metric": "valor_total_estoque",
        "default_cat": "categoria",
        "default_where": "",
        "metrics": {
            "valor_total_estoque": {"label": "Capital em Estoque (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "lead_time_reposicao": {"label": "Lead Time de Reposição (Dias)", "format": "{:.0f} dias", "is_pct": False},
            "custo_unitario": {"label": "Custo Unitário (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "preco_venda_sugerido": {"label": "Preço de Venda Sugerido (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "estoque_disponivel": {"label": "Estoque Disponível (Unidades)", "format": "{:,.0f}", "is_pct": False},
            "shelf_life_dias": {"label": "Shelf Life (Dias)", "format": "{:.0f} dias", "is_pct": False},
        },
        "dimensions": {
            "categoria": "Categoria",
            "subcategoria": "Subcategoria",
            "status_disponibilidade": "Status de Disponibilidade",
            "em_ruptura": "Em Ruptura (Sim/Não)",
        },
        "sample_cols": ["sku_id", "nome_produto", "categoria", "subcategoria", "status_disponibilidade", "estoque_disponivel", "custo_unitario", "valor_total_estoque", "lead_time_reposicao"]
    },
    "Clientes": {
        "table": "clientes",
        "default_metric": "ltv_acumulado",
        "default_cat": "segmento_rfm",
        "default_where": "",
        "metrics": {
            "ltv_acumulado": {"label": "LTV Acumulado (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "ticket_medio_historico": {"label": "Ticket Médio Histórico (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "renda_estimada": {"label": "Renda Estimada (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "total_pedidos_historico": {"label": "Total de Pedidos Histórico", "format": "{:.0f}", "is_pct": False},
            "idade": {"label": "Idade (Anos)", "format": "{:.0f} anos", "is_pct": False},
        },
        "dimensions": {
            "segmento_rfm": "Segmento RFM",
            "nivel_fidelidade": "Nível de Fidelidade",
            "estado": "Estado (UF)",
            "genero": "Gênero",
        },
        "sample_cols": ["customer_id", "nome_completo", "segmento_rfm", "nivel_fidelidade", "estado", "ltv_acumulado", "ticket_medio_historico", "total_pedidos_historico", "renda_estimada"]
    },
    "Marketing": {
        "table": "marketing",
        "default_metric": "cac",
        "default_cat": "canal",
        "default_where": "",
        "metrics": {
            "cac": {"label": "CAC - Custo de Aquisição (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "roas": {"label": "ROAS (Retorno)", "format": "{:.2f}x", "is_pct": False},
            "cpc_reais": {"label": "CPC - Custo por Clique (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "taxa_conversao_pct": {"label": "Taxa de Conversão (%)", "format": "{:.2f}%", "is_pct": True},
            "investimento_reais": {"label": "Investimento (R$)", "format": "R$ {:,.2f}", "is_pct": False},
            "receita_gerada": {"label": "Receita Gerada (R$)", "format": "R$ {:,.2f}", "is_pct": False},
        },
        "dimensions": {
            "canal": "Canal de Mídia",
            "categoria_foco": "Categoria Foco",
            "status": "Status",
        },
        "sample_cols": ["campanha_id", "nome_campanha", "canal", "categoria_foco", "investimento_reais", "receita_gerada", "roas", "cac", "cpc_reais"]
    },
    "Atendimento": {
        "table": "atendimento",
        "default_metric": "tempo_resolucao_horas",
        "default_cat": "categoria_problema",
        "default_where": "status_atendimento = 'Resolvido'",
        "metrics": {
            "tempo_resolucao_horas": {"label": "Tempo de Resolução (Horas)", "format": "{:.1f}h", "is_pct": False},
            "tempo_primeira_resposta_minutos": {"label": "Tempo 1ª Resposta (Minutos)", "format": "{:.1f} min", "is_pct": False},
            "nota_csat": {"label": "Nota CSAT (1 a 5)", "format": "{:.2f}", "is_pct": False},
            "custo_operacional_ticket": {"label": "Custo por Ticket (R$)", "format": "R$ {:,.2f}", "is_pct": False},
        },
        "dimensions": {
            "categoria_problema": "Categoria do Problema",
            "canal_entrada": "Canal de Entrada",
            "status_atendimento": "Status do Chamado",
        },
        "sample_cols": ["ticket_id", "canal_entrada", "categoria_problema", "status_atendimento", "nota_csat", "tempo_primeira_resposta_minutos", "tempo_resolucao_horas", "custo_operacional_ticket"]
    }
}


def calculate_iqr_stats(series: pd.Series, k: float = 1.5) -> Dict[str, Any]:
    """Calcula quartis e limites de Tukey (IQR)."""
    s = series.dropna()
    if s.empty:
        return {
            "n": 0, "mean": 0.0, "min": 0.0, "q1": 0.0, "median": 0.0,
            "q3": 0.0, "max": 0.0, "iqr": 0.0, "lower_bound": 0.0, "upper_bound": 0.0,
            "outliers_low_count": 0, "outliers_high_count": 0, "total_outliers": 0, "outlier_pct": 0.0
        }
    
    q1 = float(np.percentile(s, 25))
    q3 = float(np.percentile(s, 75))
    iqr = q3 - q1
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    
    outliers_low = s[s < lower_bound]
    outliers_high = s[s > upper_bound]
    total_outliers = len(outliers_low) + len(outliers_high)
    
    return {
        "n": len(s),
        "mean": float(s.mean()),
        "min": float(s.min()),
        "q1": q1,
        "median": float(s.median()),
        "q3": q3,
        "max": float(s.max()),
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outliers_low_count": len(outliers_low),
        "outliers_high_count": len(outliers_high),
        "total_outliers": total_outliers,
        "outlier_pct": (total_outliers / len(s) * 100.0) if len(s) > 0 else 0.0,
    }


def show_dispersao_outliers(repo: DuckDBRepository):
    """Página simplificada e direta de Boxplots & Análise de Outliers."""
    st.markdown('<div class="page-title">Dispersão & Outliers</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Análise estatística de dispersão e identificação de anomalias por base de dados.</div>', unsafe_allow_html=True)

    # 1. Controles Principais (Seleção Direta)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        base_choice = st.selectbox("1. Base de Dados:", list(TABLE_CONFIGS.keys()), index=0, key="box_base")
        cfg = TABLE_CONFIGS[base_choice]

    with c2:
        metric_keys = list(cfg["metrics"].keys())
        metric_labels = [cfg["metrics"][m]["label"] for m in metric_keys]
        default_m_idx = metric_keys.index(cfg["default_metric"]) if cfg["default_metric"] in metric_keys else 0
        metric_sel = st.selectbox("2. Métrica (Eixo Y):", metric_labels, index=default_m_idx, key="box_metric")
        metric_key = metric_keys[metric_labels.index(metric_sel)]
        metric_meta = cfg["metrics"][metric_key]

    with c3:
        dim_keys = ["_none_"] + list(cfg["dimensions"].keys())
        dim_labels = ["Consolidado (Sem quebra)"] + [cfg["dimensions"][d] for d in cfg["dimensions"].keys()]
        default_d_idx = 1 if len(dim_keys) > 1 else 0
        dim_sel = st.selectbox("3. Quebra (Eixo X):", dim_labels, index=default_d_idx, key="box_dim")
        dim_key = dim_keys[dim_labels.index(dim_sel)]

    with c4:
        iqr_k = st.selectbox("4. Limite IQR:", [1.5, 3.0], format_func=lambda x: "1.5x (Tukey)" if x == 1.5 else "3.0x (Extremos)", index=0, key="box_iqr")

    # 2. Consulta de Dados
    where_sql = f"WHERE {cfg['default_where']}" if cfg['default_where'] else ""
    df = repo.execute_sql(f"SELECT * FROM {cfg['table']} {where_sql};")

    if df.empty or metric_key not in df.columns:
        st.info("Nenhum dado encontrado para a seleção atual.")
        return

    # 3. Estatísticas e Classificação
    stats = calculate_iqr_stats(df[metric_key], k=iqr_k)
    low_b, up_b = stats["lower_bound"], stats["upper_bound"]
    
    df["status_outlier"] = df[metric_key].apply(
        lambda v: "Inferior" if v < low_b else ("Superior" if v > up_b else "Normal")
    )
    df_out = df[df["status_outlier"] != "Normal"].copy()

    # 4. Métricas Rápidas
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registros Analisados", f"{stats['n']:,}")
    
    med_str = metric_meta["format"].format(stats["median"])
    avg_str = metric_meta["format"].format(stats["mean"])
    m2.metric("Mediana", med_str, f"Média: {avg_str}")
    
    low_str = metric_meta["format"].format(low_b)
    up_str = metric_meta["format"].format(up_b)
    m3.metric("Limites Normais (Cercas)", f"[{low_str} a {up_str}]", f"IQR: {metric_meta['format'].format(stats['iqr'])}")
    
    m4.metric("Outliers Detectados", f"{stats['total_outliers']:,} ({stats['outlier_pct']:.1f}%)", f"↓ {stats['outliers_low_count']} inf. | ↑ {stats['outliers_high_count']} sup.")

    # 5. Gráfico Boxplot
    st.markdown("---")
    chart_title = f"{metric_meta['label']}" + (f" por {cfg['dimensions'].get(dim_key, dim_key)}" if dim_key != "_none_" else " (Consolidado)")
    
    if dim_key == "_none_":
        fig = px.box(
            df,
            y=metric_key,
            points="outliers",
            title=chart_title,
            labels={metric_key: metric_meta["label"]},
            color_discrete_sequence=["#38BDF8"]
        )
    else:
        fig = px.box(
            df,
            x=dim_key,
            y=metric_key,
            color=dim_key,
            points="outliers",
            title=chart_title,
            labels={metric_key: metric_meta["label"], dim_key: cfg["dimensions"].get(dim_key, dim_key)},
        )
        fig.update_layout(showlegend=False)

    fig.add_hline(
        y=stats["median"],
        line_dash="dot",
        line_color="#F59E0B",
        annotation_text=f"Mediana: {med_str}",
        annotation_position="top left"
    )
    fig.update_layout(height=420, margin=dict(l=40, r=20, t=40, b=30))
    st.plotly_chart(fig, use_container_width=True)

    # 6. Tabela Simples de Outliers
    st.subheader(f"📋 Registros Fora da Curva ({len(df_out):,})")
    if df_out.empty:
        st.success("Nenhum outlier encontrado para os parâmetros selecionados.")
    else:
        cols_to_show = [c for c in cfg["sample_cols"] if c in df.columns]
        if metric_key not in cols_to_show:
            cols_to_show.append(metric_key)
        cols_to_show.append("status_outlier")
        
        df_out_sorted = df_out.sort_values(by=metric_key, ascending=False)
        st.dataframe(df_out_sorted[cols_to_show].head(100), use_container_width=True)
        
        csv_data = df_out_sorted.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Baixar Lista de Outliers (CSV)",
            csv_data,
            f"outliers_{base_choice}_{metric_key}.csv",
            "text/csv",
            key="btn_download_outliers"
        )
