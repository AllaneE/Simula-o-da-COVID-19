import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit as st

# Configuração do Streamlit
st.set_page_config(page_title="Simulação da Propagação da COVID-19", layout="wide")

# Mapa de cores para os estados
color_map = {0: '#669BBC', 1: '#F4A261', 2: '#C1121F', 3: '#4A5759'}

# Função para carregar o grafo original
def load_original_graph():
    try:
        G = nx.read_graphml('grafo_original.graphml')
    except FileNotFoundError:
        G = nx.read_edgelist('facebook_combined.txt', nodetype=int, create_using=nx.Graph())
    return G

# Função para carregar o grafo SEIR e os estados
def load_seir_graph():
    try:
        G_seir = nx.read_graphml('grafo_seir.graphml')
        status_df = pd.read_csv('status.csv')
        status_df['node'] = status_df['Node'].astype(str)
        status_dict = dict(zip(status_df['node'], status_df['Status']))
        return G_seir, status_dict
    except FileNotFoundError:
        raise FileNotFoundError("Arquivos 'grafo_seir.graphml' ou 'status.csv' não encontrados.")

# Função para carregar dados de link prediction
def load_link_prediction_data():
    try:
        top10_df = pd.read_csv('top10.csv')
        top_risk_nodes = set(top10_df['node'])
        return top_risk_nodes, top10_df
    except FileNotFoundError:
        raise FileNotFoundError("Arquivo 'top10.csv' não encontrado.")

# Função para criar visualização com PyVis
def create_pyvis_graph(G, node_colors, title, output_file, top10_df=None):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=False)
    net.from_nx(G)
    for node in net.nodes:
        node_id = str(node['id'])
        node['color'] = node_colors.get(node_id, '#AAAAAA')
        node['title'] = f"Nó {node_id}"
    net.set_options("""
    var options = {
      "nodes": {"shape": "dot", "size": 10},
      "physics": {"barnesHut": {"gravitationalConstant": -2000, "centralGravity": 0.3, "springLength": 95}, "minVelocity": 0.75}
    }
    """)
    if top10_df is not None:
        table_html = "<h3>Top 10 Links de Maior Risco:</h3><table border='1'><tr><th>Nó 1</th><th>Nó 2</th><th>Score</th></tr>"
        for _, row in top10_df.iterrows():
            table_html += f"<tr><td>{row['node1']}</td><td>{row['node2']}</td><td>{row.get('score', 'N/A'):.6f}</td></tr>"
        table_html += "</table>"
        net.add_node(-1, label=" ", title=table_html, shape="text", x=-1000, y=-1000, fixed=True, physics=False)
    net.save_graph(output_file)

# Interface Streamlit
st.title("Simulação da Propagação da COVID-19 em Redes Sociais")

# Grafo Original
st.subheader("🔗 Grafo Original")
try:
    G_original = load_original_graph()
    node_colors = {str(node): color_map[0] for node in G_original.nodes()}
    num_nodes = G_original.number_of_nodes()
    num_edges = G_original.number_of_edges()
    st.write(f"Nós: {num_nodes}")
    st.whitee(f"Arestas: {num_edges}")
    create_pyvis_graph(G_original, node_colors, "Grafo Original", "grafo_original.html")
    with open("grafo_original.html", "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=800)
except FileNotFoundError:
    st.error("Arquivo 'grafo_original.graphml' ou 'facebook_combined.txt' não encontrado.")

# Grafo SEIR
st.subheader("🔗 Rede após Simulação SEIR")
try:
    G_seir, status_dict = load_seir_graph()
    node_colors = {str(node): color_map[status_dict.get(str(node), 0)] for node in G_seir.nodes()}
    num_nodes = G_seir.number_of_nodes()
    num_edges = G_seir.number_of_edges()
    st.write(f"Nós: {num_nodes}")
    st.whitee(f"Arestas: {num_edges}")
    create_pyvis_graph(G_seir, node_colors, "Rede SEIR", "grafo_seir.html")
    with open("grafo_seir.html", "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=800)
except FileNotFoundError:
    st.error("Arquivos 'grafo_seir.graphml' ou 'status.csv' não encontrados.")

# Link Prediction
st.subheader("🔗 Previsão Simples com Link Prediction")
try:
    top_risk_nodes, top10_df = load_link_prediction_data()
    node_colors = {str(node): "purple" if str(node) in top_risk_nodes else color_map[status_dict.get(str(node), 0)] for node in G_seir.nodes()}
    st.write("Visualizando os 10 pares de nós mais prováveis de conexão futura (maior risco de contágio).")
    create_pyvis_graph(G_seir, node_colors, "Link Prediction", "grafo_link_prediction.html", top10_df)
    with open("grafo_link_prediction.html", "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=800)
except FileNotFoundError:
    st.error("Arquivo 'top10.csv' não encontrado.")
