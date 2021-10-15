# Origem notebook CUSTOM - INDICADORES (Base - 25_Back..._Parte_2(BT))
# Imports
#

import streamlit as st

def indic (dfi, data_i, data_f, rf=4.86):

    import bt
    import yfinance as yf

    import datetime as dt 
    # import statistics as st

    import pandas as pd
    import matplotlib
    import plotly

    matplotlib.style.use('seaborn-darkgrid')
    # get_ipython().run_line_magic('matplotlib', 'inline')  # só para o jupyter


    # ## Funções Utilitárias

    # Consulta preço do CDI na base do BCB

    @st.cache(suppress_st_warning=True)
    def consulta_bc(codigo_bcb):
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(codigo_bcb)
        df = pd.read_json(url)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df.set_index('data', inplace=True)
        return df


    # Calcula CDI acumulado no periodo

    def cdi_acumulado(data_inicio, data_fim):
        cdi = consulta_bc(12)
        cdi_acumulado = (1 + cdi[data_inicio : data_fim] / 100).cumprod()
        cdi_acumulado.iloc[0] = 1
        return cdi_acumulado


    # Função para converter lista em dicionário
    # list to dict
    def Convert(a):
        it = iter(a)
        res_dct = dict(zip(it, it))
        return res_dct

    # Plota a evolução dos portifolios com e sem alocação em renda fixa

    def bt_estrat_plot(estrat, x_size, y_size):
        fig = estrat.plot(title="Evolucao Histórica do Preço de Fechamento Ajustado (Adj. Close)\n Rebalanceamento da Carteira c/ Renda Fixa X apenas Buy&Hold\n", figsize=(18, 10), fontsize=12)
        fig.axes.title.set_size(x_size)
        fig.axes.legend(fontsize=y_size);
        return fig


    #####  Parâmetros de entrada
    data_inicio = data_i
    data_fim    = data_f
    tickers = dfi.columns
    risk_free_perc_interest = rf
    ##### Parâmetros

    # Renda Fixa 
    cdi = cdi_acumulado(data_inicio=data_inicio, data_fim=data_fim)

    # Prepara para o yFinance
    #tickers_carteira = [t+'.SA' for t in tickers]

    tickers_carteira = [ticker for ticker in tickers if ticker != 'Date']

    # Obtém as cotações dos preços ajustados
    carteira = yf.download(tickers_carteira, start=data_inicio, end=data_fim)['Adj Close']

    # Inclui o CDI na carteira
    carteira['renda_fixa'] = cdi

    # Ex. CPTS11 com dados insuficientes no período. Eliminandoa coluna
    # df.drop('column_name', axis=1, inplace=True)
    # CPTS11 com dados insuficientes no período. Eliminandoa coluna
    # carteira.drop('CPTS11.SA', axis=1, inplace=True)

    # Retira o sufixo
    carteira.columns = carteira.columns.str.rstrip('.SA')

    ### Começa o backtesting
    carteira.dropna(inplace=True)
             
    # Cria lista com ativos e respectivos pesos iniciais e converte em dict
    tam = len(carteira.columns)
    j = 1/tam
    lst = [[i,j] for i in carteira.columns]

    flat_list = [item for sublist in lst for item in sublist] # Transforma uma lista de listas muma lista única
    super = Convert(flat_list)

    # Alimenta bt com ativos e pesos iniciais usando **kwargs
    bt.algos.WeighSpecified(**super)

    # Monta as duas estratégias a serem submetidas ao portfolio
    rebalanceamento = bt.Strategy('rebalanceamento', 
                    [bt.algos.RunMonthly(run_on_end_of_period=True),
                     bt.algos.SelectAll(),
                     bt.algos.CapitalFlow(100000),
                     bt.algos.WeighSpecified(**super),
                     bt.algos.Rebalance()])

    buy_hold = bt.Strategy('Buy&Hold', 
                       [ bt.algos.RunOnce(),
                         bt.algos.SelectAll(),
                         bt.algos.WeighEqually(),
                         bt.algos.Rebalance()]
                        )

    # Cria as estratégias
    bt1 = bt.Backtest(rebalanceamento, carteira)

    colunas = list(carteira.columns)
    bt2 = bt.Backtest(buy_hold, carteira[colunas])

    # Armazena em resultados
    resultados = bt.run(bt1, bt2);

    # Tesouro IPCA+ 2055
    resultados.set_riskfree_rate(rf=risk_free_perc_interest)

    # Operações efetuadas pelo robot bt dentro das estratégias
    resultados.get_transactions()

    # ## Estatísticas
    estats = resultados.stats

    df_start_end = estats['start':'end']

    # Ajusta as datas para tipo datetime
    df = df_start_end.copy()
    df['rebalanceamento'] = pd.to_datetime(df['rebalanceamento'].dt.strftime('%Y-%m-%d'))
    df['Buy&Hold'] = pd.to_datetime(df['Buy&Hold'].dt.strftime('%Y-%m-%d'))
    df_start_end = df.copy()

    # Separa os dataframes específicos dos indicadores para posterior impressão
    df_rf = estats['rf':'rf']


    # Retorno Total
    df_ind = estats['total_return':'total_return']
    df_total_return = df_ind.copy()

    df_total_return.loc['total_return':'total_return', 'Buy&Hold'].values[0]
    
    with pd.option_context('display.float_format', '%{:0.2f}'.format):
        rebal = round(float(df_total_return.loc['total_return':'total_return', 'rebalanceamento'].values[0]), 2)
        df_total_return.loc['total_return':'total_return', 'rebalanceamento'] = rebal*100.00
        
        buy = round(float(df_total_return.loc['total_return':'total_return', 'Buy&Hold'].values[0]), 2)
        df_total_return.loc['total_return':'total_return', 'Buy&Hold'] = buy*100.00 

    
    # CAGR
    df_ind = estats['cagr':'cagr']
    df_cagr = df_ind.copy()

    with pd.option_context('display.float_format', '{:0.2f}%'.format):
        rebal = round(float(df_cagr.loc['cagr':'cagr', 'rebalanceamento'].values[0]), 2)
        df_cagr.loc['cagr':'cagr', 'rebalanceamento'] = rebal*100.00
        # print(rebal)

        buy = round(float(df_cagr.loc['cagr':'cagr', 'Buy&Hold'].values[0]), 2)
        df_cagr.loc['cagr':'cagr', 'Buy&Hold'] = buy*100.00
        
    # Queda Máxima (Máx. Drawdown)
    df_ind = estats.loc['max_drawdown':'max_drawdown', ['rebalanceamento', 'Buy&Hold']]
    df_max_drawdown = df_ind.copy()

    with pd.option_context('display.float_format', '{:0.2f}%'.format):
        rebal = round(float(df_max_drawdown.loc['max_drawdown':'max_drawdown', 'rebalanceamento'].values[0]), 2)
        df_max_drawdown.loc['max_drawdown':'max_drawdown', 'rebalanceamento'] = rebal*100.00
        # print(rebal)

        buy = round(float(df_max_drawdown.loc['max_drawdown':'max_drawdown', 'Buy&Hold'].values[0]), 2)
        df_max_drawdown.loc['max_drawdown':'max_drawdown', 'Buy&Hold'] = buy*100.00
       
    # Nº Médio de Dias de Queda (Drawdown)
    df_avg_drawdown_days = estats['avg_drawdown_days':'avg_drawdown_days']
    df_avg_drawdown_days
    
    # Melhor e Pior Mês
    df_ind = df_best_worst_month = estats.loc['best_month':'worst_month']
    df_best_worst_month = df_ind.copy()

    with pd.option_context('display.float_format', '{:0.4f}%'.format):
        rebal1 = round(float(df_best_worst_month.loc['best_month':'best_month', 'rebalanceamento'].values[0]), 4)
        rebal2 = round(float(df_best_worst_month.loc['worst_month':'worst_month', 'rebalanceamento'].values[0]), 4)

        df_best_worst_month.loc['best_month':'best_month', 'rebalanceamento'] = rebal1*100
        df_best_worst_month.loc['worst_month':'worst_month', 'rebalanceamento'] = rebal2*100
        
        buy1 = round(float(df_best_worst_month.loc['best_month':'best_month', 'Buy&Hold'].values[0]), 4)
        buy2 = round(float(df_best_worst_month.loc['worst_month':'worst_month', 'Buy&Hold'].values[0]), 4)

        df_best_worst_month.loc['best_month':'best_month', 'Buy&Hold'] = buy1*100
        df_best_worst_month.loc['worst_month':'worst_month', 'Buy&Hold'] = buy2*100

    # Índice de Sharpe Anual
    df_ind = estats['yearly_sharpe':'yearly_sharpe']
    df_yearly_sharpe = df_ind.copy()

    with pd.option_context('display.float_format', '{:0.2f}%'.format):
        rebal = round(float(df_yearly_sharpe.loc['yearly_sharpe':'yearly_sharpe', 'rebalanceamento'].values[0]), 2)
        df_yearly_sharpe.loc['yearly_sharpe':'yearly_sharpe', 'rebalanceamento'] = rebal*1.00
        # print(rebal)

        buy = round(float(df_yearly_sharpe.loc['yearly_sharpe':'yearly_sharpe', 'Buy&Hold'].values[0]), 2)
        df_yearly_sharpe.loc['yearly_sharpe':'yearly_sharpe', 'Buy&Hold'] = buy*1.00
        # print(df_yearly_sharpe)

    # Concatenando tudo
    with pd.option_context('display.float_format', '{:0.2f}%'.format):

        df_portf_stats = pd.concat([df_start_end, df_rf, df_total_return, df_cagr, df_yearly_sharpe, df_max_drawdown, df_avg_drawdown_days, df_best_worst_month])
        df = df_portf_stats.copy()
        ind = ['Data Inicial', 'Data Final', 'Tx. Livre de Risco ('+r'%'+' aa.)', 'Retorno Total ('+r'%'+' no período)', 'CAGR ('+r'%'+' aa.)', 'Indice de Sharpe Anualizado', \
        'Queda Máxima ('+r'%'+' aa.)', 'Dias de Queda', 'Rentab. Melhor Mês ('+r'%'+' aa.)', 'Rentab. Pior Mês ('+r'%'+' aa.)']
        df.index = ind

        df[['rebalanceamento', 'Buy&Hold']]
        df.loc['Data Inicial']['rebalanceamento'] = df.loc['Data Inicial']['rebalanceamento'].strftime('%Y-%m-%d')
        df.loc['Data Inicial']['Buy&Hold'] = df.loc['Data Inicial']['Buy&Hold'].strftime('%Y-%m-%d')
        df.loc['Data Final']['rebalanceamento'] = df.loc['Data Final']['rebalanceamento'].strftime('%Y-%m-%d')
        df.loc['Data Final']['Buy&Hold'] = df.loc['Data Final']['Buy&Hold'].strftime('%Y-%m-%d')

    return df, bt_estrat_plot(resultados, 20, 10)