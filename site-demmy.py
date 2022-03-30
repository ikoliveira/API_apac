#coding: utf-8
# Desenvolvimento do site .... 
# Demmily Falcão Fernandes


import backend as bk
import requests
import json 
import pandas as pd 
import os
import glob
import streamlit as st
import matplotlib.pyplot as plt
import calmap
import calplot
import numpy as np


st.title("Dados estações - INMET")
bk.sub_text("Projeto de Estagio", align="center", font=30)


img = 'background.png'
icone = 'ic.jpeg'
bk.set_bg_hack(img)
st.sidebar.image(icone, use_column_width=True)


@st.cache
def acionaSite(estadoEstacao):
    codigosEstacoes = bk.codigosEstacoes(data, estadoEstacao)
    for i in range(len(codigosEstacoes)):
        link = bk.preparaLink(codigosEstacoes[i], dataInicio, dataFim, tipo='h') 
        dados = requests.get(link)
        dat = json.loads(dados.text)
        df = pd.json_normalize(dat)
        df = bk.converte(df)

        Dfmax = df[['DC_NOME','DT_MEDICAO', 'TEM_MAX', 'UMD_MAX']].groupby('DT_MEDICAO').max()
        Dfmin = df[['DT_MEDICAO', 'TEM_MIN', 'UMD_MIN']].groupby('DT_MEDICAO').min()
        dfsite = pd.merge(Dfmax, Dfmin, on=['DT_MEDICAO'])

        Acumchuva = df[['DT_MEDICAO','DATETIME','DC_NOME','CHUVA']]
        tabela = Acumchuva.set_index(["DATETIME"])
        acumdia = tabela['CHUVA'].astype('float').resample('d').sum()
        chuvasite = pd.merge(tabela['DT_MEDICAO'], acumdia, on=['DATETIME'])
      
        if(variavel =='Temperatura e Umidade'):
            st.dataframe(dfsite)
            csv = bk.convert_csv(dfsite)
            st.download_button(label="Download", data=csv, file_name='dataframe.csv', mime='csv')

        elif(variavel == 'Precipitação'):
            
            if var != 'Mapa de Precipitação':
                st.write(tabela['DC_NOME'][0])
                bk.decideGrafico(var, chuvasite, dataInicio, dataFim)

        elif(variavel == 'Mapa de Estações'):
            dfgeral = pd.DataFrame(data = None);
            for i in range(len(codigosEstacoes)):
                link = bk.preparaLink(codigosEstacoes[i], dataInicio, dataFim, tipo='d') 
                dados = requests.get(link)
                dat = json.loads(dados.text)
                dfgeral = pd.json_normalize(dat)
                dfgeral = bk.convertee(dfgeral)
                dfgeral = dfgeral.rename(columns = {"VL_LATITUDE":"lat"})
                dfgeral = dfgeral.rename(columns = {"VL_LONGITUDE":"lon"})
                #st.map(dfgeral)
                if (i == 0):
                    dfgeral.to_csv('tabelaCompleta-' + estadoEstacao + '.csv', mode='w', header=True)
                else:
                    dfgeral.to_csv('tabelaCompleta-' + estadoEstacao + '.csv', mode='a', header=False)
            dmap = pd.read_csv('tabelaCompleta-' + estadoEstacao + '.csv', delimiter=',')
            dmap['lat'] = pd.to_numeric(dmap['lat'])
            dmap['lon'] = pd.to_numeric(dmap['lon'])
            dmap['CHUVA'] = pd.to_numeric(dmap['CHUVA'])
            dmapa = dmap[['lat','lon', 'CHUVA']]
            st.map(dmapa)

link = "https://apitempo.inmet.gov.br/estacoes/T"


states = bk.retornaestados()
estadoEstacao = st.sidebar.selectbox(
    "Selecione o estado da estação desejada:",
    (states.keys())
)


dataInicio = st.sidebar.date_input("Data inicial")
dataFim = st.sidebar.date_input("Data final")
variavel = st.sidebar.selectbox("Selecione a variável desejada:", ['Temperatura e Umidade', 'Precipitação', 'Mapa de Estações'])

if variavel == 'Precipitação':
    var = st.sidebar.selectbox("Selecione abaixo a forma de visualização da precipitação:", ('Gráfico de Barras Modo Interativo', 'Calendário'))


if bk.validalink(link):
    if dataFim < dataInicio:
        st.warning('data errada')
        st.button("Re-run")

    data = bk.dados(link)
    formRes=st.sidebar.button("SUBMIT")  
    if formRes:
        acionaSite(estadoEstacao)
    else:
        bk.sub_text("texto a ser inserido...", align="justify", font=15)
else:
    st.warning('warnin')