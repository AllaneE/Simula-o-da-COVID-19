import streamlit as st
from pyvis.network import Network
import networkx as nx
import pandas as pd
import os
from streamlit.components.v1 import html

# Configuração da página do Streamlit
st.set_page_config(page_title="Simulação de COVID-19 com Modelo SEID", layout="wide")

# Função para carregar o grafo a partir do arquivo
def load_graph(file_path, file_type='txt'):
    if file_type == 'txt':
        G = nx.read_edgelist(file_path, nodetype=int)
    elif file_type == 'graphml':
        G = nx.read_graphml(file_path)
    return G

# Função para criar grafo interativo com pyvis
def create_pyvis_graph(G, title, state_col=None, highlight_edges=None, height="500px"):
    net = Network(height=height, width="100%", notebook=False, directed=False)
    net.set_options('''
    {
        "nodes": {
            "font": {
                "size": 10
            }
        },
        "edges": {
            "color": {
                "inherit": false
            },
            "smooth": false
        },
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -8000,
                "springLength": 100
            }
        }
    }
    ''')

    state_colors = {'S': 'green', 'E': 'yellow', 'I': 'red', 'D': 'black'}

    # Adicionar nós
    for node in G.nodes():
        color = state_colors[G.nodes[node][state_col]] if state_col and state_col in G.nodes[node] else 'blue'
        net.add_node(node, label=str(node), color=color, size=10)

    # Adicionar arestas
    for u, v in G.edges():
        color = 'purple' if highlight_edges and ((u, v) in highlight_edges or (v, u) in highlight_edges) else 'gray'
        net.add_edge(u, v, color=color)

    # Salvar grafo como HTML
    html_file = f"{title.replace(' ', '_')}.html"
    net.save_graph(html_file)
    return html_file

# Interface do Streamlit
st.title("Simulação de COVID-19 com Modelo SEID")

# Explicação do projeto (baseado no README.md)
st.header("Sobre o Projeto")
st.markdown("""
Este projeto simula a propagação da COVID-19 em uma rede de contatos utilizando o modelo epidemiológico SEID (Suscetível, Exposto, Infectado, Morto). 
O grafo inicial é baseado em uma rede social do Facebook (`facebook_combined.txt`), onde os nós representam indivíduos e as arestas representam interações. 
A simulação modela a evolução dos estados dos nós ao longo do tempo, considerando taxas de infecção, exposição, recuperação e mortalidade. 
Além disso, é realizada uma predição de links para identificar possíveis novos contatos que podem facilitar a propagação da doença, destacados em roxo no grafo final.
""")

# Carregar e exibir grafo original
st.header("Grafo Original")
try:
    G_original = load_graph("facebook_combined.txt", file_type='txt')
    num_nodes = G_original.number_of_nodes()
    num_edges = G_original.number_of_edges()
    st.write(f"Número de nós: {num_nodes}")
    st.write(f"Número de arestas: {num_edges}")
    html_file = create_pyvis_graph(G_original, "Grafo_Original")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html(html_content, height=500)
except FileNotFoundError:
    st.error("Arquivo 'facebook_combined.txt' não encontrado.")

# Carregar e exibir grafo após simulação SEID
st.header("Grafo Após Simulação SEID")
try:
    G_seid = load_graph("grafo_seir.graphml", file_type='graphml')
    # Carregar estados dos nós a partir de status.csv
    status_df = pd.read_csv("status.csv")
    state_counts = status_df['status'].value_counts().to_dict()
    
    # Atribuir estados aos nós
    for _, row in status_df.iterrows():
        G_seid.nodes[row['node']]['status'] = row['status']
    
    st.write(f"Número de nós: {G_seid.number_of_nodes()}")
    st.write(f"Número de arestas: {G_seid.number_of_edges()}")
    st.write("Distribuição dos estados:")
    st.write(f"Suscetíveis: {state_counts.get('S', 0)}")
    st.write(f"Expostos: {state_counts.get('E', 0)}")
    st.write(f"Infectados: {state_counts.get('I', 0)}")
    st.write(f"Mortos: {state_counts.get('D', 0)}")
    html_file = create_pyvis_graph(G_seid, "Grafo_Apos_Simulacao", state_col='status')
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html(html_content, height=500)
except FileNotFoundError:
    st.error("Arquivos 'grafo_seir.graphml' ou 'status.csv' não encontrados.")

# Exibir tabela de predição de links
st.header("Predição de Links")
try:
    top10_df = pd.read_csv("top10.csv")
    st.write("Tabela com os Top 10 Links Previstos:")
    st.table(top10_df)
    
    # Grafo com predição de links
    st.header("Grafo com Predição de Links")
    highlight_edges = [(row['node1'], row['node2']) for _, row in top10_df.iterrows()]
    html_file = create_pyvis_graph(G_seid, "Grafo_com_Links_Previstos", state_col='status', highlight_edges=highlight_edges)
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html(html_content, height=500)
except FileNotFoundError:
    st.error("Arquivo 'top10.csv' não encontrado.")

# Legenda
st.markdown("""
**Legenda das Cores:**  
- Vermelho: Infectado  
- Verde Escuro: Removido  
- Azul Claro: Suscetível  
- Amarelo: Exposto  
- Roxo: Nós em risco (Link Prediction)
""")
