import requests
import json 
import pandas as pd 
import streamlit as st
import datetime
import calmap
import matplotlib.pyplot as plt
import july
import numpy as np
from matplotlib import dates
import base64

# Formata a string que representa o link que será usado para download das estacoes.
@st.cache
def preparaLink(codigoEstacao, dataInicio, dataFim, tipo):
    if tipo == 'h':
        url = 'https://apitempo.inmet.gov.br/estacao/'
        urlfim = url + "/" + str(dataInicio) + "/" +  str(dataFim) + "/" + codigoEstacao
        return urlfim
    elif tipo == 'd':
        url = 'https://apitempo.inmet.gov.br/estacao/diaria/'
        url2 = url + str(dataInicio)+"/"+str(dataFim)+"/"+codigoEstacao
        return url2


# Prepara o arquivo json que foi gerado a partir do download dos dados direto no site do INMET
@st.cache
def dados(link):
    resp = requests.get(link)
    return json.loads(resp.text)
  

    
#Extrai todos os estados das estações
def retornaestados():
    estados = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AP': 'Amapá',
    'AM': 'Amazonas',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MT': 'Mato Grosso',
    'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PR': 'Paraná',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'SC': 'Santa Catarina',
    'SP': 'São Paulo',
    'SE': 'Sergipe',
    'TO': 'Tocantins'}
    return estados
    

# Retorna uma lista com o codigo de cada estacao referente ao Estado selecionado
def codigosEstacoes(data, estadoEstacao):
    codigos_estacoes =  []
    for dic in range(len(data)):
        if(data[dic]["SG_ESTADO"] == estadoEstacao):
            dict = data[dic]
            codigos_estacoes.append(dict['CD_ESTACAO'])
    return codigos_estacoes

#converte as colunas para seus respectivos formatos
def converte(df):

    for convert in range(len(df.columns)):
        try:
            if(df[df.columns[convert]] != "HR_MEDICAO"):
                pd.to_numeric(df[df.columns[convert]])
        except:
            continue

    df = df.rename(columns={"HR_MEDICAO":"DATETIME"})
    df["DATETIME"] = pd.to_datetime(df["DT_MEDICAO"] + " " + df["DATETIME"])

    return df

#opção de download csv para dataframe temperatura

@st.cache
def convert_csv(df):
    return df.to_csv().encode('utf-8')

#plot de calendário para chuva
def calendar(dfchuva, dataini, datafim):
    #calplot.calplot(chuva, cmap='Reds', figsize=(16,8))
    #plt.suptitle('Calendar Heatmap', y=1.0, fontsize=20)


     #plt.figure(figsize=(16,8))
     #calmap.yearplot(data=dfchuva, year=2014)
     #plt.suptitle('teste', y=.65, fontsize=20)

     from july.utils import date_range
     dates = date_range(dataini, datafim)
     july.heatmap( dates, data=dfchuva, title='Acumulado Precipitação', cmap="Blues", month_grid=True, horizontal = True, colorbar= True)
     plt.plot()


# Retorna o grafico de chuvas em barras
# A função recebe como argumento um dataframe e após separar a coluna desejada monta o gráfico sobre a lista.
# A linha days = dates.date2num(datas) precisa receber necessariamente um dado do tipo lista para funcionar.
def plotaGrafico(chuvasite):  
        
        datas = []
        
        for i in range(len(chuvasite['DT_MEDICAO'])):
            datas.append(np.datetime64(chuvasite['DT_MEDICAO'][i]))
        
        plt.rcParams['figure.figsize']=6,4

        days= dates.date2num(datas)
    
        plt.bar(days, chuvasite['CHUVA'], width=0.4, color='b')
     
        plt.xticks(days)
        x_y_axis=plt.gca()
        xaxis_format= dates.DateFormatter('%m/%d')
        
        x_y_axis.xaxis.set_major_formatter(xaxis_format)
        x_y_axis.set_ylim(0)
        plt.xlabel('Data(mm/dd)') 
        plt.ylabel('Precipitação') 
        plt.title('Acumulado de Chuva')

        st.pyplot()
        plt.clf()


def decideGrafico(var, dados, dataInicio, dataFim):
    st.set_option('deprecation.showPyplotGlobalUse', False)
    if var == "Gráfico de Barras Modo Interativo":
        st.bar_chart(data=dados['CHUVA'])
    elif var == 'Mapa de Precipitação':
        st.map(dados)
    elif var == 'Calendário':
        st.pyplot(calendar(dados['CHUVA'], dataInicio, dataFim))


def validalink(link):
    return requests.get(link).status_code == 200
    

def convertee(df):

    for convert in range(len(df.columns)):

        try:
            pd.to_numeric(df[df.columns[convert]])
        except:
            continue
    return df




def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
    The bg will be static and won't take resolution of device into account.
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


def app_meta(icon):
    main_bg_ext = "png"
     # set sidebar width
    st.markdown(
    """

    <style>

    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 300px;
    }

    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 300px;
        margin-left: -300px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )


def sub_text(text, align, font):
    '''
    A function to neatly display text in app.
    Parameters
    ----------
    text : Just plain text.
    Returns
    -------
    Text defined by html5 code below.
    '''
    
    html_temp = f"""
    <h1 style = "color:#1B3B69; text-align:{align}; font-size: {font}px"> {text} </h1>
    </div>
    """
    
    st.markdown(html_temp, unsafe_allow_html = True)