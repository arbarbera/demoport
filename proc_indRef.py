# Função que retorna um df com o Retorno Medio Diario
import pandas as pd
import numpy as np
# Date & Time Pkgs
import time
import datetime as dt
from datetime import datetime, timedelta, date


def ret_Med_Diario(df):
    # Cria dataframe de retornos diarios a partir de df vindo do yFinance
    colunas = list(df.columns)
    dfrd = pd.DataFrame(df[colunas[0]].pct_change(), columns=[colunas[0]])
    col = colunas[1]

    for col in colunas:
        dfrd[col] = df[col].pct_change()

    return dfrd

# Função que retorna um df com o Retorno Medio Diario
# Cria dataframe de retornos acumulados a partir de df vindo do yFinance


def ret_Acum_Diario(df):
    colunas = list(df.columns)
    # hgre11_daily_cum = (hgre11_d_ret + 1).cumprod()
    # df1[col].pct_change()+1
    dfr_ac = pd.DataFrame(df[colunas[0]].pct_change().cumprod(), columns=[colunas[0]])
    if len(colunas) > 1:
        col = colunas[1]

    for col in colunas:
        dfr_ac[col] = (df[col].pct_change() + 1).cumprod()

    return dfr_ac

# Função que trata e agrega o IFIX à lista de ativos p/ comparação
# Ajusta índice antes de receber o IFIX


def incl_Ifix(df):
    df.reset_index(inplace=True)
    # Lendo o arquivo do IFIX
    ifix = pd.read_csv('IFIX_PREP.csv')
    # Converte valores do IFIX
    ifix['Valor'] = ifix['Valor'].astype(np.float64)
    # Compatibiliza as colunas no padrao yFinance
    ifix.columns = ['Date', 'IFIX']
    # Converte a data do IFIX para o padrao yFinance
    ifix['Date'] = pd.to_datetime(ifix['Date'], format='%d/%m/%Y')
    # Anexa a coluna do IFIX
    df = pd.merge(df, ifix, on=['Date'], how='left')
    # Indexa DF1 já com IFIX adicionado pela coluna Date (datetime index)
    df.set_index('Date', inplace=True)
    # Uniformiza decimais
    df = df.round(decimals=2)

    # Limpa o '.SA' das colunas do df
    ativos = df.columns
    colunas = []
    for i in range(len(ativos)):
        a = ativos[i].replace('.SA', '')
        colunas.append(a)

    df.columns = colunas

    df_r_acum = ret_Acum_Diario(df)

    return df_r_acum
