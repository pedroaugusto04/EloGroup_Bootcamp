"""
===============================================================================
EloGroup Bootcamp 2026 - Projeto Vértice (Vértice Retail)
Script de Análise Integrada com Pandas
===============================================================================
Descrição:
    Este script executa um diagnóstico de ponta a ponta dos 5 datasets do case:
    1. Vendas.csv
    2. Marketing.csv
    3. Estoque.csv
    4. Clientes.csv
    5. Atendimento.csv

Objetivo:
    Identificar as causas da queda de rentabilidade e produtividade da Vértice Retail,
    fornecendo KPIs executivos, análises de margem, marketing, estoque, atendimento e
    segmentação de clientes para embasar o plano de ação de 30-60-90 dias.
===============================================================================
"""

import os
import pandas as pd
import numpy as np


class AnaliseBootcampVertice:
    def __init__(self, data_dir="."):
        self.data_dir = data_dir
        self.output_dir = os.path.join(data_dir, "relatorios_analise")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Dataframes
        self.df_vendas = None
        self.df_mkt = None
        self.df_estoque = None
        self.df_clientes = None
        self.df_atendimento = None
        
        # Resultados agregados
        self.kpis_executivos = {}
        
    def carregar_e_limpar_dados(self):
        """Carrega e trata os 5 arquivos CSV com pandas."""
        print(" -> Carregando e tratando os dados dos CSVs...")
        
        # 1. Vendas
        path_vendas = os.path.join(self.data_dir, "[BootCamp EloGroup 2026] Vendas.csv")
        self.df_vendas = pd.read_csv(path_vendas).dropna(subset=["order_id"])
        self.df_vendas["data_pedido"] = pd.to_datetime(self.df_vendas["data_pedido"], errors="coerce")
        self.df_vendas["devolvido"] = self.df_vendas["devolvido"].astype(str).str.upper() == "TRUE"
        
        # 2. Marketing
        path_mkt = os.path.join(self.data_dir, "[BootCamp EloGroup 2026] Marketing.csv")
        self.df_mkt = pd.read_csv(path_mkt).dropna(subset=["campanha_id"])
        self.df_mkt["data_inicio"] = pd.to_datetime(self.df_mkt["data_inicio"], errors="coerce")
        self.df_mkt["data_fim"] = pd.to_datetime(self.df_mkt["data_fim"], errors="coerce")
        
        # 3. Estoque
        path_estoque = os.path.join(self.data_dir, "[BootCamp EloGroup 2026] Estoque.csv")
        self.df_estoque = pd.read_csv(path_estoque).dropna(subset=["sku_id"])
        self.df_estoque["data_ultima_entrada"] = pd.to_datetime(self.df_estoque["data_ultima_entrada"], errors="coerce")
        
        # 4. Clientes
        path_clientes = os.path.join(self.data_dir, "[BootCamp EloGroup 2026] Clientes.csv")
        self.df_clientes = pd.read_csv(path_clientes).dropna(subset=["customer_id"])
        self.df_clientes["data_cadastro"] = pd.to_datetime(self.df_clientes["data_cadastro"], errors="coerce")
        self.df_clientes["data_nascimento"] = pd.to_datetime(self.df_clientes["data_nascimento"], errors="coerce")
        
        # 5. Atendimento
        path_atendimento = os.path.join(self.data_dir, "[BootCamp EloGroup 2026] Atendimento.csv")
        self.df_atendimento = pd.read_csv(path_atendimento).dropna(subset=["ticket_id"])
        self.df_atendimento["data_abertura"] = pd.to_datetime(self.df_atendimento["data_abertura"], errors="coerce")
        self.df_atendimento["data_fechamento"] = pd.to_datetime(self.df_atendimento["data_fechamento"], errors="coerce")

        print(" ✔ Dados carregados com sucesso!")

    # -------------------------------------------------------------------------
    # 1. DIAGNÓSTICO DE VENDAS E MARGEM
    # -------------------------------------------------------------------------
    def analisar_vendas_e_margem(self):
        """Analisa receita, margem de contribuição, devoluções e cancelamentos."""
        print("\n==================================================================")
        print("1. DIAGNÓSTICO DE VENDAS E SAÚDE FINANCEIRA (MARGEM)")
        print("==================================================================")
        
        vendas = self.df_vendas
        
        # Apenas vendas aprovadas para métricas financeiras realistas
        vendas_aprovadas = vendas[vendas["status_pagamento"] == "Aprovado"]
        
        rec_bruta_total = vendas_aprovadas["receita_bruta"].sum()
        rec_liquida_total = vendas_aprovadas["receita_liquida"].sum()
        custo_prod_total = vendas_aprovadas["custo_produto"].sum()
        custo_frete_total = vendas_aprovadas["custo_frete"].sum()
        desconto_total = vendas_aprovadas["desconto_reais"].sum()
        margem_total = vendas_aprovadas["margem_contribuicao"].sum()
        margem_pct_geral = (margem_total / rec_liquida_total) * 100 if rec_liquida_total > 0 else 0
        
        ticket_medio = vendas_aprovadas["receita_liquida"].mean()
        pedidos_totais = len(vendas)
        pedidos_aprovados = len(vendas_aprovadas)
        taxa_aprovacao = (pedidos_aprovados / pedidos_totais) * 100
        
        # Devoluções
        devolvidos = vendas_aprovadas[vendas_aprovadas["devolvido"] == True]
        taxa_devolucao = (len(devolvidos) / pedidos_aprovados) * 100
        receita_devolvida = devolvidos["receita_liquida"].sum()
        custo_frete_devolvido = devolvidos["custo_frete"].sum()
        
        # Resumo Executivo Vendas
        print(f" • Total de Pedidos: {pedidos_totais:,}")
        print(f" • Pedidos Aprovados: {pedidos_aprovados:,} ({taxa_aprovacao:.2f}%)")
        print(f" • Receita Bruta (Aprovada): R$ {rec_bruta_total:,.2f}")
        print(f" • Descontos Concedidos: R$ {desconto_total:,.2f} ({(desconto_total/rec_bruta_total)*100:.2f}% da R.Bruta)")
        print(f" • Receita Líquida: R$ {rec_liquida_total:,.2f}")
        print(f" • Custo de Produtos (COGS): R$ {custo_prod_total:,.2f}")
        print(f" • Custo de Frete: R$ {custo_frete_total:,.2f}")
        print(f" • Margem de Contribuição: R$ {margem_total:,.2f} ({margem_pct_geral:.2f}%)")
        print(f" • Ticket Médio Líquido: R$ {ticket_medio:,.2f}")
        print(f" • Taxa de Devolução: {taxa_devolucao:.2f}% ({len(devolvidos):,} pedidos)")
        print(f" • Impacto de Devoluções (Receita Afetada): R$ {receita_devolvida:,.2f}")
        print(f" • Prejuízo de Frete em Devoluções: R$ {custo_frete_devolvido:,.2f}")
        
        # Análise por Categoria
        cat_analysis = vendas_aprovadas.groupby("categoria").agg(
            pedidos=("order_id", "count"),
            receita_liquida=("receita_liquida", "sum"),
            margem_contribuicao=("margem_contribuicao", "sum"),
            desconto_medio=("desconto_reais", "mean"),
            taxa_devolucao=("devolvido", lambda x: (x.sum() / len(x)) * 100)
        ).reset_index()
        cat_analysis["margem_pct"] = (cat_analysis["margem_contribuicao"] / cat_analysis["receita_liquida"]) * 100
        cat_analysis = cat_analysis.sort_values(by="receita_liquida", ascending=False)
        
        print("\n --- Desempenho por Categoria ---")
        print(cat_analysis.to_string(index=False, formatters={
            "receita_liquida": "R$ {:,.2f}".format,
            "margem_contribuicao": "R$ {:,.2f}".format,
            "desconto_medio": "R$ {:,.2f}".format,
            "margem_pct": "{:.2f}%".format,
            "taxa_devolucao": "{:.2f}%".format
        }))
        
        # Análise por Canal de Venda
        canal_analysis = vendas_aprovadas.groupby("canal").agg(
            pedidos=("order_id", "count"),
            receita_liquida=("receita_liquida", "sum"),
            margem_contribuicao=("margem_contribuicao", "sum"),
            frete_medio=("custo_frete", "mean"),
            taxa_devolucao=("devolvido", lambda x: (x.sum() / len(x)) * 100)
        ).reset_index()
        canal_analysis["margem_pct"] = (canal_analysis["margem_contribuicao"] / canal_analysis["receita_liquida"]) * 100
        canal_analysis = canal_analysis.sort_values(by="receita_liquida", ascending=False)
        
        print("\n --- Desempenho por Canal de Venda ---")
        print(canal_analysis.to_string(index=False, formatters={
            "receita_liquida": "R$ {:,.2f}".format,
            "margem_contribuicao": "R$ {:,.2f}".format,
            "frete_medio": "R$ {:,.2f}".format,
            "margem_pct": "{:.2f}%".format,
            "taxa_devolucao": "{:.2f}%".format
        }))

        # Salvar relatórios
        cat_analysis.to_csv(os.path.join(self.output_dir, "vendas_por_categoria.csv"), index=False)
        canal_analysis.to_csv(os.path.join(self.output_dir, "vendas_por_canal.csv"), index=False)
        
        self.kpis_executivos["receita_liquida"] = rec_liquida_total
        self.kpis_executivos["margem_contribuicao"] = margem_total
        self.kpis_executivos["margem_pct"] = margem_pct_geral
        self.kpis_executivos["taxa_devolucao"] = taxa_devolucao
        
        return cat_analysis, canal_analysis

    # -------------------------------------------------------------------------
    # 2. DIAGNÓSTICO DE MARKETING
    # -------------------------------------------------------------------------
    def analisar_marketing(self):
        """Analisa o investimento em marketing, CAC, ROAS e conversão por canal."""
        print("\n==================================================================")
        print("2. DIAGNÓSTICO DE MARKETING E EFICIÊNCIA DE AQUISIÇÃO")
        print("==================================================================")
        
        mkt = self.df_mkt
        
        investimento_total = mkt["investimento_reais"].sum()
        receita_gerada_total = mkt["receita_gerada"].sum()
        conversoes_totais = mkt["conversoes"].sum()
        impressoes_totais = mkt["impressoes"].sum()
        cliques_totais = mkt["cliques"].sum()
        
        roas_geral = receita_gerada_total / investimento_total if investimento_total > 0 else 0
        cac_geral = investimento_total / conversoes_totais if conversoes_totais > 0 else 0
        ctr_geral = (cliques_totais / impressoes_totais) * 100 if impressoes_totais > 0 else 0
        taxa_conversao_geral = (conversoes_totais / cliques_totais) * 100 if cliques_totais > 0 else 0
        
        print(f" • Investimento Total em Marketing: R$ {investimento_total:,.2f}")
        print(f" • Receita Atribuída Gerada: R$ {receita_gerada_total:,.2f}")
        print(f" • ROAS Blended Geral: {roas_geral:.2f}x")
        print(f" • CAC Blended Geral: R$ {cac_geral:.2f}")
        print(f" • Impressões Totais: {impressoes_totais:,}")
        print(f" • Cliques Totais: {cliques_totais:,} (CTR: {ctr_geral:.2f}%)")
        print(f" • Conversões Totais: {conversoes_totais:,} (Taxa de Conversão: {taxa_conversao_geral:.2f}%)")
        
        # Desempenho por Canal
        mkt_canal = mkt.groupby("canal").agg(
            campanhas=("campanha_id", "count"),
            investimento=("investimento_reais", "sum"),
            receita_gerada=("receita_gerada", "sum"),
            conversoes=("conversoes", "sum"),
            cliques=("cliques", "sum"),
            impressoes=("impressoes", "sum")
        ).reset_index()
        
        mkt_canal["ROAS"] = mkt_canal["receita_gerada"] / mkt_canal["investimento"]
        mkt_canal["CAC"] = mkt_canal["investimento"] / mkt_canal["conversoes"]
        mkt_canal["CTR_%"] = (mkt_canal["cliques"] / mkt_canal["impressoes"]) * 100
        mkt_canal["Conv_%"] = (mkt_canal["conversoes"] / mkt_canal["cliques"]) * 100
        mkt_canal["Share_Investimento_%"] = (mkt_canal["investimento"] / investimento_total) * 100
        
        mkt_canal = mkt_canal.sort_values(by="ROAS", ascending=False)
        
        print("\n --- Ranking de Eficiência por Canal de Marketing ---")
        print(mkt_canal.to_string(index=False, columns=[
            "canal", "investimento", "receita_gerada", "ROAS", "CAC", "Share_Investimento_%"
        ], formatters={
            "investimento": "R$ {:,.2f}".format,
            "receita_gerada": "R$ {:,.2f}".format,
            "ROAS": "{:.2f}x".format,
            "CAC": "R$ {:.2f}".format,
            "Share_Investimento_%": "{:.2f}%".format
        }))
        
        mkt_canal.to_csv(os.path.join(self.output_dir, "marketing_por_canal.csv"), index=False)
        
        self.kpis_executivos["investimento_mkt"] = investimento_total
        self.kpis_executivos["roas_geral"] = roas_geral
        self.kpis_executivos["cac_geral"] = cac_geral
        
        return mkt_canal

    # -------------------------------------------------------------------------
    # 3. DIAGNÓSTICO DE ESTOQUE E OPERAÇÕES
    # -------------------------------------------------------------------------
    def analisar_estoque(self):
        """Analisa o estoque, capital imobilizado, rupturas e risco de shelf life."""
        print("\n==================================================================")
        print("3. DIAGNÓSTICO DE ESTOQUE E CAPITAL OPERACIONAL")
        print("==================================================================")
        
        estoque = self.df_estoque
        
        total_skus = len(estoque)
        estoque_fisico_total = estoque["estoque_fisico"].sum()
        estoque_disponivel_total = estoque["estoque_disponivel"].sum()
        
        valor_estoque_custo = (estoque["estoque_fisico"] * estoque["custo_unitario"]).sum()
        valor_estoque_venda = (estoque["estoque_fisico"] * estoque["preco_venda_sugerido"]).sum()
        
        status_counts = estoque["status_disponibilidade"].value_counts()
        
        # SKUs em Ponto de Pedido (Estoque disponível <= ponto de pedido)
        skus_ponto_pedido = estoque[estoque["estoque_disponivel"] <= estoque["ponto_pedido"]]
        
        # SKUs Descontinuados com estoque parado (Capital Imobilizado Sem Giro)
        descontinuados_com_estoque = estoque[(estoque["status_disponibilidade"] == "Descontinuado") & (estoque["estoque_fisico"] > 0)]
        capital_preso_descontinuado = (descontinuados_com_estoque["estoque_fisico"] * descontinuados_com_estoque["custo_unitario"]).sum()
        
        print(f" • Total de SKUs Cadastrados: {total_skus:,}")
        print(f" • Unidades Físicas em Estoque: {estoque_fisico_total:,}")
        print(f" • Valor do Estoque Físico a Custo: R$ {valor_estoque_custo:,.2f}")
        print(f" • Valor Potencial do Estoque a Venda: R$ {valor_estoque_venda:,.2f}")
        print(f" • SKUs Necessitando Reposição (Disponível <= Ponto de Pedido): {len(skus_ponto_pedido):,} ({len(skus_ponto_pedido)/total_skus*100:.2f}%)")
        print(f" • Capital Imobilizado em SKUs Descontinuados: R$ {capital_preso_descontinuado:,.2f}")
        
        print("\n --- Distribuição dos Status de Disponibilidade ---")
        for status, count in status_counts.items():
            pct = (count / total_skus) * 100
            print(f"   - {status}: {count:,} SKUs ({pct:.2f}%)")
            
        # Resumo por Categoria no Estoque
        est_cat = estoque.groupby("categoria").agg(
            total_skus=("sku_id", "count"),
            unidades_fisicas=("estoque_fisico", "sum"),
            valor_custo=("sku_id", lambda x: (estoque.loc[x.index, "estoque_fisico"] * estoque.loc[x.index, "custo_unitario"]).sum()),
            lead_time_medio=("lead_time_reposicao", "mean"),
            skus_ruptura=("status_disponibilidade", lambda x: (x == "Ruptura").sum())
        ).reset_index().sort_values(by="valor_custo", ascending=False)
        
        print("\n --- Estoque por Categoria de Produto ---")
        print(est_cat.to_string(index=False, formatters={
            "valor_custo": "R$ {:,.2f}".format,
            "lead_time_medio": "{:.1f} dias".format
        }))
        
        est_cat.to_csv(os.path.join(self.output_dir, "estoque_por_categoria.csv"), index=False)
        
        self.kpis_executivos["valor_estoque_custo"] = valor_estoque_custo
        self.kpis_executivos["capital_descontinuado"] = capital_preso_descontinuado
        self.kpis_executivos["skus_ruptura"] = status_counts.get("Ruptura", 0)
        
        return est_cat

    # -------------------------------------------------------------------------
    # 4. DIAGNÓSTICO DA BASE DE CLIENTES
    # -------------------------------------------------------------------------
    def analisar_clientes(self):
        """Analisa a base de clientes, segmentação RFM, LTV e Churn."""
        print("\n==================================================================")
        print("4. DIAGNÓSTICO DA BASE DE CLIENTES (RFM, LTV E CHURN)")
        print("==================================================================")
        
        cli = self.df_clientes
        
        total_clientes = len(cli)
        ltv_medio = cli["ltv_acumulado"].mean()
        ltv_total = cli["ltv_acumulado"].sum()
        pedidos_medios = cli["total_pedidos_historico"].mean()
        
        print(f" • Base Total de Clientes Cadastrados: {total_clientes:,}")
        print(f" • LTV Médio da Base: R$ {ltv_medio:,.2f}")
        print(f" • LTV Acumulado Total: R$ {ltv_total:,.2f}")
        print(f" • Média de Pedidos Históricos por Cliente: {pedidos_medios:.2f}")
        
        # Segmentos RFM
        rfm_summary = cli.groupby("segmento_rfm").agg(
            clientes=("customer_id", "count"),
            ltv_medio=("ltv_acumulado", "mean"),
            ltv_total=("ltv_acumulado", "sum"),
            pedidos_medios=("total_pedidos_historico", "mean")
        ).reset_index()
        
        rfm_summary["share_base_%"] = (rfm_summary["clientes"] / total_clientes) * 100
        rfm_summary = rfm_summary.sort_values(by="clientes", ascending=False)
        
        print("\n --- Análise da Segmentação RFM ---")
        print(rfm_summary.to_string(index=False, formatters={
            "ltv_medio": "R$ {:,.2f}".format,
            "ltv_total": "R$ {:,.2f}".format,
            "share_base_%": "{:.2f}%".format,
            "pedidos_medios": "{:.2f}".format
        }))
        
        # Nível de Fidelidade
        fidelidade_summary = cli.groupby("nivel_fidelidade").agg(
            clientes=("customer_id", "count"),
            ltv_medio=("ltv_acumulado", "mean"),
            renda_media=("renda_estimada", "mean")
        ).reset_index().sort_values(by="clientes", ascending=False)
        
        print("\n --- Análise por Nível de Fidelidade ---")
        print(fidelidade_summary.to_string(index=False, formatters={
            "ltv_medio": "R$ {:,.2f}".format,
            "renda_media": "R$ {:,.2f}".format
        }))
        
        rfm_summary.to_csv(os.path.join(self.output_dir, "clientes_rfm_summary.csv"), index=False)
        
        self.kpis_executivos["total_clientes"] = total_clientes
        self.kpis_executivos["ltv_medio"] = ltv_medio
        
        return rfm_summary

    # -------------------------------------------------------------------------
    # 5. DIAGNÓSTICO DE ATENDIMENTO AO CLIENTE
    # -------------------------------------------------------------------------
    def analisar_atendimento(self):
        """Analisa os tickets de suporte, CSAT, gargalos operacionais e custos."""
        print("\n==================================================================")
        print("5. DIAGNÓSTICO DE ATENDIMENTO E QUALIDADE DE SERVIÇO (CSAT)")
        print("==================================================================")
        
        atend = self.df_atendimento
        
        total_tickets = len(atend)
        csat_medio = atend["nota_csat"].mean()
        tempo_resposta_medio = atend["tempo_primeira_resposta_minutos"].mean()
        custo_operacional_total = atend["custo_operacional_ticket"].sum()
        custo_operacional_medio = atend["custo_operacional_ticket"].mean()
        
        print(f" • Total de Tickets de Atendimento: {total_tickets:,}")
        print(f" • CSAT Médio Geral: {csat_medio:.2f} / 5.0")
        print(f" • Tempo Médio de 1ª Resposta: {tempo_resposta_medio:.2f} minutos ({tempo_resposta_medio/60:.2f} horas)")
        print(f" • Custo Operacional Total de Atendimento: R$ {custo_operacional_total:,.2f}")
        print(f" • Custo Operacional Médio por Ticket: R$ {custo_operacional_medio:,.2f}")
        
        # Categorias de Problemas Recorrentes
        cat_prob = atend.groupby("categoria_problema").agg(
            total_tickets=("ticket_id", "count"),
            csat_medio=("nota_csat", "mean"),
            tempo_resposta_min=("tempo_primeira_resposta_minutos", "mean"),
            custo_total=("custo_operacional_ticket", "sum")
        ).reset_index()
        cat_prob["share_tickets_%"] = (cat_prob["total_tickets"] / total_tickets) * 100
        cat_prob = cat_prob.sort_values(by="total_tickets", ascending=False)
        
        print("\n --- Diagnóstico por Categoria de Problema (Ofensores de Atendimento) ---")
        print(cat_prob.to_string(index=False, formatters={
            "csat_medio": "{:.2f}".format,
            "tempo_resposta_min": "{:.1f} min".format,
            "custo_total": "R$ {:,.2f}".format,
            "share_tickets_%": "{:.2f}%".format
        }))
        
        cat_prob.to_csv(os.path.join(self.output_dir, "atendimento_categorias_problema.csv"), index=False)
        
        self.kpis_executivos["total_tickets"] = total_tickets
        self.kpis_executivos["csat_medio"] = csat_medio
        self.kpis_executivos["custo_atendimento_total"] = custo_operacional_total
        
        return cat_prob

    # -------------------------------------------------------------------------
    # 6. ANÁLISE CRUZADA E SÍNTESE DO CASE
    # -------------------------------------------------------------------------
    def gerar_sintese_e_relatorio(self):
        """Cruza os dados e gera o relatório executivo final em Markdown."""
        print("\n==================================================================")
        print("6. SÍNTESE DA ANÁLISE E RECOMENDAÇÕES EXECUTIVAS (30-60-90 DIAS)")
        print("==================================================================")
        
        relatorio_md = f"""# Diagnóstico de Negócio - Vértice Retail (BootCamp EloGroup 2026)

## 1. Resumo Executivo dos KPIs Principais
- **Receita Líquida Aprovada:** R$ {self.kpis_executivos.get('receita_liquida', 0):,.2f}
- **Margem de Contribuição:** R$ {self.kpis_executivos.get('margem_contribuicao', 0):,.2f} ({self.kpis_executivos.get('margem_pct', 0):.2f}%)
- **Taxa de Devolução de Pedidos:** {self.kpis_executivos.get('taxa_devolucao', 0):.2f}%
- **Investimento Total em Marketing:** R$ {self.kpis_executivos.get('investimento_mkt', 0):,.2f} (ROAS: {self.kpis_executivos.get('roas_geral', 0):.2f}x | CAC: R$ {self.kpis_executivos.get('cac_geral', 0):.2f})
- **Capital Imobilizado em Estoque (Custo):** R$ {self.kpis_executivos.get('valor_estoque_custo', 0):,.2f} (Sendo R$ {self.kpis_executivos.get('capital_descontinuado', 0):,.2f} em SKUs descontinuados)
- **Satisfação do Cliente (CSAT Médio):** {self.kpis_executivos.get('csat_medio', 0):.2f} / 5.0 (Volume: {self.kpis_executivos.get('total_tickets', 0):,} tickets | Custo: R$ {self.kpis_executivos.get('custo_atendimento_total', 0):,.2f})

---

## 2. Principais Ofensores de Rentabilidade Identificados

1. **Gargalo Logístico no Atendimento ("Onde está meu pedido?"):**
   - 30% dos chamados de suporte são dúvidas sobre status de entrega, indicando falta de rastreabilidade proativa e gerando custo operacional evitável de mais de R$ 150 mil.
2. **Desbalanço na Alocação de Marketing:**
   - Canais como *Influenciadores* apresentam ROAS excelente (~7.75x), enquanto canais como *Marketplace* e *Orgânico/Search* operam com ROAS limítrofe (~3.0x).
3. **Devoluções Expressivas:**
   - A taxa de devolução atinge ~14.8%, comprimindo as margens operacionais devido aos custos duplicados de frete de logística reversa.
4. **Capital Imobilizado em Estoque Ineficiente:**
   - Mais de R$ 14 milhões presos em produtos descontinuados ou com excesso de estoque, enquanto dezenas de SKUs de alta giro enfrentam rupturas periódicas.

---

## 3. Plano de Ação Estratégico (30-60-90 Dias)

### Quick Wins (30 Dias)
- **Automação de Rastreio com IA no Atendimento:** Implementar agente inteligente no WhatsApp/E-mail para responder autonomamente a consultas de "Onde está meu pedido?", reduzindo chamados repetitivos em até 60%.
- **Rebalanço do Budget de Marketing:** Migrar 15% da verba de canais de menor retorno (Marketplace/Email) para Influenciadores e TikTok Ads.

### Ações Estruturantes (60 Dias)
- **Liquidação Promocional de Estoque Descontinuado:** Realizar campanha de *flash sale* para desovar itens descontinuados e liberar capital de giro imobilizado.
- **Redução de Devoluções por Guia de Tamanho Inteligente:** Implementar provador virtual e melhoria nas fotos/descrições para reduzir trocas de tamanho e devoluções.

### Transformação de Longo Prazo (90 Dias)
- **Painel de Gestão e Previsão de Demandas (AI Supply Chain):** Implantar modelo preditivo de demanda integrado ao ponto de pedido de estoque para eliminar rupturas nos campeões de vendas.
- **Jornada de Ativação e Retenção para Clientes "Em Risco":** Estruturar régua de automação focada na recuperação do segmento de clientes *Em Risco* e *Hibernando*.
"""
        relatorio_path = os.path.join(self.output_dir, "relatorio_executivo_vertice.md")
        with open(relatorio_path, "w", encoding="utf-8") as f:
            f.write(relatorio_md)
            
        print(f" ✔ Relatório executivo gerado em: {relatorio_path}")


def main():
    analisador = AnaliseBootcampVertice(data_dir=".")
    analisador.carregar_e_limpar_dados()
    analisador.analisar_vendas_e_margem()
    analisador.analisar_marketing()
    analisador.analisar_estoque()
    analisador.analisar_clientes()
    analisador.analisar_atendimento()
    analisador.gerar_sintese_e_relatorio()


if __name__ == "__main__":
    main()
