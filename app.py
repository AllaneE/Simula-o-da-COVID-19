import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# Configuração inicial do Streamlit
st.set_page_config(page_title="Simulação SEIR - COVID-19", layout="wide")

st.title("Simulação Epidemia SEIR em Rede - COVID-19")
st.markdown("""
Simulação da propagação do COVID-19 usando o modelo SEIR em uma rede social (dataset Facebook).
Análise de métricas de rede e previsão de nós em risco via link prediction.
""")

# Carregar os dados
try:
    G_original = nx.read_graphml("grafo_original.graphml")
    G_seir = nx.read_graphml("grafo_seir.graphml")
    df_status = pd.read_csv("status.csv")
    df_top10 = pd.read_csv("top10.csv")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Exibir métricas do grafo original
st.header("Grafo Original")
st.markdown(f"**Nós**: {G_original.number_of_nodes()}")
st.markdown(f"**Arestas**: {G_original.number_of_edges()}")
st.markdown(f"**Densidade**: {nx.density(G_original):.2f}")

# Visualizar grafo original
net = Network(height="750px", width="100%", bgcolor="#FFFFFF", font_color="black")
for node, data in G_original.nodes(data=True):
    label = f"Nó {node}"
    net.add_node(node, label=label, color="#C6E5B1", title=f"<b>{label}</b><br>Status: Desconhecido", size=10)
for source, target in G_original.edges():
    net.add_edge(source, target)
net.set_options('{"physics": {"enabled": false}}')
components.html(net.generate_html(), height=800)

# Exibir métricas do grafo SEIR
st.header("Grafo após Simulação SEIR")
st.markdown(f"**Nós**: {G_seir.number_of_nodes()}")
st.markdown(f"**Arestas**: {G_seir.number_of_edges()}")
st.markdown(f"**Densidade**: {nx.density(G_seir):.2f}")

# Contagem de estados
st.subheader("Quantidade por Estado")
st.table(df_status['status_label'].value_counts())

# Configurar status e cores para o grafo SEIR
color_map = {'Suscetível': '#669BBC', 'Exposto': '#F4A261', 'Infectado': '#C1121F', 'Removido': '#4A5759'}
for node in G_seir.nodes():
    status = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
    G_seir.nodes[node]['status_label'] = status[0] if len(status) > 0 else 'Desconhecido'

# Visualizar grafo SEIR
net = Network(height="750px", width="100%", bgcolor="#FFFFFF", font_color="black")
for node, data in G_seir.nodes(data=True):
    status = data.get('status_label', 'Desconhecido')
    color = color_map.get(status, '#999999')
    label = f"Nó {node}"
    net.add_node(node, label=label, color=color, title=f"<b>{label}</b><br>Status: {status}", size=10)
for source, target in G_seir.edges():
net.set_options('{"physics": {"enabled": false}}')
components.html(net.generate_html(), height=800)

# Top 10 nós mais infectados
st.header("Top 10 Nós Mais Infectados")
st.table(df_top10)

# Grafo com nós em risco
st.subheader("Grafo com Nós em Risco")
color_risco_map = {'Infectado': '#C1121F', 'Removido': '#4A5759', 'Suscetível': '#669BBC', 'Exposto': '#F4A261', 'Em risco': 'purple'}
G_risco = G_seir.copy()
top10_risco = df_top10['Node'].astype(int).tolist()
for node in G_risco.nodes():
    G_risco.nodes[node]['status_label'] = 'Em risco' if node in top10_risco else G_seir.nodes[node]['status_label']

# Visualizar grafo com nós em risco
net = Network(height="750px", width="100%", bgcolor="#FFFFFF", font_color="black")
for node, data in G_risco.nodes(data=True):
    status = data.get('status_label', 'Desconhecido')
    color = color_risco_map.get(status, '#999999')
    label = f"Nó {node}"
    net.add_node(node, label=label, color=color, title=f"<b>{label}</b><br>Status: {status}", size=10)
for source, target in G_risco.edges():
    net.add_edge(source, target)
net.set_options('{"physics": {"enabled": false}}')
components.html(net.generate_html(), height=800)

# Legenda
st.markdown("""
**Legenda das Cores:**  
- Vermelho: Infectado  
- Verde Escuro: Removido  
- Azul Claro: Suscetível  
- Amarelo: Exposto  
- Roxo: Nós em risco (Link Prediction)
""")
