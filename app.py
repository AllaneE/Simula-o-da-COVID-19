import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

# Fundo escuro para matplotlib
plt.style.use('dark_background')

st.set_page_config(page_title="Simulação COVID-19 com Modelo SEIR", layout="wide")

# Carregar grafo
def load_graph(file_path, file_type='txt'):
    if file_type == 'txt':
        return nx.read_edgelist(file_path, nodetype=int)
    elif file_type == 'graphml':
        return nx.read_graphml(file_path)

# Plotar com matplotlib
def plot_graph(G, title, state_col=None, highlight_edges=None):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    
    if state_col:
        state_colors = {'S': 'green', 'E': 'yellow', 'I': 'red', 'D': 'black'}
        colors = [state_colors.get(G.nodes[node].get(state_col, 'S'), 'gray') for node in G.nodes()]
    else:
        colors = 'cyan'

    edge_colors = ['purple' if highlight_edges and ((u, v) in highlight_edges or (v, u) in highlight_edges) else 'gray' for u, v in G.edges()]
    
    nx.draw(G, pos, node_color=colors, edge_color=edge_colors, with_labels=False, node_size=80)
    plt.title(title)
    return plt

# Plotar grafo com Pyvis
def plot_graph_pyvis(G, state_col=None, highlight_edges=None):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    net.barnes_hut()

    color_map = {'S': 'green', 'E': 'yellow', 'I': 'red', 'D': 'black'}
    for node in G.nodes():
        state = G.nodes[node].get(state_col, 'S')
        color = color_map.get(state, 'gray')
        net.add_node(node, label=str(node), color=color)

    for u, v in G.edges():
        color = 'purple' if highlight_edges and ((u, v) in highlight_edges or (v, u) in highlight_edges) else 'gray'
        net.add_edge(u, v, color=color)

    net.save_graph("graph.html")
    return "graph.html"

# Interface
st.title("Simulação COVID-19 com Modelo SEIR")

st.header("Sobre o Projeto")
st.markdown("""
Este projeto simula a propagação da COVID-19 usando o modelo SEIR (Suscetível, Exposto, Infectado, Removido) em uma rede social baseada em dados do Facebook.
""")

# --- Grafo Original
st.subheader("Grafo Original")
try:
    G_original = load_graph("facebook_combined.txt", file_type='txt')
    st.write(f"Nós: {G_original.number_of_nodes()}, Arestas: {G_original.number_of_edges()}")
    fig = plot_graph(G_original, "Grafo Original")
    st.pyplot(fig)
except FileNotFoundError:
    st.error("Arquivo 'facebook_combined.txt' não encontrado.")

# --- Grafo SEID
st.subheader("Grafo Após Simulação SEIDR")
try:
    G_seid = load_graph("grafo_seir.graphml", file_type='graphml')
    status_df = pd.read_csv("status.csv")

    for _, row in status_df.iterrows():
        G_seid.nodes[str(row['node'])]['status_label'] = row['status_label']

    counts = status_df['status_label'].value_counts().to_dict()
    st.write("Distribuição dos estados:")
    st.write(counts)

    fig = plot_graph(G_seid, "Grafo SEIR com Matplotlib", state_col='status')
    st.pyplot(fig)

    st.markdown("### Visualização Interativa (Pyvis)")
    html_file = plot_graph_pyvis(G_seid, state_col='status')
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    components.html(html_content, height=600, scrolling=True)

except FileNotFoundError:
    st.error("Arquivos 'grafo_seir.graphml' ou 'status.csv' não encontrados.")

# --- Predição de Links
st.subheader("Predição de Novos Links")
try:
    top10_df = pd.read_csv("top10.csv")
    st.dataframe(top10_df)

    edges_pred = [(str(row['node1']), str(row['node2'])) for _, row in top10_df.iterrows()]
    fig = plot_graph(G_seid, "Grafo com Links Previstos (Roxo)", state_col='status', highlight_edges=edges_pred)
    st.pyplot(fig)

    st.markdown("### Visualização Interativa com Links Previstos (Pyvis)")
    html_file = plot_graph_pyvis(G_seid, state_col='status', highlight_edges=edges_pred)
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    components.html(html_content, height=600, scrolling=True)

except FileNotFoundError:
    st.error("Arquivo 'top10.csv' não encontrado.")
