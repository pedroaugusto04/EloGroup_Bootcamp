"""Gera os slides auxiliares auditados do case Vértice Retail."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Vértice-Slides-Auxiliares.pptx"

W = 13.333
H = 7.5

INK = RGBColor(55, 24, 62)
PURPLE = RGBColor(86, 18, 101)
MAGENTA = RGBColor(224, 0, 210)
BODY = RGBColor(93, 88, 96)
MUTED = RGBColor(130, 123, 133)
LAVENDER = RGBColor(247, 239, 250)
LAVENDER_2 = RGBColor(239, 224, 244)
LINE = RGBColor(222, 198, 228)
WHITE = RGBColor(255, 255, 255)


def add_text(slide, text, x, y, w, h, size=15, color=BODY, bold=False,
             font="Lato", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
             margin=0, line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(margin)
    frame.margin_top = frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    p = frame.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = font
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.line_spacing = line_spacing
    return box


def add_rect(slide, x, y, w, h, fill, radius=False, line=None):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    if radius:
        shape.adjustments[0] = 0.08
    return shape


def add_line(slide, x1, y1, x2, y2, color=LINE, width=1):
    line = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(width)
    return line


def add_header(slide, code, section):
    add_rect(slide, 0.60, 0.39, 0.28, 0.055, MAGENTA)
    add_text(slide, f"{code} / {section}", 1.00, 0.27, 7.4, 0.28,
             size=10.5, color=PURPLE, bold=True)
    add_text(slide, "VÉRTICE", 11.78, 0.27, 0.95, 0.28,
             size=10.5, color=INK, bold=True, align=PP_ALIGN.RIGHT)


def add_footer(slide, code):
    add_line(slide, 0.60, 6.92, 12.73, 6.92, LINE, 0.8)
    add_text(slide, code, 12.25, 7.02, 0.48, 0.22,
             size=9.5, color=INK, bold=True, align=PP_ALIGN.RIGHT)


def add_title(slide, text, y=0.82, size=27):
    return add_text(slide, text, 0.60, y, 12.0, 0.78,
                    size=size, color=INK, bold=True, line_spacing=0.95)


def add_label(slide, text, x, y, w):
    add_text(slide, text.upper(), x, y, w, 0.24, size=9.5,
             color=MAGENTA, bold=True)


def add_card(slide, x, y, w, h, title, value, body, accent=PURPLE):
    add_rect(slide, x, y, w, h, LAVENDER, radius=False)
    add_rect(slide, x, y, 0.06, h, accent)
    add_text(slide, title.upper(), x + 0.23, y + 0.20, w - 0.42, 0.25,
             size=9.5, color=MAGENTA, bold=True)
    add_text(slide, value, x + 0.23, y + 0.52, w - 0.42, 0.52,
             size=22, color=INK, bold=True)
    add_text(slide, body, x + 0.23, y + 1.13, w - 0.42, h - 1.28,
             size=11.5, color=BODY, line_spacing=1.05)


def slide_contract(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
    add_header(slide, "A1", "CONTRATO DOS DADOS")
    add_title(slide, "O número muda quando muda a fonte.")
    add_text(slide, "Antes de cruzar bases, fixe período, grão e definição financeira.",
             0.60, 1.55, 11.8, 0.36, size=15, color=BODY)

    add_card(slide, 0.60, 2.05, 2.92, 3.45, "Vendas · 391 dias", "R$ 14,17M",
             "Receita efetivamente retida.\n\nR$ 16,67M é receita nominal de pedidos aprovados, antes do estorno das devoluções.")
    add_card(slide, 3.66, 2.05, 2.92, 3.45, "Estoque · snapshot ausente", "99 + 701",
             "99 SKUs zerados e 701 no/abaixo do ponto de pedido.\n\nSaldo operacional é válido; a data da posição não foi fornecida.")
    add_card(slide, 6.72, 2.05, 2.92, 3.45, "Marketing · 2023–2025", "Sem ROAS real",
             "Não há campaign_id ou janela de atribuição nos pedidos.\n\nComparações por canal são exploratórias, não causais.")
    add_card(slide, 9.78, 2.05, 2.95, 3.45, "CRM + CX · baixa cobertura", "2,3%",
             "Só 346 de 15 mil clientes aparecem em Vendas.\n\n65,4% dos tickets citam pedidos fora do extrato disponível.")

    add_rect(slide, 0.60, 5.83, 12.13, 0.72, PURPLE)
    add_text(slide, "REGRA DE LEITURA", 0.85, 6.02, 1.52, 0.22,
             size=10, color=MAGENTA, bold=True)
    add_text(slide, "KPIs dentro de cada base são auditáveis; métricas cruzadas exigem cobertura explícita.",
             2.45, 5.96, 9.92, 0.32, size=14, color=WHITE, bold=True)
    add_footer(slide, "A1")


def slide_liquidation(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
    add_header(slide, "A2", "MEMÓRIA DE CÁLCULO · LIQUIDAÇÃO")
    add_title(slide, "Liquidação: cenário auditável, não promessa.")
    add_text(slide, "Cenário central · 206 de 207 SKUs valorados pelo custo histórico de Vendas",
             0.60, 1.55, 11.8, 0.36, size=14.5, color=BODY)

    steps = [
        ("SALDO DISPONÍVEL", "65.266 un.", "descontinuados"),
        ("SELL-THROUGH", "50%", "32.526 un."),
        ("DESCONTO", "30%", "sobre preço histórico"),
        ("DEVOLUÇÕES", "− R$ 720 mil", "ajuste por categoria"),
    ]
    x = 0.60
    for idx, (label, value, note) in enumerate(steps):
        add_rect(slide, x, 2.12, 2.42, 1.35, LAVENDER)
        add_text(slide, label, x + 0.18, 2.32, 2.06, 0.22, size=9, color=MAGENTA, bold=True)
        add_text(slide, value, x + 0.18, 2.62, 2.06, 0.35, size=19, color=INK, bold=True)
        add_text(slide, note, x + 0.18, 3.08, 2.06, 0.22, size=10.5, color=BODY)
        if idx < len(steps) - 1:
            add_text(slide, "›", x + 2.51, 2.52, 0.30, 0.40, size=24, color=MAGENTA, bold=True,
                     align=PP_ALIGN.CENTER)
        x += 2.86

    add_rect(slide, 0.60, 3.90, 5.80, 1.55, PURPLE)
    add_text(slide, "RECEITA ESTIMADA PÓS-DEVOLUÇÕES", 0.88, 4.14, 4.95, 0.24,
             size=10, color=MAGENTA, bold=True)
    add_text(slide, "R$ 4,14M", 0.88, 4.49, 3.10, 0.55, size=31, color=WHITE, bold=True)
    add_text(slide, "Entrada de receita no cenário — não benefício líquido do projeto.",
             3.45, 4.55, 2.55, 0.46, size=11.5, color=WHITE)

    add_rect(slide, 6.68, 3.90, 2.85, 1.55, LAVENDER)
    add_label(slide, "Custo histórico", 6.94, 4.14, 2.2)
    add_text(slide, "R$ 3,03M", 6.94, 4.49, 2.2, 0.42, size=23, color=INK, bold=True)
    add_text(slide, "+ R$ 143 mil de frete", 6.94, 5.00, 2.2, 0.24, size=10.5, color=BODY)

    add_rect(slide, 9.80, 3.90, 2.93, 1.55, LAVENDER_2)
    add_label(slide, "Contribuição estimada", 10.06, 4.14, 2.4)
    add_text(slide, "R$ 969 mil", 10.06, 4.49, 2.4, 0.42, size=23, color=INK, bold=True)
    add_text(slide, "23,4% da receita", 10.06, 5.00, 2.2, 0.24, size=10.5, color=BODY)

    add_label(slide, "Limites", 0.60, 5.82, 1.0)
    add_text(slide, "Sem impostos, comissões, logística reversa, retorno físico ou elasticidade de preço. Estoque sem data de snapshot.",
             1.40, 5.76, 11.0, 0.48, size=11.5, color=BODY)
    add_footer(slide, "A2")


def slide_discount(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
    add_header(slide, "A3", "EVIDÊNCIA · DESCONTOS")
    add_title(slide, "Desconto corrói margem; efeito no volume segue inconclusivo.", size=25.5)

    add_label(slide, "Margem de contribuição ponderada", 0.60, 1.70, 4.6)
    bars = [
        ("Sem desconto", 58.1),
        ("5–10%", 54.8),
        ("20–25%", 45.4),
        ("35–40%", 32.2),
    ]
    maxw = 4.25
    y = 2.14
    for label, value in bars:
        add_text(slide, label, 0.60, y + 0.06, 1.08, 0.24, size=11.5, color=INK, bold=True)
        add_rect(slide, 1.78, y, maxw, 0.34, LAVENDER_2)
        add_rect(slide, 1.78, y, maxw * value / 60.0, 0.34, PURPLE)
        add_text(slide, f"{value:.1f}%".replace(".", ","), 6.12, y + 0.04, 0.62, 0.24,
                 size=11.5, color=INK, bold=True, align=PP_ALIGN.RIGHT)
        y += 0.68

    add_rect(slide, 7.05, 1.70, 5.68, 3.48, LAVENDER)
    add_label(slide, "O que a base sustenta", 7.40, 2.02, 4.8)
    facts = [
        ("3,51 un.", "por pedido, com ou sem desconto"),
        ("−0,026 un.", "diferença within-SKU ponderada"),
        ("R$ 579 mil", "teto mecânico de 15% nas aprovadas"),
    ]
    fy = 2.43
    for value, note in facts:
        add_text(slide, value, 7.40, fy, 1.72, 0.32, size=18, color=INK, bold=True)
        add_text(slide, note, 9.17, fy + 0.03, 3.12, 0.30, size=11.5, color=BODY)
        fy += 0.72
    add_text(slide, "O valor de R$ 579 mil é limite aritmético no período observado; não inclui reação de demanda.",
             7.40, 4.62, 4.78, 0.42, size=10.5, color=MUTED)

    add_rect(slide, 0.60, 5.55, 12.13, 0.91, PURPLE)
    add_text(slide, "DECISÃO", 0.88, 5.82, 1.02, 0.24, size=10, color=MAGENTA, bold=True)
    add_text(slide, "Pilotar teto por SKU com grupo de controle; reconhecer benefício financeiro somente após medir elasticidade.",
             1.85, 5.75, 10.38, 0.40, size=13.5, color=WHITE, bold=True)
    add_footer(slide, "A3")


def slide_sequence(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
    add_header(slide, "A4", "POR QUE SEQUENCIAR")
    add_title(slide, "Marketing e CRM entram depois da conciliação.")
    add_text(slide, "O diagnóstico existe; a otimização ainda não seria auditável.",
             0.60, 1.55, 11.8, 0.34, size=15, color=BODY)

    add_rect(slide, 0.60, 2.04, 5.88, 3.54, LAVENDER)
    add_label(slide, "Marketing", 0.90, 2.34, 2.0)
    add_text(slide, "38,2M", 0.90, 2.73, 1.75, 0.52, size=27, color=INK, bold=True)
    add_text(slide, "conversões declaradas em campanhas iniciadas em 2023", 2.62, 2.79, 3.25, 0.50,
             size=11.5, color=BODY)
    add_text(slide, "26,5 mil", 0.90, 3.55, 1.75, 0.42, size=21, color=INK, bold=True)
    add_text(slide, "registros de venda em 2023 — sem campaign_id, UTM ou janela de atribuição", 2.62, 3.55, 3.25, 0.56,
             size=11.5, color=BODY)
    add_line(slide, 0.90, 4.38, 6.12, 4.38, LINE, 0.8)
    add_text(slide, "PRÓXIMO PASSO", 0.90, 4.64, 1.32, 0.22, size=9.5, color=MAGENTA, bold=True)
    add_text(slide, "Instrumentar checkout e conciliar mídia → pedido → margem antes de realocar verba.",
             2.30, 4.58, 3.60, 0.54, size=12.5, color=INK, bold=True)

    add_rect(slide, 6.84, 2.04, 5.89, 3.54, LAVENDER)
    add_label(slide, "CRM", 7.14, 2.34, 2.0)
    add_text(slide, "346 / 15 mil", 7.14, 2.73, 2.30, 0.52, size=27, color=INK, bold=True)
    add_text(slide, "clientes aparecem no extrato de Vendas", 9.42, 2.79, 2.70, 0.42,
             size=11.5, color=BODY)
    add_text(slide, "40,6%", 7.14, 3.55, 1.55, 0.42, size=21, color=INK, bold=True)
    add_text(slide, "dos registros estão concentrados em um único cliente; LTV não reconcilia com o ERP", 8.76, 3.55, 3.35, 0.56,
             size=11.5, color=BODY)
    add_line(slide, 7.14, 4.38, 12.37, 4.38, LINE, 0.8)
    add_text(slide, "PRÓXIMO PASSO", 7.14, 4.64, 1.32, 0.22, size=9.5, color=MAGENTA, bold=True)
    add_text(slide, "Resolver identidade do cliente e recomputar valor observado antes de segmentar incentivos.",
             8.54, 4.58, 3.55, 0.54, size=12.5, color=INK, bold=True)

    add_rect(slide, 0.60, 5.88, 12.13, 0.60, PURPLE)
    add_text(slide, "RESPOSTA À BANCA", 0.88, 6.07, 1.55, 0.22, size=9.5, color=MAGENTA, bold=True)
    add_text(slide, "Não otimizamos canal ou segmento porque isso criaria falsa precisão; priorizamos primeiro o dado conciliável.",
             2.44, 6.01, 9.86, 0.32, size=12.5, color=WHITE, bold=True)
    add_footer(slide, "A4")


def main():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    slide_contract(prs)
    slide_liquidation(prs)
    slide_discount(prs)
    slide_sequence(prs)
    prs.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
