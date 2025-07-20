import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tempfile
import os

# Função para exibir grafo Pyvis no Streamlit
def display_pyvis_graph(graph):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", notebook=False)
    for node in graph.nodes(data=True):
        color = node[1].get('color', '#FFFFFF')
        label = node[1].get('label', str(node[0]))
        net.add_node(node[0], label=label, color=color)
    for edge in graph.edges():
        net.add_edge(edge[0], edge[1])
    
    path = tempfile.mktemp(suffix=".html")
    net.show(path)
    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=650, scrolling=True)

# --- Carregamento dos dados ---
G_original = nx.read_graphml('/mnt/data/grafo_original.graphml')
G_seir = nx.read_graphml('/mnt/data/grafo_seir.graphml')
status_df = pd.read_csv('/mnt/data/status.csv')
top10_df = pd.read_csv('/mnt/data/top10.csv')

status_df['Node'] = status_df['Node'].astype(str)
top10_df['Node'] = top10_df['Node'].astype(str)

status_dict = dict(zip(status_df['Node'], status_df['Status']))
status_label_dict = dict(zip(status_df['Node'], status_df['status_label']))
top10_nodes = top10_df['Node'].tolist()

# --- Subgrafo limitado a 500 nós ---
valid_nodes = [node for node in G_seir.nodes() if node in status_dict]
sample_nodes = valid_nodes[:500]
H = G_seir.subgraph(sample_nodes).copy()

# Atribuir status e rótulos
for node in H.nodes():
    H.nodes[node]['status'] = status_dict.get(node, 0)
    H.nodes[node]['status_label'] = status_label_dict.get(node, 'Desconhecido')

# --- Cores por status ---
def cor_status(status):
    cores = {
        0: "#A9A9A9",  # suscetível
        1: "#FFD700",  # exposto
        2: "#FF4500",  # infectado
        3: "#32CD32",  # recuperado
        4: "#4B0082",  # falecido
    }
    return cores.get(status, "#FFFFFF")

# Aplicar cor ao SEIR
for node in H.nodes():
    H.nodes[node]['color'] = cor_status(H.nodes[node]['status'])
    H.nodes[node]['label'] = f"{node} - {H.nodes[node]['status_label']}"

# --- GRAFO COM LINK PREDICTION ---
G_pred = H.copy()
for node in G_pred.nodes():
    status = G_pred.nodes[node].get('status', 0)
    if node in top10_nodes:
        G_pred.nodes[node]['color'] = '#AA00FF'  # roxo - previsão
    else:
        G_pred.nodes[node]['color'] = cor_status(status)
    G_pred.nodes[node]['label'] = f"{node} - {status_label_dict.get(node, 'Desconhecido')}"

# --- Streamlit App ---
st.set_page_config(page_title="Simulação Epidemia em Redes", layout="wide")
st.title("🔬 Simulação de Epidemia em Redes com SEIR e Previsão por Link Prediction")
st.markdown("""
    Este projeto visa simular a propagação de uma doença infecciosa (como a COVID-19) em uma rede social utilizando o modelo epidemiológico SEIR (Suscetível, Exposto, Infectado, Recuperado). O grafo original representa uma rede social extraída de dados do Facebook, onde os nós são indivíduos e as arestas representam conexões entre eles. A análise inclui a visualização do grafo original, a simulação SEIR e a previsão de nós de alto risco usando técnicas de link prediction.
""")

# --- Métricas da rede ---
st.subheader("📊 Métricas da Rede (Subgrafo SEIR com 500 nós)")
st.markdown("As métricas abaixo descrevem as características estruturais do subgrafo utilizado na simulação.")

num_nos = H.number_of_nodes()
num_arestas = H.number_of_edges()
densidade = nx.density(H)
diametro = nx.diameter(H) if nx.is_connected(H) else "Grafo desconexo"
clustering_medio = nx.average_clustering(H)

st.write({
    "Número de Nós": num_nos,
    "Número de Arestas": num_arestas,
    "Densidade": round(densidade, 4),
    "Diâmetro": diametro,
    "Coef. de Clustering Médio": round(clustering_medio, 4)
})

# --- Histograma de graus ---
st.subheader("📈 Histograma de Grau dos Nós")
graus = [grau for no, grau in H.degree()]
fig, ax = plt.subplots()
ax.hist(graus, bins=20, color="#66CCFF", edgecolor="black")
ax.set_title("Distribuição do Grau dos Nós")
ax.set_xlabel("Grau")
ax.set_ylabel("Frequência")
st.pyplot(fig)

# --- Tabela Top 10 ---
st.subheader("🏅 Top 10 Nós Previstos como Potencialmente Infectados")
st.dataframe(top10_df, hide_index=True)

# --- Visualizações ---
st.subheader("🌐 Visualizações Interativas dos Grafos")

tab1, tab2, tab3 = st.tabs(["Grafo Original", "Grafo Pós-Simulação SEIR", "Grafo com Previsão (Adamic-Adar)"])

with tab1:
    st.markdown("**Visualização do Grafo Original (sem estados SEIR)**")
    G_sub_original = G_original.subgraph(list(H.nodes())).copy()
    for node in G_sub_original.nodes():
        G_sub_original.nodes[node]['color'] = "#AAAAAA"
        G_sub_original.nodes[node]['label'] = str(node)
    display_pyvis_graph(G_sub_original)

with tab2:
    st.markdown("**Visualização do Grafo após Simulação SEIR**")
    display_pyvis_graph(H)

with tab3:
    st.markdown("**Visualização com Previsão de Próximos Infectados (Link Prediction - Adamic-Adar)**")
    display_pyvis_graph(G_pred)



