import streamlit as st
import streamlit.components.v1 as stc

import numpy as np
#import pprint
#from itertools import cycle, islice
import collections
from IPython.core.display import HTML
import warnings
warnings.filterwarnings('ignore')

import re  # stylizing streamlit dataframe viewrticker
from matplotlib import pyplot as plt

# File Processing Pkgs
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from csv import writer

import pandas.testing
from PIL import Image
from IPython.display import display

# Date & Time Pkgs
import time
import datetime as dt
from datetime import datetime, timedelta, date

# Ploting Pkgs
# import plotly.graph_objects as go
# import plotly.express as px
# import matplotlib.pyplot as plt
# from matplotlib.ticker import FuncFormatter
# from matplotlib import cm
# import seaborn as sns

# Finance Pkgs
import yfinance as yf
from yfinance import shared
import pypfopt

import portfolio as pf
import ef_frontier as ef
import montecarlo as mc

# from pypfopt import risk_models, plotting, expected_returns, EfficientFrontier, \
#     DiscreteAllocation, objective_functions

# Locais produzidas "na casa"
import proc_ifix, proc_data11, plot_funcs1, new_indic

#@st.cache
# def load_data(dataset_file):
#    data = pd.read_csv(dataset_file, sep=';', encoding='cp1252')
#    return data


#@st.cache
def get_Data1(tickers_selected, tipo=""):

    d_ini = (dt.datetime.today() - dt.timedelta(1984)).strftime('%Y-%m-%d')
    d_end = dt.datetime.today().strftime('%Y-%m-%d')
   
    tickers_selected.sort()
    tickers_sorted = tickers_selected

    tickers = []

    if not tipo:
        # Introduz extensao .SA em cada ticker para o yfinance
        for i in range(len(tickers_sorted)):
            tickers.append(tickers_sorted[i] + '.SA')
    else:
        tickers = tickers_sorted

    # Verifica ausencia de dados
    error_message = []
    msg = ''

    i = 0
    
    for ticker in tickers:
        tickerdata = yf.Ticker(ticker)
        history = tickerdata.history(start=d_ini, end=d_end)

        #st.sidebar.write(list(shared._ERRORS.keys())[0])

        if len(list(shared._ERRORS.keys())) > 0:
                       
            if i >= len(list(shared._ERRORS.keys())):
                break
            else:
                error_message.append(list(shared._ERRORS.keys())[i])
            i += 1 

    if len(error_message) > 0:

        for i in range(len(error_message)):
            msg += "[" + error_message[i] + "], "
            tickers.remove(error_message[i])

        st.sidebar.warning('A lista de ativos ' + msg + ' foi retirada por possuir menos de 30 dados')

    # Fim-Verifica

    tickers.sort()  # Resorteado depois da verificacao

    # Prepara portfolio 
    pf1 = pf.build_portfolio(names=tickers,
                    start_date=d_ini,
                    end_date=d_end, data_api='yfinance')

    db_assets = pf1.data
    #db_assets = yf.download(tickers, start=d_ini, end=d_end)
    df = db_assets.copy()

    # Testa se é ticker único (pandas series)
    if len(tickers) == 1:
        # df = pd.DataFrame(db_assets, columns=tickers, index=list(db_assets.index))
        df = pd.DataFrame(df, index=list(db_assets.index))

    df.columns = tickers
    # df.to_csv('app_B3.csv', index=True)

    df = val_Stocks(df)

    # Alteracao CRUCIAL - VERIFICAR 
    pf1.data = df
    ################################
    return df.loc[d_ini:d_end], d_ini, d_end, pf1


