# Simulação da COVID-19 com Previsão de Infecção

Este repositório contém uma simulação da propagação da COVID-19 usando o modelo epidemiológico SIRD (Suscetíveis, Infectados, Recuperados, Mortos) aplicada ao dataset `facebook_combined.txt`, que representa uma rede social com 4039 nós, 88234 arestas, densidade de 0.0108, assortatividade de 0.0636, diâmetro 8 e conectado. O projeto integra a simulação SIRD com previsão de infecção (link prediction) para identificar o próximo nó a ser infectado em cada iteração, usando o número de vizinhos em comum como critério, e inclui visualização interativa do grafo.

## Funcionalidades
- **Simulação SIRD**: Modela a propagação da doença com taxas de infecção (`beta=0.3`), recuperação (`gamma=0.1`) e mortalidade (`alpha=0.05`) usando `ndlib`.
- **Previsão de Infecção**: Prevê um único nó suscetível como o próximo a ser infectado por iteração, com base no maior número de vizinhos em comum com nós infectados.
- **Visualização Interativa**: Gera um grafo interativo em HTML com `pyvis`, onde:
  - Suscetíveis: azul
  - Infectados: vermelho
  - Recuperados: verde
  - Mortos: preto
  - Nó previsto: destacado com tamanho maior e borda

Toda a explicação esta disponível no [notebook de simulação](Simulação_da_COVID_19 (1).ipynb) ou no [Notebook Colab](https://colab.research.google.com/drive/1fTmTeAYljoEoe483SzvV4Ky72yUkj23a?usp=sharing).
