import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os

# Configuração da página do Streamlit
st.set_page_config(page_title="Simulação de COVID-19 com Modelo SEID", layout="wide")

# Função para carregar o grafo a partir do arquivo
def load_graph(file_path, file_type='txt'):
    if file_type == 'txt':
        G = nx.read_edgelist(file_path, nodetype=int)
    elif file_type == 'graphml':
        G = nx.read_graphml(file_path)
    return G

# Função para plotar o grafo com cores baseadas no estado
def plot_graph(G, title, state_col=None, highlight_edges=None):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    
    if state_col:
        state_colors = {'S': 'green', 'E': 'yellow', 'I': 'red', 'D': 'black'}
        colors = [state_colors[G.nodes[node][state_col]] for node in G.nodes()]
    else:
        colors = 'blue'  # Cor padrão para grafo original
    
    edge_colors = ['purple' if highlight_edges and ((u, v) in highlight_edges or (v, u) in highlight_edges) else 'gray' for u, v in G.edges()]
    
    nx.draw(G, pos, node_color=colors, edge_color=edge_colors, with_labels=False, node_size=100)
    plt.title(title)
    return plt

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
    fig = plot_graph(G_original, "Grafo Original (Rede Social do Facebook)")
    st.pyplot(fig)
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
    fig = plot_graph(G_seid, "Grafo Após Simulação (Verde: Suscetível, Amarelo: Exposto, Vermelho: Infectado, Preto: Morto)", state_col='status')
    st.pyplot(fig)
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
    fig = plot_graph(G_seid, "Grafo com Links Previstos (Arestas Roxas: Links Previstos)", state_col='status', highlight_edges=highlight_edges)
    st.pyplot(fig)
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
