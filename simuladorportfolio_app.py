import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

# Basic page configuration
#st.set_page_config(page_title="Simulador de Portfolio | Lucas Caúla", page_icon=":desktop_computer:", layout="wide")

def build_sidebar():
    st.write("##")
    lista_ticker = pd.read_csv("assets/tickers_ibra.csv", index_col=0)
    tickers = st.multiselect(label="Selecione as Empresas", options=lista_ticker, placeholder='Tickers')
    tickers = [t+".SA" for t in tickers]
    data_inicio = st.date_input("Data Inicial", format="DD/MM/YYYY", value=datetime(2023,1,2))
    data_fim = st.date_input("Data Final", format="DD/MM/YYYY", value="today")
    aporte_inicial = st.text_input('Aporte Inicial (Opcional):', placeholder='R$')

    if tickers:
        if aporte_inicial: 
            precos = yf.download(tickers, start=data_inicio, end=data_fim)["Adj Close"]
            if len(tickers) == 1:
                precos = precos.to_frame()
                precos.columns = [tickers[0].rstrip(".SA")]

            precos.columns = precos.columns.str.rstrip(".SA")
            precos["IBOV"] = yf.download("^BVSP", start=data_inicio, end=data_fim)["Adj Close"]
            return tickers, precos, aporte_inicial, data_inicio, data_fim
        else: 
            precos = yf.download(tickers, start=data_inicio, end=data_fim)["Adj Close"]
        if len(tickers) == 1:
            precos = precos.to_frame()
            precos.columns = [tickers[0].rstrip(".SA")]

        precos.columns = precos.columns.str.rstrip(".SA")
        precos["IBOV"] = yf.download("^BVSP", start=data_inicio, end=data_fim)["Adj Close"]
        return tickers, precos, None, data_inicio, data_fim
    return None, None, None, data_inicio, data_fim


def build_main(tickers, precos, aporte_inicial, data_inicio, data_fim):
    #PESO TA AQUI
    pesos = np.ones(len(tickers))/len(tickers)
    precos["Portfólio"] = precos.drop("IBOV", axis = 1) @ pesos
    precos_normalizados = 100 * precos / precos.iloc[0]
    retorno_total = precos.pct_change()[1:]
    volatilidade_anualizada = retorno_total.std()*np.sqrt(252)
    retorno_porcentagem = (precos_normalizados.iloc[-1] - 100) / 100

    if aporte_inicial:
        aporte_inicial = float(aporte_inicial)
        resultado = (retorno_porcentagem["Portfólio"] * aporte_inicial) + aporte_inicial
        diferenca = resultado - aporte_inicial
        resultado = "{:,.2f}".format(round(resultado, 2))
        aporte_inicial = "{:,.2f}".format(round(aporte_inicial, 2))
        diferenca = "{:,.2f}".format(round(diferenca, 2))
        data_inicial_formatada = data_inicio.strftime("%d/%m/%Y")
        data_final_formatada = data_fim.strftime("%d/%m/%Y")
        if resultado > aporte_inicial:
            st.write(f"Parabéns pela sua simulação de carteira de investimentos! Com base no aporte inicial de R\${aporte_inicial} realizado de {data_inicial_formatada} até {data_final_formatada} seu resultado foi R\${resultado}, com ganho de R\${diferenca}")
            st.write("---")
        elif resultado < aporte_inicial:
            st.write(f"Parabéns pela sua simulação de carteira de investimentos! Com base no aporte inicial de R\${aporte_inicial} realizado de {data_inicial_formatada} até {data_final_formatada} seu resultado foi R\${resultado}, com perda de R\${diferenca[1:]}")
            st.write("---")
        else:
            st.write(f"Parabéns pela sua simulação de carteira de investimentos! Com base no aporte inicial de R\${aporte_inicial} realizado de {data_inicial_formatada} até {data_final_formatada} seu resultado foi R\${resultado}, sem ganhos.")
            st.write("---")

    mygrid = grid(3 ,3 ,3 ,3 ,3 , 3, vertical_align="top")
    for ativo in precos.columns:
        c = mygrid.container(border=True)
        c.subheader(ativo, divider="red")
        colA, colB, colC = c.columns(3)
        if ativo == "Portfólio":
            colA.image("assets/pie-chart-dollar-svgrepo-com.svg")
        elif ativo == "IBOV":
            colA.image("assets/pie-chart-svgrepo-com.svg")
        else:
            colA.image(f'https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{ativo}.png', width=85)
        colB.metric(label="retorno", value=f"{retorno_porcentagem[ativo]:.0%}")
        colC.metric(label="volatilidade", value=f"{volatilidade_anualizada[ativo]:.0%}")
        style_metric_cards(background_color='rgba(255,255,255,0)')

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("Desempenho Relativo")
        st.write("##")
        st.line_chart(precos_normalizados, height=600)

    with col2:
        st.subheader("Risco-Retorno")
        st.write("##")
        fig = px.scatter(
            x=volatilidade_anualizada,
            y=retorno_porcentagem,
            text=volatilidade_anualizada.index,
            color=retorno_porcentagem/volatilidade_anualizada,
            color_continuous_scale=px.colors.sequential.Bluered_r
        )
        fig.update_traces(
            textfont_color='white', 
            marker=dict(size=45),
            textfont_size=10,                  
        )
        fig.layout.yaxis.title = 'Retorno Total'
        fig.layout.xaxis.title = 'Volatilidade (anualizada)'
        fig.layout.height = 600
        fig.layout.xaxis.tickformat = ".0%"
        fig.layout.yaxis.tickformat = ".0%"        
        fig.layout.coloraxis.colorbar.title = 'Sharpe'
        st.plotly_chart(fig, use_container_width=True)

st.set_page_config(page_title="Simulador de Portfólio", page_icon=":bar_chart:", layout="wide")

with st.sidebar:
    tickers, precos, aporte_inicial, data_inicio, data_fim = build_sidebar()

st.title("Simulador de Portfólio")
if tickers:
    build_main(tickers, precos, aporte_inicial, data_inicio, data_fim)
else:
    st.write("Feito por [Lucas Caúla](https://www.linkedin.com/in/lucas-ca%C3%BAla-b17169215/?originalSubdomain=br)")
    st.write("O objetivo deste projeto é criar um simulador que permita aos usuários experimentar a criação e gerenciamento de um portfólio de ações usando Python. O projeto abordará desde a seleção das ações até a análise do desempenho do portfólio ao longo do tempo.")
    st.write("⬅ Para começar, selecione as ações desejadas ao lado.")