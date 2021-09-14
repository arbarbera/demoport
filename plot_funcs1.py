
# Plotly Pie Chart
#
# Cores testadas (px.colors.sequential.): Dense, Emrld, Blugrn, Sunsetdark, Agsunset, Brwnyl. Viridis, YlOrRd
# Cores testadas (px.colors.diverging.): BrBG, PRGn, Spectral, Picnic, Portland, RdBu
# Cores testadas (px.colors.cyclical.): Twilight, IceFire
#
# fig = px.pie(df1, values='Peso', names='Ticker', hover_name='Ticker', color_discrete_sequence=px.colors.sequential.balance,
#              hole=0.6)
# fig = px.pie(df1, values='Peso', names='Ticker', hover_name='Ticker', color_discrete_sequence=px.colors.cyclical.mygbm,
#              hole=0.6)

# Streamlit
import streamlit as st
import streamlit.components.v1 as stc

# Ploting Pkgs
#import plotly.graph_objects as go
import plotly.express as px

#import plotly.plotly as py
#from plotly.offline import plot
#from chart_studio import plotly
#import plotly.offline as pyoff
import plotly.graph_objects as go
# import plotly.figure_factory as ff 

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import cm
from matplotlib.pyplot import figure

import seaborn as sns

import pandas as pd
# def plot_01(df):
#  def format_tick_labels(y, pos):
#    return '{0:.2f}'.format(y)
#
#  # Uniformiza decimais
#  df_cleaned = df.round(decimals=2)
#  ativos = df_cleaned.columns
#
#  fig = plt.figure(figsize=(8, 5))
#  plt.title('Cotações dos Ativos da Carteira', fontsize=12, color='grey')
#  ax = plt.gca()  # get current axis
#
#  ax.yaxis.set_major_formatter(FuncFormatter(format_tick_labels))
#
#  for i in ativos:
#    plt.plot(df_cleaned.index, df[i])
#
#  plt.xlabel('Datas', fontsize=10, color='grey')
#  plt.xticks(rotation=-15, fontsize=6)
#  plt.yticks(rotation=60, fontsize=6)
#  plt.ylabel('Preço de Fechamento', fontsize=10, color='grey')
#  leg = plt.legend(labels=ativos, fontsize=6)
#
#  st.pyplot(fig)


def plot_02(df, period='diaria'):

  def format_tick_labels(y, pos):
    return '{0:.2f}'.format(y)

  if period == 'diaria':
    tit_1 = 'Evolução das Cotações'
    tit_2 = 'Preços de Fechamento'
  else:
    tit_1 = 'Variação (%) Acumulada'
    tit_2 = 'Variação (%) Pr. de Fechamento'
  # Uniformiza decimais

  ativos = df.columns

  my_dpi = 96
  width_fig = 680 / my_dpi
  height_fig = 480 / my_dpi

  fig = plt.figure(figsize=(width_fig, height_fig), dpi=my_dpi * 2)

  plt.title(tit_1, fontsize=10, color='grey')
  ax = plt.gca()  # get current axis
  ax.yaxis.set_major_formatter(FuncFormatter(format_tick_labels))

  c = 'black'
  for i in ativos:
    if i == 'IFIX':
      plt.plot(df.index, df[i], color=c)
    else:
      plt.plot(df.index, df[i])
      plt.xlabel('Datas', fontsize=10, color='grey')
      plt.xticks(rotation=-15, fontsize=7)
      plt.yticks(rotation=60, fontsize=7)
      plt.ylabel(tit_2, fontsize=10, color='grey')

  ativos.sort_values
  leg = plt.legend(labels=ativos, fontsize=7, loc="upper left")

  st.pyplot(fig)
  return fig
  # plt.show()


