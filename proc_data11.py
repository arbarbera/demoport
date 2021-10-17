# Finance Pkgs
import yfinance as yf
from yfinance import shared
import pypfopt
import numpy as np
from pypfopt.expected_returns import mean_historical_return
from pypfopt import risk_models, plotting, expected_returns, EfficientFrontier, objective_functions
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from cvxpy import *

# Data Pkgs
import pandas as pd


# Funções Disponíveis
#

# Calcula Retorno Anual Medio ESPERADO dos ativos escolhidos
#

def xPected_Ret_Media(df):
    rmed = expected_returns.mean_historical_return(df)

    return rmed

# Calcula a Covariância de Ledoit-Wolf
#


def cov_LW(df):
    S = CovarianceShrinkage(df).ledoit_wolf()

    return S

# Calcular Índice de Sharpe Máximo (Sharpe Ratio) e retorna Pesos. Relação retorno x risco deve ser > 0.5 (estudável)
#


def port_max_Sharpe_055(S, r):

    ef = EfficientFrontier(r, S)

    min_weight, max_weight = 0.01, 0.34

    weights = ef.nonconvex_objective(
        objective_functions.sharpe_ratio,
        objective_args=(ef.expected_returns, ef.cov_matrix),
        constraints=[
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # sum to 1
            {"type": "ineq", "fun": lambda w: w - min_weight},  # greater than min_weight
            {"type": "ineq", "fun": lambda w: max_weight - w},  # less than max_weight
        ],
    )

    peso_ajustado = ef.clean_weights()
    return peso_ajustado, ef


def port_Max_Sharpe(S, r):
    ef = EfficientFrontier(r, S)
    ef.add_objective(objective_functions.L2_reg, gamma=0.5)  # minimiza zeros nos pesos retornados
    pesos = ef.max_sharpe()
    peso_ajustado = ef.clean_weights()

    return peso_ajustado, ef  # pesos de alocação

# Calcula alocaçao otima. Retorna quantidades de ativos e sobra (valor não alocado)
# pesos = peso_ajustado vindos de port_Max_Sharpe(S, r)
#


def aloc_Otima(df, pesos, valor=100000):
    precos = get_latest_prices(df)
    ad = DiscreteAllocation(pesos, precos, valor)

    #alocacao, sobra = ad.lp_portfolio('CVXPY')
    alocacao, sobra = ad.lp_portfolio()
    #alocacao, sobra = ad.greedy_portfolio()

    return alocacao, sobra

# Performance do portfolio de Indice de Sharpe Máximo
#


def perf_Port(ef):
    eRet, aVol, sharpe = ef.portfolio_performance(verbose=False)  # Fronteira de Markowitz

    return eRet, aVol, sharpe

# Retorna os pesos percentuais do portfólio de Mínima Volatilidade
#


def port_Min_Vol(S, r):
    ef = EfficientFrontier(r, S)
    ef.add_objective(objective_functions.L2_reg, gamma=0.1)  # minimiza zeros nos pesos retornado
    pesos = ef.min_volatility()
    peso_ajustado = ef.clean_weights()

    return peso_ajustado, ef  # pesos de alocação e objeto ef

# Calcula o número de ações a serem compradas, segundo os pesos obtidos para o portfólio de mínima volatilidade
# e respectivo saldo em conta (USD)
#
# pesos = peso_ajustado vindos de port_Min_Vol(S, r)
#


def aloc_Min_Vol(df, pesos, valor=100000):
    valor_alocar = valor
    precos = get_latest_prices(df)
    ad = DiscreteAllocation(pesos, precos, valor_alocar)

    # alocacao, sobra = ad.lp_portfolio() # solver default to 'GLPK_MI'
    # alocacao, sobra = ad.lp_portfolio("CVXPY")
    alocacao, sobra = ad.greedy_portfolio()

    return alocacao, sobra

# Retorna os pesos percentuais do portfólio de Risco Máximo Admitido pelo investidor (default=0.25 (25%))
#


def port_Max_Risk(S, rmed, max_risk=0.80, gamma=0.1):
    ef = EfficientFrontier(rmed, S)
    ef.add_objective(objective_functions.L2_reg, gamma=gamma)  # minimiza zeros nos pesos retornado

    # Max_Risk = 0.40 # Abaixo o estimador não converge
    ef.efficient_risk(target_volatility=max_risk)

    pesos = ef.max_sharpe()
    peso_ajustado = ef.clean_weights()

    return peso_ajustado, ef  # pesos de alocação e objeto ef


def port_Max_Risk_055(S, rmed, max_risk=0.60, gamma=0.1):
    ef = EfficientFrontier(rmed, S)
    ef.efficient_risk(target_volatility=max_risk)

    ####
    min_weight, max_weight = 0.01, 0.20

    weights = ef.nonconvex_objective(
        objective_functions.sharpe_ratio,
        objective_args=(ef.expected_returns, ef.cov_matrix),
        constraints=[
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # sum to 1
            {"type": "ineq", "fun": lambda w: w - min_weight},  # greater than min_weight
            {"type": "ineq", "fun": lambda w: max_weight - w},  # less than max_weight
        ],
    )

    peso_ajustado = ef.clean_weights()
    return peso_ajustado, ef  # pesos de alocação e objeto ef