def val_Stocks(df_Pos_Escolha, min_limit=30):
    # Checa número mínimo de ativos para significância estatística

    df = df_Pos_Escolha
    df_descr = pd.DataFrame(df.describe())

    linhas = len(df)
    cols = df_descr.columns
    drop_cols = []
    min_ativos = min_limit

    for i in range(len(cols)):
        if df_descr[cols[i]]['count'] < min_ativos:
            drop_cols.append(cols[i])

    sem_dados = ""
    if drop_cols:
        for i in drop_cols:
            sem_dados += i.replace('.SA', '') + " "

        # for i in range(len(drop_cols)):
        #   ativo = '[' + drop_cols[i] + ']'
        #   sem_dados += ativo.replace('.SA', '')

        if len(drop_cols) > 1:
            st.sidebar.warning('A lista ' + sem_dados + ' foi retirada por possuir menos de 30 dados')
        else:
            st.sidebar.warning('O ativo ' + sem_dados + ' foi retirado por possuir menos de 30 dados')

        df.drop(drop_cols, axis='columns', inplace=True)

    # Elimina NaNs

    df.dropna(inplace=True)
    df = df.round(decimals=2)

    # print('Saindo de val_Stocksdf', df)

    return(df)


# Leitura do arquivo geral baixado da b3 - processo ETL (etl.py <= '2021-06-06 - ETL de Dados Históricos da B3.ipynb')
# Montagem da lista de ativos para serem selecionados com multiselect da Streamlit

@st.cache(suppress_st_warning=True)
def gera_Lista(path='tmp/', name_file='fii_B3', type_file='csv', codbdi=12):
    _file = f'{path}{name_file}.{type_file}'

    df2 = pd.read_csv(_file)

    if codbdi:
        df2 = df2[['sigla_acao', 'codbdi']]
        df2 = df2[df2['codbdi'] == codbdi]

        # Dropa coluna codbdi que já serviu ao seu propósito de permitir a seleção da família de ativos (FIIs -> codbdi==12)
        df2 = df2.drop(['codbdi'], 1)

        df2.drop_duplicates('sigla_acao', ignore_index=True, inplace=True)
        df2.sort_values('sigla_acao', inplace=True)

        lista_completa_ativos = list(df2['sigla_acao'].values)
        # print("1 ", lista_completa_ativos)
    else:
        df2 = df2[['Ticker', 'Name']]

        df2.drop_duplicates('Ticker', ignore_index=True, inplace=True)
        df2.sort_values('Ticker', inplace=True)

        lista = []
        tam = len(df2)
        for i in range(tam):
            lista.append(df2['Ticker'][i])  # + ' - ' + df2['Name'][i])
            # lista.append(df2['Name'][i] + ' - ' + df2['Ticker'][i])

        lista_completa_ativos = lista
        # print("2 ", lista_completa_ativos)

    return lista_completa_ativos


def check_Email(email):
    # regex = "\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
    reg_ex = r'[^@]+@[^@]+\.[^@]+'

    # pass the regular expression
    # and the string in search() method
    if(re.search(reg_ex, email)):
        return True
    else:
        return False


def check_Nome(nome):   # Nao aceita acentos
    # regex = "\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
    reg_ex = r'[a-zA-Z0-9]'

    # pass the regular expression
    # and the string in search() method
    if(re.search(reg_ex, nome)):
        return True
    else:
        return False


# def main():
st.set_page_config(layout="wide")

image = Image.open("PORT_co_Peq.png")
# st.sidebar.write("""
# **[PORTI]**.co
# """)
st.sidebar.image(image, use_column_width=False, width=100)

# Pagina Central

#col1, col2, col3 = st.beta_columns((1, 4, 1))
col1, col2, col3 = st.beta_columns((1, 4, 1))

with col1:
    st.image(image, use_column_width=False, width=100)

