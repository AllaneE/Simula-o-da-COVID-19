import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import defaultdict
import requests
from io import StringIO

st.set_page_config(page_title="Projeto Simulação SEIR - COVID-19", layout="wide")

st.title("Simulação Epidemia SEIR em Rede - COVID-19")
st.markdown("""
Este projeto simula a propagação de uma epidemia usando o modelo SEIR em uma rede social real (dataset Facebook).
Utilizamos métricas de teoria de redes para analisar o grafo antes e depois da simulação, além de aplicar link prediction para prever quais nós estão em maior risco de infecção.
""")

@st.cache_data
def grafos_e_dados():
    G_original = nx.read_graphml("grafo_original.graphml")
    G_seir = nx.read_graphml("grafo_seir.graphml")
    df_status = pd.read_csv("status.csv")
    df_top10 = pd.read_csv("top10.csv")
    return G_original, G_seir, df_status, df_top10

try:
    G_original, G_seir, df_status, df_top10 = grafos_e_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

def grafo_pyvis(G, height=600, width="100%"):
    net = Network(height=f"{height}px", width=width, notebook=False)
    net.from_nx(G)
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 250,
          "springConstant": 0.001
        },
        "minVelocity": 0.75
      }
    }
    """)
    net.show("temp.html")
    with open("temp.html", "r") as f:
        html_str = f.read()
    st.components.v1.html(html_str, height=height+50)

st.header("Grafo Original")
st.write(f"Número de nós: {G_original.number_of_nodes()}")
st.write(f"Número de arestas: {G_original.number_of_edges()}")
st.write(f"Densidade do grafo: {nx.density(G_original):.6f}")
st.write(f"Grau médio do grafo: {nx.average_clustering(G_original):.6f}")
grafo_pyvis(G_original)

st.header("Grafo após simulação SEIR")
st.write(f"Número de nós: {G_seir.number_of_nodes()}")
st.write(f"Número de arestas: {G_seir.number_of_edges()}")
st.write(f"Densidade do grafo: {nx.density(G_seir):.6f}")
st.write(f"Grau médio do grafo: {nx.average_clustering(G_seir):.6f}")

status_cont = df_status['status_label'].value_counts()
st.subheader("Quantidade por estado:")
st.table(status_cont)

color_map = {'Suscetível': '#669BBC', 'Exposto': '#F4A261', 'Infectado': '#C1121F', 'Removido': '#4A5759'}
colors = []
for node in G_seir.nodes():
    status_label = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
    if len(status_label) > 0:
        colors.append(color_map.get(status_label[0], '#999999'))
    else:
        colors.append('#999999')

for i, node in enumerate(G_seir.nodes()):
    G_seir.nodes[node]['color'] = colors[i]

grafo_pyvis(G_seir)

st.header("Top 10 nós mais infectados")
st.table(df_top10)
st.subheader("Grafo com possíveis nós")
color_risco_map = {'Infectado': '#C1121F', 'Removido': '#4A5759', 'Suscetível': '#669BBC', 'Em risco': 'purple', 'Exposto': '#F4A261'}
G_risco = G_seir.copy()
top10_risco = df_top10['Node'].astype(int).tolist()
for node in G_risco.nodes():
    if node in top10_risco:
        G_risco.nodes[node]['color'] = color_risco_map['Em risco']
    else:
        status_label = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
        if len(status_label) > 0:
            G_risco.nodes[node]['color'] = color_risco_map.get(status_label[0], '#999999')
        else:
            G_risco.nodes[node]['color'] = '#999999'
grafo_pyvis(G_risco)

st.markdown("""
---  
**Legenda das cores no grafo:**  
- Vermelho: Infectado  
- Verde escuro: Removido  
- Azul claro: Suscetível  
- Amarelo: Exposto  
- Roxo: Próximos nós com maior risco (Link Prediction)
""")