# Criando o dataframe para o Pie Chart do Portfólio
#
def df_To_Pie(pesos):  # pesos é OrderedDict

    port = list(pesos.items())
    # Monta dataframe de saída
    df = pd.DataFrame(port, columns=['Ticker', 'Peso'])

    return df


# Fluxo de Execução do Processamento :

# (0) Limpa o '.SA' das colunas do df
#ativos = df.columns
#colunas = []
# for i in range(len(ativos)):
#    a = ativos[i].replace('.SA', '')
#    colunas.append(a)

#df.columns = colunas

# (1) Calcula retorno medio anual de cada ativo da lista de ativos escolhidos
#retorno_medio = xPected_Ret_Media(df)

# (2) Calcula a Covariância de Ledoit-Wolf entre os ativos
#covar = cov_LW(df)

# (3) Obtém os PESOS do portfólio de Máx. Indice de Sharpe e da fronteira eficiente
#pesos, fronteira_eficiente = port_max_Sharpe_055(covar, retorno_medio)

# (4) ALOCAÇÃO - Obtém os percentuais de alocacao do portfólio com Máx. Indice de Sharpe, para um valor de patrimônio
#     default = 100000
#alocacao_Max_Sharpe, sobra_Max_Sharpe = aloc_Otima(df, pesos, valor=100000)

# (5) PERFORMANCE MÁX. SHARPE - Mede a performance do portfólio com Máx. Indice de Sharpe
#ret_Max_Sh, vol_Max_Sh, max_Sharpe = perf_Port(fronteira_eficiente)
# fronteira_eficiente foi retornada em port_Max_Sharpe(covar, retorno_medio), processada no passo (3)
#
# print("Retorno Anual Esperado: ", f'{ret_Max_Sh*100:.1f}%')
# print("Volatilidade Anual: ", f'{vol_Max_Sh*100:.1f}%')
# print("Índice de Sharpe: ", f'{max_Sharpe:.2f}')

# (6) Obtém os PESOS do portfólio de Mín. Volatilidade e da fronteira eficiente correspondente
#pesos_Min_Vol, fronteira_eficiente_Min_Vol = port_Min_Vol(covar, retorno_medio)

# (7) ALOCAÇÃO MÍN. VOLATILIDADE - Obtém os percentuais de alocacao do portfólio com Mín. Volatilidade, para um valor de patrimônio
#     default = 100000
#alocacao_Min_Vol, sobra_Min_Vol = aloc_Otima(df, pesos_Min_Vol, valor=100000)

# (8) PERFORMANCE MÍN. VOLATILIDADE - Mede a performance do portfólio com Mín. Volatilidade
#retorno, volatilidade, sharpe = perf_Port(fronteira_eficiente_Min_Vol)
#          # fronteira_eficiente_Min_Vol foi retornada em port_Min_Vol(covar, retorno_medio), processada no passo (6)
#
#          # print("Retorno Anual Esperado: ", f'{retorno*100:.1f}%')
#          # print("Volatilidade Anual: ", f'{volatilidade*100:.1f}%')
#          # print("Índice de Sharpe: ", f'{sharpe:.2f}')

# (9) Obtém os PESOS do portfólio de Risco Máx. tolerado pelo Investidor e da respectiva fronteira eficiente
#pesos_Max_Risk, fronteira_eficiente_Max_Risk = port_Max_Risk(covar, retorno_medio)

# (10) ALOCAÇÃO com RISCO MÁXIMO ADMITIDO pelo investidor - Obtém os percentuais de alocacao do portfólio RISCO Máx., para um valor de patrimônio
#     default = 100000
#alocacao_Max_Risk, sobra_Max_Risk = aloc_Otima(df, pesos_Max_Risk, valor=100000)

# (11) PERFORMANCE MÁX RISK - Mede a performance do portfólio com Risco Máximo Admitido
#retorno, volatilidade, sharpe = perf_Port(fronteira_eficiente_Max_Risk)
#          # fronteira_eficiente_Max_Risk foi retornada em port_Max_Risk(covar, retorno_medio), processada no passo (9)
#
#          # print("Retorno Anual Esperado: ", f'{retorno*100:.1f}%')
#          # print("Volatilidade Anual: ", f'{volatilidade*100:.1f}%')
#          # print("Índice de Sharpe: ", f'{sharpe:.2f}')

# (12) Preparando os Dados para plotar o Pie Chart
#

#df_Max_Sharpe = df_To_Pie(pesos)  # Esteve inibida
#df_Min_Vol = df_To_Pie(pesos_Min_Vol)
#df_Max_Risk = df_To_Pie(pesos_Max_Risk)  # Esteve inibida

# (13) Plotando os Pie Charts de cada portfólio
#
# pie_Plot_Tickers(df_Max_Sharpe, "max_sharpe")
# pie_Plot_Tickers(df_Min_Vol, "min_vol")
# pie_Plot_Tickers(df_Max_Risk, "max_risk")

#return df_Max_Sharpe, df_Min_Vol, df_Max_Risk, \
#    pesos, pesos_Min_Vol, pesos_Max_Risk,   \
#    alocacao_Max_Sharpe, sobra_Max_Sharpe,  \
#    alocacao_Min_Vol, sobra_Min_Vol,  \
#    alocacao_Max_Risk, sobra_Max_Risk

# return df_Min_Vol, pesos_Min_Vol, sobra_Min_Vol, alocacao_Min_Vol, sobra_Min_Vol