with col2:
    
    Title_html = """
    <style>
        .title h1{
          user-select: none;
          font-size: 43px;
          color: white;
          background: repeating-linear-gradient(-45deg, red 10%, red 50%, red 100%, rgb(0, 0, 0) 100%);
          background-size: 600vw 600vw;
          -webkit-text-fill-color: transparent;
          -webkit-background-clip: text;
          animation: slide 10s linear infinite forwards;
        }
        .title h2{font-size: 32px; color: red;}
        @keyframes slide {
          0%{
            background-position-x: 0%;
          }
          100%{
            background-position-x: 600vw;
          }
        }
    </style> 
    
    <div class="title">
        <h1>Portfólios Baseados em Dados</h1>
        <!--<h2><b>(Risco/Retorno Históricos)</b></h2>-->
        <p></p>
        <p>&nbsp</p>
        <h3><b>INSTRUÇÕES DE USO:</b</h3>
        <p></p>
        <p>&nbsp</p>
        <h3>1 - Informe seu nome e melhor e-mail (e tecle TAB). </h3>
        <h3>2 - Escolha o Tipo de Ativo a partir da lista suspensa (e tecle TAB). </h3>
        <h3>3 - Selecione os Ativos a partir da lista (clique a seta antes de digitar). </h3>
        <h3>4 - Confirme suas escolhas. </h3>
        <h3>5 - Se houver mensagem de alerta, substitua o ativo.</h3>
        <h3>6 - Para sair do App basta fechar o navegador.</h3>  
    </div>
    """
    st.markdown(Title_html, unsafe_allow_html=True)  # Title rendering

# Pega nome e-mail

nome = st.sidebar.text_input('Nome')
e_mail = st.sidebar.text_input('E-mail')

if not check_Nome(nome):
    st.sidebar.warning('Digite seu nome sem acentos!')
    st.stop()

if not check_Email(e_mail):
    st.sidebar.warning('Digite um e-mail válido e tecle <ENTER>')
    st.stop()
else:
    st.sidebar.success('Obrigado')

if e_mail:
    with open('tmp/e_mail.csv', 'a', newline='', encoding='ISO-8859-1') as f:
        dia = date.today()
        data_hoje = dia.strftime("%Y-%m-%d")
        dados = [data_hoje, e_mail, nome]
        writer_obj = writer(f)
        writer_obj.writerow(dados)
        f.close()

    file_name = 'tmp/e_mail.csv'
    file_name_no_dup = 'tmp/e_mail_no_dup.csv'
    df = pd.read_csv(file_name, sep=',', encoding='ISO-8859-1')
    df.drop_duplicates(subset=None, keep=False, inplace=True)
    # escreve o resultado em outro arquivo
    df.to_csv(file_name_no_dup, index=False)

# Fim Pega nome e e-mail

op_list = ''
options = ''
tipo_ativo = ''

# print(e_mail)

