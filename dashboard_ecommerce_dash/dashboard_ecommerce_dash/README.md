# Painel Estatístico de E-commerce (Dash)

Aplicação web feita com Python, Dash e Plotly para visualizar os dados de `ecommerce_estatistica.csv` em um painel interativo.

## Gráficos
1. Histograma de preços.
2. Dispersão entre avaliações e quantidade vendida codificada.
3. Mapa de calor de correlações.
4. Barras com as 10 marcas mais frequentes.
5. Pizza da distribuição por gênero/categoria.
6. Densidade da distribuição das notas.
7. Regressão entre preço e quantidade vendida codificada.

## Executar localmente
Requer Python 3.10 ou superior. Deixe o CSV na mesma pasta de `app.py`.

```bash
python -m venv .venv
```

Ative o ambiente:
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Instale e execute:

```bash
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:8050` no navegador.

## Publicar e gerar um link público
1. Crie um repositório GitHub e envie todos os arquivos desta pasta, incluindo `assets/style.css` e `ecommerce_estatistica.csv`.
2. No Render, crie um **Web Service** e conecte o repositório.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:server`
5. Publique. O serviço fornecerá o link público do dashboard.

## Observações
`Qtd_Vendidos_Cod` é uma variável codificada e não representa necessariamente a contagem exata de vendas. Correlação e regressão não comprovam causalidade.
