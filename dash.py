import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import math


@st.cache_data
def verificar_ticker(ticker):
    try:
        dados = yf.Ticker(ticker).history(period="1d", start="2010-01-01", end="2024-11-25")
        return not dados.empty
    except Exception:
        return False


@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = [item + ".SA" for item in base_tickers["Código"]]
    tickers_validos = [ticker for ticker in tickers if verificar_ticker(ticker)]
    return tickers_validos


@st.cache_data
def carregar_dados(empresas):
    cotacoes_acao = pd.DataFrame()
    for ticker in empresas:
        try:
            dados = yf.Ticker(ticker).history(period="1d", start="2010-01-01", end="2024-11-25")
            if not dados.empty:
                cotacoes_acao[ticker] = dados["Close"]
        except Exception as e:
            st.warning(f"{ticker}: Ignorado devido a erro - {str(e)}")
    return cotacoes_acao


acoes_validas = carregar_tickers_acoes()
dados = carregar_dados(acoes_validas)

st.write(
    """
# App Preço de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos
"""
)

st.sidebar.header("Filtros")

lista_acoes = st.sidebar.multiselect("Escolha as ações para visualizar", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        dados.columns = lista_acoes

data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider(
    "Selecione o período",
    min_value=data_inicial,
    max_value=data_final,
    value=(data_inicial, data_final),
    step=dt.timedelta(days=1),
    format="DD/MM/YY",
)

dados = dados.loc[intervalo_data[0] : intervalo_data[1]]

st.line_chart(dados)

texto_performance_ativos = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)

carteira = [1000 for _ in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)

    if performance_ativo > 0:
        texto_performance_ativos += f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos += f"  \n{acao}: :red[{performance_ativo:.1%}]"
    elif math.isnan(performance_ativo):
        texto_performance_ativos += f"  \n{acao}: :blue[Não existe]"
    else:
        texto_performance_ativos += f"  \n{acao}: {performance_ativo:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = (
        f"Performance da carteira com todos os ativos: :green[{performance_carteira:.1%}]"
    )
elif performance_carteira < 0:
    texto_performance_carteira = (
        f"Performance da carteira com todos os ativos: :red[{performance_carteira:.1%}]"
    )
else:
    texto_performance_carteira = (
        f"Performance da carteira com todos os ativos: {performance_carteira:.1%}"
    )

st.write(
    f"""
### Performance dos Ativos
Essa foi a perfomance de cada ativo no período selecionado:

{texto_performance_ativos}

{texto_performance_carteira}
"""
)