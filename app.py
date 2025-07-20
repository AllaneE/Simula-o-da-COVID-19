
import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# Configuração do Streamlit
st.set_page_config(page_title="Simulação SEID - COVID-19", layout="wide")

st.title("Simulação Epidemia SEID - COVID-19")
st.markdown("""
Simulação da propagação do COVID-19 com modelo SEID em uma rede social (dataset Facebook).  
Exibe métricas de rede e previsão de novos contatos em risco via link prediction.
""")

# Carregar dados
try:
    G_original = nx.read_graphml("grafo_original.graphml", node_type=int)
    G_seid = nx.read_graphml("grafo_seir.graphml", node_type=int)
    df_status = pd.read_csv("status.csv")
    df_top10 = pd.read_csv("top10.csv")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Grafo original
st.header("Grafo Original")
st.write(f"Nós: {G_original.number_of_nodes()}")
st.write(f"Arestas: {G_original.number_of_edges()}")
st.write(f"Densidade: {nx.density(G_original):.6f}")

net = Network(height="600px", width="100%", bgcolor="#FFFFFF", font_color="black", cdn_resources='remote')
for node in G_original.nodes():
    net.add_node(int(node), label=f"Nó {node}", color="#1E90FF", title="Status: Desconhecido", size=10)
for source, target in G_original.edges():
    net.add_edge(int(source), int(target), color="#808080")
net.set_options('''
{
    "physics": {"enabled": false},
    "layout": {"randomSeed": 42},
    "edges": {"color": {"inherit": false}, "smooth": false}
}
''')
components.html(net.generate_html(), height=650)

# Grafo após simulação SEID
st.header("Grafo Após Simulação SEID")
for node in G_seid.nodes():
    status = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
    G_seid.nodes[node]['status'] = status[0] if len(status) > 0 else 'Desconhecido'

st.write(f"Nós: {G_seid.number_of_nodes()}")
st.write(f"Arestas: {G_seid.number_of_edges()}")
st.write(f"Densidade: {nx.density(G_seid):.6f}")

st.subheader("Quantidade por Estado")
st.table(df_status['status_label'].value_counts())

net = Network(height="600px", width="100%", bgcolor="#FFFFFF", font_color="black", cdn_resources='remote')
color_map = {'Suscetível': '#669BBC', 'Exposto': '#F4A261', 'Infectado': '#C1121F', 'Removido': '#4A5759'}
for node in G_seid.nodes():
    status = G_seid.nodes[node].get('status', 'Desconhecido')
    color = color_map.get(status, '#999999')
    net.add_node(int(node), label=f"Nó {node}", color=color, title=f"Status: {status}", size=10)
for source, target in G_seid.edges():
    net.add_edge(int(source), int(target), color="#808080")
net.set_options('''
{
    "physics": {"enabled": false},
    "layout": {"randomSeed": 42},
    "edges": {"color": {"inherit": false}, "smooth": false}
}
''')
components.html(net.generate_html(), height=650)

# Top 10 links previstos
st.header("Predição de Links")
st.subheader("Top 10 Links Previstos")
st.table(df_top10)

# Grafo com links previstos e nós de risco
st.header("Grafo com Links Previstos")
net = Network(height="600px", width="100%", bgcolor="#FFFFFF", font_color="black", cdn_resources='remote')
top_5_nodes = df_top10['Node'].astype(int).tolist()[:5]  # Top 5 nós para destaque
highlight_edges = [(int(row['node1']), int(row['node2'])) for _, row in df_top10.iterrows()]

for node in G_seid.nodes():
    status = G_seid.nodes[node].get('status', 'Desconhecido')
    if node in top_5_nodes:
        color = '#800080'  # Roxo para nós em risco (top 5)
        title = "Status: Em risco (Link Prediction)"
    else:
        color = color_map.get(status, '#999999')
        title = f"Status: {status}"
    net.add_node(int(node), label=f"Nó {node}", color=color, title=title, size=10)

for source, target in G_seid.edges():
    net.add_edge(int(source), int(target), color="#808080")
for node1, node2 in highlight_edges:
    if not G_seid.has_edge(node1, node2):
        net.add_edge(int(node1), int(node2), color="#800080")  # Arestas roxas para links previstos

net.set_options('''
{
    "physics": {"enabled": false},
    "layout": {"randomSeed": 42},
    "edges": {"color": {"inherit": false}, "smooth": false}
}
''')
components.html(net.generate_html(), height=650)

# Legenda
st.markdown("""
**Legenda das Cores:**  
- Azul Claro (#669BBC): Suscetível  
- Amarelo (#F4A261): Exposto  
- Vermelho (#C1121F): Infectado  
- Verde Escuro (#4A5759): Removido  
- Azul (#1E90FF): Desconhecido (grafo original)  
- Roxo (#800080): Nós em risco (top 5) e Links Previstos
""")