def pie_Plot_Tickers(df, tipo_portfolio, hole=0.3):

  # Limpa o '.SA' das linha do df
  df['Ticker'] = df['Ticker'].str.replace('.SA', '')
  df.sort_values('Ticker')

  # Texto central
  txt_Centro = 'Pesos'
  legend_order = 'normal'

  if tipo_portfolio == "max_sharpe":
    color_pattern = px.colors.diverging.RdBu
    titulo_grafico = " % - Máximo Índice de Sharpe"
    compl = ""
  elif tipo_portfolio == "aloc_max_sharpe":
    color_pattern = px.colors.sequential.RdBu
    titulo_grafico = " em Qtdes. de Ações por $100 mil "
    compl = "Porfólio de Máx. Indice de Sharpe"
    txt_Centro = 'Nº de Ações'
    legend_order = 'reversed'
  elif tipo_portfolio == "min_vol":
    titulo_grafico = " % - Volatilidade Mínima (Histórica)"
    color_pattern = px.colors.sequential.dense
    compl = ""
  elif tipo_portfolio == "aloc_min_vol":
    color_pattern = px.colors.sequential.dense
    titulo_grafico = " em Qtdes. de Ações por $100 mil "
    compl = "Porfólio de Vol. Mínima Histórica"
    txt_Centro = 'Nº de Ações'
    legend_order = 'reversed'
  elif tipo_portfolio == "max_risk":
    color_pattern = px.colors.sequential.Emrld
    titulo_grafico = " % - Risco Máximo (default=20%)"
    compl = ""
  elif tipo_portfolio == "aloc_max_risk":
    color_pattern = px.colors.sequential.Emrld
    titulo_grafico = " em Qtdes. de Ações por $100 mil "
    compl = "Porfólio de Máx. Risco Tolerado de 20% por Ativo"
    txt_Centro = 'Nº de Ações'
    legend_order = 'reversed'

  df = df[df['Ticker'] != '']

  df.drop_duplicates('Ticker', ignore_index=True, inplace=True)

  #st.write(df)

  df.sort_values(by=['Ticker'], inplace=True)

  legend_itens = df.Ticker.values
  legend_itens.sort()

  fig = px.pie(df, names='Ticker', values='Peso', hover_name='Ticker',
               color_discrete_sequence=color_pattern, hole=hole)

  background_color = "white"
  back_plot_color = "rgba(0, 0, 0, 0)"

  fig.update_layout(title_text="Alocação " + titulo_grafico,
                    title_x=0,
                    title_font_size=17,
                    legend_title='Tickers',
                    annotations=[dict(text=txt_Centro, x=0.5, y=0.5, font_size=18, showarrow=False)],  # Texto central
                    showlegend=True,
                    width=600,
                    height=600,
                    #margin=dict(l=50, r=0, b=0, t=25),
                    margin=dict(l=0, r=0, b=0, t=25),
                    legend=dict(bgcolor="white"),
                    paper_bgcolor=background_color,
                    plot_bgcolor=back_plot_color,
                    font=dict(color='#383635', size=16)
                    )

  if (tipo_portfolio == 'aloc_min_vol')|(tipo_portfolio == 'aloc_max_sharpe')|(tipo_portfolio == 'aloc_max_risk'):
    fig.update_traces(textinfo='value')

  # fig.show()
  st.plotly_chart(fig)
  return fig


def view_Table(df):
    # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv')
    '''
    df.style.format(precision=0, na_rep='MISSING', thousands=".",
                formatter={('Rebalanceamento', 'Buy&Hold'): "{:.2f}" #,
                           #('Regression', 'Non-Tumour'): lambda x: "$ {:,.1f}".format(x*-1e6)
                          })
    

    df.style.format({"Rebalanceamento": "{:,.2f}", 
                          "Buy&Hold": "{:,.2f}"                          
    })

    '''

    with pd.option_context('display.float_format', '{:0.2f}%'.format):

      df.reset_index(drop=False, inplace=True)
      
      val = []
      for i in range(len(df.columns)):
            val.append(df[df.columns[i]])

      fig = go.Figure(data=[go.Table(
          #header=dict(values=list(df.columns),

          header=dict(values=list(df.columns),
                      fill_color='red',
                      font_color='white',
                      align='left'),
          # cells=dict(values=[df.Rank, df.State, df.Postal, df.Population],
          cells=dict(values=[val[i] for i in range(len(val))],
                     fill_color='lavender'))
      ])

      fig.update_layout(title={'text': 'Indicadores do Portfólio', 'x': 0,
                             'xanchor': 'left', 'yanchor': 'top'},
                      margin=dict(t=50, b=0, l=0, r=0),
                      width=1000,
                      height=300
                      )
      st.plotly_chart(fig)
    

def view_Table2(df):

  #df = df.tail(30)
  #df.iloc[::-1]

  df = df.sort_values(by='Date',ascending=False)

  # Limpa o '.SA' das colunas do df

  ativos = df.columns
  colunas = []
  for i in range(len(ativos)):
    a = ativos[i].replace('.SA', '')
    colunas.append(a)

  df.columns = colunas

  val = []
  col_W = []
  col_O = []

  for i in range(len(df.columns)):
    val.append(df[df.columns[i]])
    col_O.append(i)

    if i == 0:
      col_W.append(15)
    else:
      col_W.append(8)

  fig = go.Figure(data=[go.Table(
      columnorder=col_O,
      columnwidth=col_W,
      header=dict(values=list(df.columns),
                  fill_color='#F63A33',  # Default system theme -> #F63366
                  font_color='white',
                  align='left'),

      # cells=dict(values=[df.Rank, df.State, df.Postal, df.Population],
      #cells=dict(values=[val[i] for i in range(len(val)-1,-1,-1)],
      cells=dict(values=[val[i] for i in range(len(val))],
                 fill_color='lavender',
                 align='left'))
  ])

  fig.update_layout(title={'text': 'Preços de Fechamento', 'x': 0,
                           'xanchor': 'left', 'yanchor': 'top'},
                    margin=dict(t=50, b=0, l=0, r=0),
                    width=1000,
                    height=300
                    )

  # fig.show()
  st.plotly_chart(fig)