if e_mail:

    tipo_ativo = st.sidebar.selectbox('Escolha o Tipo de Ativo', ['Ações', 'FIIs', 'REITs', 'Stocks', 'Outros'])

    if tipo_ativo == 'Ações':
        op_List = gera_Lista(path='X://Portfolios//Streamlit//Porti//', name_file='all_B3', type_file='csv', codbdi=2)  # usando st.cache

    if tipo_ativo == 'FIIs':
        op_List = gera_Lista()  # usando st.cache

    if tipo_ativo == 'REITs':
        op_List = gera_Lista(path='X://Portfolios//Streamlit//Porti//', name_file='US_REITs', type_file='csv', codbdi="")  # usando st.cache

    if tipo_ativo == 'Stocks':
        op_List = gera_Lista(path='X://Portfolios//Streamlit//Porti//', name_file='US_Stocks', type_file='csv', codbdi="")  # usando st.cache

    _OK = ""
    _Ciao = ""

    if tipo_ativo:
        options = st.sidebar.multiselect('Selecione os Ativos da sua Carteira', op_List)
        # Segue o aplicativo

        param_tipo = ""

        if (tipo_ativo == 'REITs') | (tipo_ativo == 'Stocks'):
            # options = [i.split(' - ', 1)[0] for i in options]  # separa os Tickers (coluna 2)
            param_tipo = 'REITs'

        if options:
            _OK = st.sidebar.button('Confirma ?')
            # _NoOK = st.sidebar.button('Reescolhe')
            # _Ciao = st.sidebar.button('Sai do App')

            if _OK:
                # Selecionados os tickers, busca os preços no yfinance
                df, data_inicio, data_fim, pf2 = get_Data1(options, param_tipo)
                df1 = df.copy()
                #print("DF1 ---- ", df1.head())

                # Valida a significancia dos dados (result set > 30 linhas de preços)

                if (len(df) < 30):
                    st.sidebar.warning('Ativo com menos de 30 datas. Por favor, substitua e refaça a escolha!')
                    # st.sidebar.write('Ativos com menos de 30 datas. Por favor, refaça a escolha!')
                else:

                    df_disp = df.copy()
                    df_disp.reset_index(inplace=True)
                    df_disp = df_disp.rename(columns={'index': 'Date'})

                    df_disp['Date'] = pd.to_datetime(df_disp['Date']).dt.strftime('%Y-%m-%d')

                    # col1, col2 = st.beta_columns(2)

                    # df_disp.index = df_disp.index.normalize()  # tira a horas e minutos do datetime index
                    with col2:
                        
                        st.write("  ")
                        st.write("  ")
                        st.write("  ")
                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 24px;"><b>Indicadores do Portfólio (em Beta Teste)</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        
                        #st.write("  ")
                        #st.markdown(''' ### **Indicadores do Portfólio - Beta Teste** ''')
                        #st.write("  ")
                        #plot_funcs1.view_Table2(df_disp)
                        
                        df_indic, _= new_indic.indic(df, data_inicio, data_fim, rf=4.86)

                        df_disp = df_indic.copy()
                        df_disp.reset_index(drop=False, inplace=True)
                        
                        df_disp.columns = ['Indicador', 'Renda Fixa com Buy&Hold', 'Apenas Buy&Hold']
                        df_disp = df_disp.reindex(columns = ['Indicador', 'Renda Fixa com Buy&Hold', 'Apenas Buy&Hold'])

                        df_disp.set_index('Indicador', drop=True, inplace=True)

                        df_disp = df_disp.loc[:, ['Renda Fixa com Buy&Hold', 'Apenas Buy&Hold']]

                        #decimals = 2    
                        #df_disp['Rebalanceamento'] = df['Rebalanceamento'].apply(lambda x: round(x, decimals))
                        #df_disp['Buy&Hold'] = df['Buy&Hold'].apply(lambda x: round(x, decimals))

                        #st.dataframe(df_disp.style.highlight_max(axis=0))                   
                        #st.write(s)

                        s = df_disp.style.highlight_min(color="red").set_precision(2)
                        st.table(s)
                        plt.savefig("Indic.png") 

                        #st.write(df_disp)
                        #plot_funcs1.view_Table(df_disp)                     

                    if tipo_ativo == "FIIs":
                        df_acum_c_IFIX = proc_ifix.incl_Ifix(df)  # inclui o IFIX para ser plotado junto com os ativos
                    else:
                        df_acum = proc_ifix.ret_Acum_Diario(df)

                    # col3, col4 = st.beta_columns(2)

                    with col2:

                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 24px;"><b>Gráfico comparativo dos Ativos do Portfólio</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
              
                        if tipo_ativo == "FIIs":
                            st.write(''' #### **Ativos escolhidos e o IFIX** ''')
                            plot_funcs1.plot_02(df_acum_c_IFIX, 'acum')
                        else:
                            st.write("Ativos escolhidos")
                            plot_funcs1.plot_02(df_acum, 'acum')

                    # col5, col6 = st.beta_columns(2)

                    with col2:
                       
                        #################################
                        # def proc_Result(df):
                        # Fluxo de Execução do Processamento :

                        # (0) Limpa o '.SA' das colunas do df
                        #ativos = df.columns
                        #colunas = []
                        # for i in range(len(ativos)):
                        #    a = ativos[i].replace('.SA', '')
                        #    colunas.append(a)

                        #df.columns = colunas

                        # (1) Calcula retorno medio anual de cada ativo da lista de ativos escolhidos
                        
                        retorno_medio = proc_data11.xPected_Ret_Media(df1)

                        # (2) Calcula a Covariância de Ledoit-Wolf entre os ativos
                        covar = proc_data11.cov_LW(df1)

                        ##### INÍCIO DO PORT. MAX INDICE DE SHARPE

                        # (3) Obtém os PESOS do portfólio de Máx. Indice de Sharpe e da fronteira eficiente
                        pesos, fronteira_eficiente = proc_data11.port_max_Sharpe_055(covar, retorno_medio)

                        # (4) ALOCAÇÃO - Obtém as qtdes de alocacao do portfólio com Máx. Indice de Sharpe, para um valor de patrimônio
                        #     default = 100000
                        alocacao_Max_Sharpe, sobra_Max_Sharpe = proc_data11.aloc_Otima(df1, pesos, valor=100000)

                        # (5) PERFORMANCE MÁX. SHARPE - Mede a performance do portfólio com Máx. Indice de Sharpe
                        ret_Max_Sh, vol_Max_Sh, max_Sharpe = proc_data11.perf_Port(fronteira_eficiente)
                        # fronteira_eficiente foi retornada em port_Max_Sharpe(covar, retorno_medio), processada no passo (3)

                        df_Max_Sharpe = proc_data11.df_To_Pie(pesos)  # Esteve inibida
                        
                        # (6) Plotagens e Resultados

                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Pesos Percentuais para o Portfólio de Máx. Índice de Sharpe</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        
                        plot_funcs1.pie_Plot_Tickers(df_Max_Sharpe, 'max_sharpe')

                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Quantidades de Ações/Cotas para o Portfólio de Máx. Índice de Sharpe</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)

                        df_aloc_Max_Sharpe = proc_data11.df_To_Pie(alocacao_Max_Sharpe)
                        plot_funcs1.pie_Plot_Tickers(df_aloc_Max_Sharpe, "aloc_max_sharpe")

                        # (7) Calcula a Covariância de Ledoit-Wolf entre os ativos
                        #covar = proc_data11.cov_LW(df1)
                        #pesos_Max_Sharpe, fronteira_eficiente = proc_data11.port_Min_Vol(covar, retorno_medio)

                        retorno, volatilidade, sharpe = proc_data11.perf_Port(fronteira_eficiente)

                        st.markdown(''' ### Performance Portfólio de Máx. Indice de Sharpe ''')
                        st.write('Retorno Anual Esperado: ', f'{retorno*100:.1f}%')
                        st.write('Volatilidade Anual: ', f'{volatilidade*100:.1f}%')
                        st.write('Índice de SHARPE: ',  f'{sharpe:.2f}')
                        st.write(" ")
                        st.write(" ")

                        ##### FIM PORT. MAX INDICE DE SHARPE 

                        ##### PORTFOLIO DE VARIÂNCIA MÍNIMA (Menor Risco)

                        # (8) Obtém os PESOS do portfólio de Mín. Volatilidade e da fronteira eficiente correspondente
                        pesos_Min_Vol, fronteira_eficiente_Min_Vol = proc_data11.port_Min_Vol(covar, retorno_medio)

                        # (9) ALOCAÇÃO MÍN. VOLATILIDADE - Obtém os percentuais de alocacao do portfólio com Mín. Volatilidade, para um valor de patrimônio
                        #     default = 100000
                        alocacao_Min_Vol, sobra_Min_Vol = proc_data11.aloc_Otima(df1, pesos_Min_Vol, valor=100000)

                        # (10) CÁLCULO DA PERFORMANCE MÍN. VOLATILIDADE - Mede a performance do portfólio com Mín. Volatilidade
                        retorno, volatilidade, sharpe = proc_data11.perf_Port(fronteira_eficiente_Min_Vol)
                        # fronteira_eficiente_Min_Vol foi retornada em port_Min_Vol(covar, retorno_medio)
                        
                        # (11) Plotagens e Resultados
                        df_Min_Vol = proc_data11.df_To_Pie(pesos_Min_Vol)

                        #st.markdown(''' ### **Pesos Percentuais para o Portfólio de Variância Mínima** ''')


                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Pesos Percentuais para o Portfólio de Variância Mínima</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)

                        plot_funcs1.pie_Plot_Tickers(df_Min_Vol, 'min_vol')

                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Quantidades de Ações/Cotas para o Portfólio de Variância Mínima</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        
                        df_aloc_Min_Vol = proc_data11.df_To_Pie(alocacao_Min_Vol)
                        plot_funcs1.pie_Plot_Tickers(df_aloc_Min_Vol, "aloc_min_vol")

                        st.markdown(''' ### Performance Portfólio de Variância Mínima ''')
                        st.write('Retorno Anual Esperado: ', f'{retorno*100:.1f}%')
                        st.write('Volatilidade Anual: ', f'{volatilidade*100:.1f}%')
                        st.write('Índice de SHARPE: ', f'{sharpe:.2f}')
                        st.write(" ")
                        st.write(" ")

                        ##### FIM PORT. VARIÂNCIA MÍNIMA 

                        ##### PORTFOLIO DE RISCO MÁXIMO TOLERADO PELO INVESTIDOR 

                        # (12) Obtém os PESOS do portfólio de Risco Máx. tolerado pelo Investidor e da respectiva fronteira eficiente
                        pesos_Max_Risk, fronteira_eficiente_Max_Risk = proc_data11.port_Max_Risk_055(covar, retorno_medio, max_risk=0.25, gamma=0.1)
                        # pesos_Max_Risk, fronteira_eficiente_Max_Risk = proc_data11.port_max_Sharpe_055(covar, retorno_medio)

                        # (13) ALOCAÇÃO com RISCO MÁXIMO ADMITIDO pelo investidor - Obtém os percentuais de alocacao do portfólio RISCO Máx., para um valor de patrimônio
                        #     default = 100000
                        alocacao_Max_Risk, sobra_Max_Risk = proc_data11.aloc_Otima(df1, pesos_Max_Risk, valor=100000)

                        # (14) PERFORMANCE MÁX RISK - Mede a performance do portfólio com Risco Máximo Admitido
                        retorno, volatilidade, sharpe = proc_data11.perf_Port(fronteira_eficiente_Max_Risk)
                               # fronteira_eficiente_Max_Risk foi retornada em port_Max_Risk(covar, retorno_medio), 
                               # processada no passo (9)
                        
                        # (15) Plotagens e Resultados
                        df_Max_Risk = proc_data11.df_To_Pie(pesos_Max_Risk)

                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Pesos Percentuais para o Portfólio de Risco Máx. Tolerado</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        plot_funcs1.pie_Plot_Tickers(df_Max_Risk, 'max_risk')

                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Quantidades de Ações/Cotas para o Portfólio de Risco Máx. Tolerado</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        df_aloc_Max_Risk = proc_data11.df_To_Pie(alocacao_Max_Risk)
                        plot_funcs1.pie_Plot_Tickers(df_aloc_Max_Risk, "aloc_max_risk")

                        st.markdown(''' ### Performance Portfólio de Risco Máximo Tolerado ''')
                        st.write('Retorno Anual Esperado: ', f'{retorno*100:.1f}%')
                        st.write('Volatilidade Anual: ', f'{volatilidade*100:.1f}%')
                        st.write('Índice de SHARPE: ', f'{sharpe:.2f}')
                        st.write(" ")
                        st.write(" ")
                        
                        ##### FIM PORT. RISCO MÁXIMO TOLERADO

                        # (15) Preparando os Dados para plotar o Pie Chart
                        #
                        # ->df_Max_Sharpe = proc_data11.df_To_Pie(pesos)  # Esteve inibida
                        # ->df_Min_Vol = proc_data11.df_To_Pie(pesos_Min_Vol)
                        # ->df_Max_Risk = proc_data11.df_To_Pie(pesos_Max_Risk)  # Esteve inibida

                        # (16) Plotando os Pie Charts de cada portfólio
                        #
                        #pie_Plot_Tickers(df_Max_Sharpe, "max_sharpe")
                        #pie_Plot_Tickers(df_Min_Vol, "min_vol")
                        #pie_Plot_Tickers(df_Max_Risk, "max_risk")

                        #################################

                        #df_M_S, df_M_Vol, df_M_R, \
                        #pesos, pesos_Min_Vol, pesos_Max_Risk, \
                        #alocacao_Max_Sharpe, sobra_Max_Sharpe, \
                        #alocacao_Min_Vol, sobra_Min_Vol, \
                        #alocacao_Max_Risk, sobra_Max_Risk = proc_data11.proc_Result(df1)

                        #df_M_Vol, pesos_Min_Vol, sobra_Min_Vol, \
                        #   alocacao_Min_Vol, sobra_Min_Vol = proc_data11.proc_Result(df1)

                        # plot_funcs.pie_Plot_Tickers(df_M_S, 'max_sharpe')
                        # ->st.markdown(''' ### **Portfólio de Volatilidade Mínima** ''')
                        # ->plot_funcs.pie_Plot_Tickers(df_Min_Vol, 'min_vol')

                        # Calcula retorno medio da carteira
                        # ->retorno_medio = proc_data11.xPected_Ret_Media(df1)

                        # ->df_aloc_Min_Vol = proc_data11.df_To_Pie(alocacao_Min_Vol)
                        # ->plot_funcs.pie_Plot_Tickers(df_aloc_Min_Vol, 'aloc_min_vol')

                        # (2) Calcula a Covariância de Ledoit-Wolf entre os ativos
                        # ->covar = proc_data11.cov_LW(df1)
                        # ->pesos_Min_Vol, fronteira_eficiente_Min_Vol = proc_data11.port_Min_Vol(covar, retorno_medio)

                        # ->retorno, volatilidade, sharpe = proc_data11.perf_Port(fronteira_eficiente_Min_Vol)

                        # ->st.markdown(''' ### Performance Portfólio de Vol. Mínima ''')
                        # ->st.write('Retorno(%) anual: ', round(retorno * 100, 2))
                        # ->st.write('Volatilidade(%) anual: ', round(volatilidade * 100, 2))
                        # ->st.write('Índice de SHARPE: ', round(sharpe, 2))
                        # ->st.write(" ")
                        # ->st.write(" ")

                        # (3) Calcula a Covariância de Ledoit-Wolf entre os ativos

                        # covar = proc_data11.cov_LW(df1)
                        # ->pesos, fronteira_eficiente = proc_data11.port_max_Sharpe_055(covar, retorno_medio)

                        # ->plot_funcs.pie_Plot_Tickers(df_Max_Sharpe, 'max_sharpe')
                        # ->st.markdown(''' ### **Portfólio de Máximo Índice de Sharpe** ''')
            
                        # Calcula retorno medio da carteira
                        # retorno_medio = proc_data11.xPected_Ret_Media(df1)

                        # ->retorno, volatilidade, sharpe = proc_data11.perf_Port(fronteira_eficiente)
                        # ->pesos_Max_Sharpe, fronteira_eficiente = proc_data11.port_Min_Vol(covar, retorno_medio)

                        # ->st.markdown(''' ### Performance''')
                       

                        # ->st.write('Retorno(%) anual: ', round(retorno * 100, 2))
                        # ->st.write('Volatilidade(%) anual: ', round(volatilidade * 100, 2))
                        # ->st.write('Índice de SHARPE: ', round(sharpe, 2))
                        # ->st.write(" ")
                        # ->st.write(" ")

                        st.write(" ")
                        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 22px;"><b>Visualização da Fronteira Eficiente para o Portfólio Escolhido</b></p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                        
                        st.write(" ")
                        
                        plot_funcs1.fronteira(pf2)

                    # Plota gráficos de linha dos ativos escolhidos
                    # plot_funcs.plot_02(df_acum_c_IFIX, 'acum')

                    # Processa e obtem variáveis do portfolio
                    # df_M_S, df_M_Vol, df_M_R = proc_data11.proc_Result(df1)

                    # Plota Pie Charts dos Portfolios
                    # plot_funcs.pie_Plot_Tickers(df_M_S, 'max_sharpe')
                    # plot_funcs.pie_Plot_Tickers(df_M_Vol, 'min_vol')
                    # plot_funcs.pie_Plot_Tickers(df_M_R, 'max_risk')

    # else:
        # st.stop()

# if __name__ == '__main__':
#    main()
