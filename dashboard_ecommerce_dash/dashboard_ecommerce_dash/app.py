from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

DATA_PATH = Path(__file__).resolve().parent / "ecommerce_estatistica.csv"
df = pd.read_csv(DATA_PATH)
for col in ["Nota", "N_Avaliações", "Desconto", "Preço", "Qtd_Vendidos_Cod", "Nota_MinMax", "N_Avaliacoes_MinMax", "Desconto_MinMax", "Preço_MinMax"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

app = Dash(__name__)
app.title = "Painel estatístico de e-commerce"

def chart_card(title, description, figure):
    return html.Section(className="chart-card", children=[
        html.H3(title), html.P(description, className="chart-description"),
        dcc.Graph(figure=figure, config={"displayModeBar": True, "responsive": True})
    ])

# 1 — Histograma
fig_hist = px.histogram(df, x="Preço", nbins=25, title="Distribuição dos preços",
    labels={"Preço": "Preço (R$)", "count": "Quantidade de produtos"}, color_discrete_sequence=["#3B82F6"])
fig_hist.update_layout(yaxis_title="Quantidade de produtos", bargap=0.08)

# 2 — Dispersão
scatter = df.dropna(subset=["N_Avaliações", "Qtd_Vendidos_Cod"])
fig_scatter = px.scatter(scatter, x="N_Avaliações", y="Qtd_Vendidos_Cod",
    hover_name="Título" if "Título" in scatter.columns else None,
    title="Avaliações x quantidade vendida (código)",
    labels={"N_Avaliações": "Número de avaliações", "Qtd_Vendidos_Cod": "Quantidade vendida (valor codificado)"},
    color_discrete_sequence=["#0F766E"])
fig_scatter.update_xaxes(type="log", title="Número de avaliações (escala logarítmica)")
fig_scatter.update_yaxes(type="log", title="Quantidade vendida codificada (escala logarítmica)")

# 3 — Mapa de calor
corr_cols = [c for c in ["Nota", "N_Avaliações", "Desconto", "Preço", "Qtd_Vendidos_Cod"] if c in df.columns]
fig_heat = px.imshow(df[corr_cols].corr(numeric_only=True), text_auto=".2f", aspect="auto",
    color_continuous_scale="RdBu_r", zmin=-1, zmax=1, title="Mapa de calor das correlações",
    labels={"x": "Variáveis", "y": "Variáveis", "color": "Correlação"})

# 4 — Barras: dez marcas mais frequentes
brands = df["Marca"].fillna("Não informado").value_counts().head(10).sort_values()
brand_df = brands.rename_axis("Marca").reset_index(name="Quantidade de produtos")
fig_bar = px.bar(brand_df, x="Quantidade de produtos", y="Marca", orientation="h",
    title="10 marcas com mais produtos no conjunto de dados",
    labels={"Quantidade de produtos": "Quantidade de produtos", "Marca": "Marca"},
    color_discrete_sequence=["#7C3AED"])

# 5 — Pizza: gênero/categoria
counts = df["Gênero"].fillna("Não informado").value_counts()
major = counts[counts / counts.sum() >= 0.03].copy()
minor = counts[counts / counts.sum() < 0.03]
if not minor.empty:
    major.loc["Outros"] = minor.sum()
pie_df = major.rename_axis("Gênero").reset_index(name="Quantidade")
fig_pie = px.pie(pie_df, names="Gênero", values="Quantidade", title="Distribuição por gênero/categoria", hole=0.28)

# 6 — Densidade aproximada com histograma normalizado
notes = df.dropna(subset=["Nota"])
fig_density = px.histogram(notes, x="Nota", histnorm="probability density", nbins=20,
    title="Densidade da distribuição das notas", labels={"Nota": "Nota do produto", "y": "Densidade"},
    opacity=0.6, color_discrete_sequence=["#EA580C"])
fig_density.update_layout(yaxis_title="Densidade")

# 7 — Regressão
reg = df.dropna(subset=["Preço", "Qtd_Vendidos_Cod"])
fig_reg = px.scatter(reg, x="Preço", y="Qtd_Vendidos_Cod",
    hover_name="Título" if "Título" in reg.columns else None,
    title="Preço x quantidade vendida (valor codificado)",
    labels={"Preço": "Preço (R$)", "Qtd_Vendidos_Cod": "Quantidade vendida (valor codificado)"},
    trendline="ols", color_discrete_sequence=["#DB2777"])

median_price = df["Preço"].median()
median_text = f"R$ {median_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
app.layout = html.Div(className="page", children=[
    html.Header(className="hero", children=[
        html.Div("ANÁLISE DE DADOS", className="eyebrow"),
        html.H1("Painel estatístico de e-commerce"),
        html.P("Explore preços, avaliações, marcas e relações entre variáveis do catálogo de produtos."),
        html.Div(className="stats", children=[
            html.Div([html.Span(f"{len(df):,}".replace(",", "."), className="stat-value"), html.Span("produtos analisados", className="stat-label")], className="stat"),
            html.Div([html.Span(str(df.shape[1]), className="stat-value"), html.Span("colunas no arquivo", className="stat-label")], className="stat"),
            html.Div([html.Span(median_text, className="stat-value"), html.Span("preço mediano", className="stat-label")], className="stat"),
        ])
    ]),
    html.Main(className="dashboard", children=[
        chart_card("1. Histograma", "Mostra como os preços dos produtos estão distribuídos.", fig_hist),
        chart_card("2. Dispersão", "Compara o número de avaliações com a quantidade vendida codificada. Os eixos usam escala logarítmica.", fig_scatter),
        chart_card("3. Mapa de calor", "Resume a correlação linear entre as principais variáveis numéricas.", fig_heat),
        chart_card("4. Gráfico de barras", "Destaca as dez marcas mais frequentes no arquivo.", fig_bar),
        chart_card("5. Gráfico de pizza", "Apresenta a participação das categorias; categorias pequenas são agrupadas em Outros.", fig_pie),
        chart_card("6. Densidade", "Exibe a distribuição das notas dos produtos por densidade de frequência.", fig_density),
        chart_card("7. Regressão", "Mostra a relação entre preço e quantidade vendida codificada, com uma linha de tendência.", fig_reg),
    ]),
    html.Footer("Projeto educacional. Correlação não implica causalidade; a variável de vendas está codificada e não deve ser interpretada como contagem exata.", className="footer")
])

server = app.server
if __name__ == "__main__":
    app.run(debug=True)
