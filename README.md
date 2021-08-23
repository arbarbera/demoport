# Port.co DEMO
Esta é uma versão de demonstração do App para criação de Portfólios inicialmente obtidos partir da indicação de uma lista de FIIs (Fundos Imobiliários da B3)

## Objetivo
Demonstrar o potencial do aplicativo para possíveis investidores interessados em eventualmente transformá-lo num produto comercial, de modo possibilitarmos que pessoas físicas possam utilizare corretamente a Teoria de Porfólios de Markowitz, melhorando a qualidade das decisões de investimento do cidadão comum. A idéia de risco não se encontra claramente difundida entre os mais de 1.2 milhões de novos investidores do mercado de renda variável brasileiro.

## Descrição
O App já está preparado para simular portfólios de ativos (Ações, Stocks, REIts e FIIs) com base nos retornos históricos e na respectiva volatilidade histórica da lista fornecida. A versão inicial só permite a criação de carteiras organizadas por classe de ativos, sem misturá-los. A previsão é a de que, em Versões futuras, não haja essa limitação.

O aplicativo permite simular alocações em percentuais do valor total de 100 Mil unidades monetárias hipoteticamente investidas e as correspondentes quantidades de ativos a serem adquiridas via home-broker. Essas alocações são automaticamente calculadas com base nas cotações atualizadas até o dia útil anterior ao da simulação, obtidas do Yahoo Finance

As funcionalidades já suportadas pelo aplicativo contemplam estimativa do retorno anual, Índice de Sharpe e Volatilidade anual, para todas as carteiras simuladas. Além disto, há as seguintes:

1. **Alocação Ingênua (Naive Allocation)** dos ativos no portfólio, plotando pie-chart mostrando percentuais e quantidades a serem adquiridas, sempre que houver a não convergência do cálculo do índice de Sharpe (o índice de Sharpe pode divergir, quando houver retornos negativos);
2. **Alocação para Portfólio de Variância Mínima (risco mínimo)**, plotando pie-chart mostrando percentuais e quantidades a serem adquiridas;
3. **Alocação para Portfólio de Máximo Índice de Sharpe**, plotando pie-chart mostrando percentuais e quantidades a serem adquiridas;
4. **Alocação para Portfólio de Máximo Risco Suportado, dada uma Taxa Livre de Risco**, plotando pie-chart mostrando percentuais e quantidades a serem adquiridas;
5. **Alocação para Portfólio de Máximo Risco Suportado, forçada a presença obrigatória de determinado ativo no portfólio**, plotando pie-chart dado com percentuais e quantidades a serem adquiridas; e
6. A**locação para Portfólio com Concentração Forçada em determinados segmentos do mercado** (fornecidos pelo cliente em formato texto), plotando pie-chart e quantidades a serem adquiridas.

Obs.: nesta demonstração, apenas o item 2 está funcional.
