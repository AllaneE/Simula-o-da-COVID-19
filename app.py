import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import requests
from io import StringIO
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# Configuração inicial
st.set_page_config(page_title="Projeto Simulação SEIR - COVID-19", layout="wide")

st.title("Simulação Epidemia SEIR em Rede - COVID-19")
st.markdown("""
Este projeto simula a propagação de uma epidemia usando o modelo SEIR em uma rede social real (dataset Facebook).
Utilizamos métricas de teoria de redes para analisar o grafo antes e depois da simulação, além de aplicar link prediction para prever quais nós estão em maior risco de infecção.
""")

@st.cache_data
def grafos_e_dados():
    try:
        # Carregar arquivos localmente
        G_original = nx.read_graphml("grafo_original.graphml")
        G_seir = nx.read_graphml("grafo_seir.graphml")
        df_status = pd.read_csv("status.csv")
        df_top10 = pd.read_csv("top10.csv")
        return G_original, G_seir, df_status, df_top10
    except FileNotFoundError as e:
        raise Exception(f"Erro ao carregar os arquivos: Arquivo não encontrado - {e}")
    except nx.NetworkXError as e:
        raise Exception(f"Erro ao processar os arquivos GraphML: {e}")
    except pd.errors.ParserError as e:
        raise Exception(f"Erro ao processar os arquivos CSV: {e}")

try:
    G_original, G_seir, df_status, df_top10 = grafos_e_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

def grafo_pyvis(G, height=750, width="100%", color_map=None, node_sizes=None, node_labels=None):
    net = Network(height=f"{height}px", width=width, bgcolor="#FFFFFF", font_color="black")
    
    # Adicionar nós com atributos personalizados
    for node, data in G.nodes(data=True):
        color = color_map.get(data.get('status_label', ''), '#999999') if color_map else '#C6E5B1'
        size = node_sizes.get(node, 10) if node_sizes else 10
        label = node_labels.get(node, str(node)) if node_labels else str(node)
        title = f"<b>{label}</b><br>Status: {data.get('status_label', 'Desconhecido')}"
        net.add_node(node, label=label, color=color, title=title, size=size)

    # Adicionar arestas
    for source, target in G.edges():
        net.add_edge(source, target)

    # Configurações de física
    net.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 250,
          "springConstant": 0.001
        },
        "minVelocity": 0.75
      },
      "nodes": {
        "font": {
          "size": 14
        }
      }
    }
    """)

    # Gerar HTML em memória
    html_str = net.generate_html()
    components.html(html_str, height=height+50)

# Exibir métricas do grafo original
st.header("Grafo Original")
st.markdown(f"**Nós**: {G_original.number_of_nodes()}")
st.markdown(f"**Arestas**: {G_original.number_of_edges()}")
st.markdown(f"**Densidade**: {nx.density(G_original):.2f}")
st.markdown(f"**Assortatividade**: {nx.degree_assortativity_coefficient(G_original):.2f}")
st.markdown(f"**Coeficiente de Clustering**: {nx.average_clustering(G_original):.2f}")

# Visualizar grafo original
node_sizes = {n: 10 for n in G_original.nodes()}  # Tamanho fixo, como no primeiro código
node_labels = {n: f"Nó {n}" for n in G_original.nodes()}
grafo_pyvis(G_original, color_map=None, node_sizes=node_sizes, node_labels=node_labels)

# Exibir métricas do grafo SEIR
st.header("Grafo após Simulação SEIR")
st.markdown(f"**Nós**: {G_seir.number_of_nodes()}")
st.markdown(f"**Arestas**: {G_seir.number_of_edges()}")
st.markdown(f"**Densidade**: {nx.density(G_seir):.2f}")
st.markdown(f"**Assortatividade**: {nx.degree_assortativity_coefficient(G_seir):.2f}")
st.markdown(f"**Coeficiente de Clustering**: {nx.average_clustering(G_seir):.2f}")
st.markdown(f"**Número de Componentes Conectados**: {len(list(nx.connected_components(G_seir)))}")

# Contagem de estados
status_cont = df_status['status_label'].value_counts()
st.subheader("Quantidade por Estado:")
st.table(status_cont)

# Configurar cores para o grafo SEIR
color_map = {'Suscetível': '#669BBC', 'Exposto': '#F4A261', 'Infectado': '#C1121F', 'Removido': '#4A5759'}
for node in G_seir.nodes():
    status_label = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
    if len(status_label) > 0:
        G_seir.nodes[node]['status_label'] = status_label[0]
    else:
        G_seir.nodes[node]['status_label'] = 'Desconhecido'

node_sizes_seir = {n: 10 for n in G_seir.nodes()}  # Tamanho fixo, como no primeiro código
node_labels_seir = {n: f"Nó {n}" for n in G_seir.nodes()}
grafo_pyvis(G_seir, color_map=None, node_sizes=node_sizes_seir, node_labels=node_labels_seir)

# Top 10 nós mais infectados
st.header("Top 10 Nós Mais Infectados")
st.table(df_top10)

# Grafo com nós em risco
st.subheader("Grafo com Possíveis Nós em Risco")
color_risco_map = {'Infectado': '#C1121F', 'Removido': '#4A5759', 'Suscetível': '#669BBC', 'Em risco': 'purple', 'Exposto': '#F4A261'}
G_risco = G_seir.copy()
top10_risco = df_top10['Node'].astype(int).tolist()
for node in G_risco.nodes():
    if node in top10_risco:
        G_risco.nodes[node]['status_label'] = 'Em risco'
    else:
        status_label = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
        if len(status_label) > 0:
            G_risco.nodes[node]['status_label'] = status_label[0]
        else:
            G_risco.nodes[node]['status_label'] = 'Desconhecido'

grafo_pyvis(G_risco, color_map=color_risco_map, node_sizes=node_sizes_seir, node_labels=node_labels_seir)

# Legenda
st.markdown("""
---
**Legenda das cores no grafo:**  
- Vermelho: Infectado  
- Verde escuro: Removido  
- Azul claro: Suscetível  
- Amarelo: Exposto  
- Roxo: Próximos nós com maior risco (Link Prediction)
""")

