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

# Performance do portfolio
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


# Criando o dataframe para o Pie Chart do Portfólio
#
def df_To_Pie(pesos):  # pesos é OrderedDict

    port = list(pesos.items())
    # Monta dataframe de saída
    df = pd.DataFrame(port, columns=['Ticker', 'Peso'])

    return df