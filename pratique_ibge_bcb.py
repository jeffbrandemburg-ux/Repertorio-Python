from pathlib import Path
import requests
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

print("=" * 70)
print("1 - API DO IBGE")
print("=" * 70)
print("Endpoint:", IBGE_URL)
print("Informação: identificação e localização dos municípios brasileiros.")

try:
    response = requests.get(IBGE_URL, timeout=60)
    response.raise_for_status()
    dados_ibge = response.json()

    registros = []
    for municipio in dados_ibge:
        microrregiao = municipio.get("microrregiao") or {}
        mesorregiao = microrregiao.get("mesorregiao") or {}

        registros.append({
            "id_municipio": municipio.get("id"),
            "municipio": municipio.get("nome"),
            "id_microrregiao": microrregiao.get("id"),
            "microrregiao": microrregiao.get("nome"),
            "id_mesorregiao": mesorregiao.get("id"),
            "mesorregiao": mesorregiao.get("nome")
        })

    df_ibge = pd.DataFrame(registros)

    print("\nPrimeiras linhas:")
    print(df_ibge.head())
    print("\nDimensões:", df_ibge.shape)

    df_ibge.to_csv(
        DATA_DIR / "ibge_municipios.csv",
        index=False,
        encoding="utf-8-sig"
    )

except requests.RequestException as erro:
    print("Erro na requisição do IBGE:", erro)

BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"

PARAMS = {
    "formato": "json",
    "dataInicial": "01/01/2025",
    "dataFinal": "31/12/2025"
}

print("\n" + "=" * 70)
print("2 - API DO BANCO CENTRAL")
print("=" * 70)
print("Endpoint:", BCB_URL)
print("Informação: taxa diária do dólar americano (venda).")

try:
    response = requests.get(BCB_URL, params=PARAMS, timeout=60)
    response.raise_for_status()

    df_bcb = pd.DataFrame(response.json())

    print("\nPrimeiras linhas:")
    print(df_bcb.head())
    print("\nQuantidade de registros:", len(df_bcb))

    bcb_csv = BASE_DIR / "bcb_tabela.csv"
    df_bcb.to_csv(
        bcb_csv,
        index=False,
        encoding="utf-8-sig"
    )
    print("\nbcb_tabela.csv salvo em:", bcb_csv)

    df_bcb["data"] = pd.to_datetime(
        df_bcb["data"],
        dayfirst=True,
        errors="coerce"
    )

    df_bcb["valor"] = pd.to_numeric(
        df_bcb["valor"],
        errors="coerce"
    )

    df_bcb = df_bcb.dropna(
        subset=["data", "valor"]
    ).copy()

    df_bcb = df_bcb.drop_duplicates().copy()

    df_bcb = df_bcb.rename(
        columns={"valor": "dolar_venda_brl"}
    )

    print("\n" + "=" * 70)
    print("3 - VALIDAÇÃO DOS DADOS")
    print("=" * 70)

    print("\nPrimeiras linhas após tratamento:")
    print(df_bcb.head())

    print("\nTipos:")
    print(df_bcb.dtypes)

    print("\nValores nulos:")
    print(df_bcb.isnull().sum())

    print("\nDuplicidades:", df_bcb.duplicated().sum())
    print("Quantidade final de registros:", len(df_bcb))

    print("\nEstatísticas do dólar:")
    print(df_bcb["dolar_venda_brl"].describe())

    csv_tratado = BASE_DIR / "dados_tratados.csv"
    parquet_tratado = BASE_DIR / "dados_tratados.parquet"

    df_bcb.to_csv(
        csv_tratado,
        index=False,
        encoding="utf-8-sig"
    )

    try:
        df_bcb.to_parquet(
            parquet_tratado,
            index=False
        )
    except ImportError:
        print("\nPara gerar Parquet, instale no terminal:")
        print("pip install pyarrow")
        parquet_tratado = None

    print("\nArquivos tratados:")
    print(csv_tratado)
    if parquet_tratado:
        print(parquet_tratado)

except requests.RequestException as erro:
    print("Erro na requisição do Banco Central:", erro)

print("\n" + "=" * 70)
print("4 - RESPOSTAS TEÓRICAS")
print("=" * 70)

print("""
1. Importância do web scraping no ambiente de trabalho

O web scraping permite coletar automaticamente informações disponíveis
na internet, reduzindo tarefas manuais e facilitando pesquisas,
monitoramento, organização e análise de dados. Seu uso deve respeitar
as regras do site e a legislação aplicável.

2. Riscos legais e éticos

Os principais riscos envolvem desrespeitar termos de uso, utilizar
conteúdo protegido por direitos autorais de forma inadequada e coletar
ou tratar dados pessoais sem observar a LGPD. Também deve-se evitar
sobrecarga dos servidores.

Duas medidas práticas:
- verificar termos de uso, regras de acesso e robots.txt;
- coletar somente os dados necessários e respeitar limites de requisições,
  evitando dados pessoais quando não forem necessários.

3. API x requisição sem API

Uma API oferece uma interface estruturada para que programas acessem
dados ou serviços. Os dados geralmente são fornecidos em formatos
estruturados, como JSON ou XML.

Sem API, o programa pode acessar diretamente uma página HTML, arquivo ou
outro recurso. No web scraping, por exemplo, é necessário interpretar
o conteúdo da página para localizar os dados.

4. Qual abordagem é mais adequada?

Quando existe uma API oficial adequada, ela normalmente é a melhor opção,
pois oferece dados estruturados, maior previsibilidade e uma forma de
acesso definida pelo fornecedor.

O web scraping pode ser usado quando não existe uma API adequada e a
coleta é permitida, mas exige atenção maior às mudanças no site, termos
de uso, direitos autorais, privacidade e volume de requisições.
""")

print("=" * 70)
print("PROCESSAMENTO CONCLUÍDO")
print("=" * 70)
