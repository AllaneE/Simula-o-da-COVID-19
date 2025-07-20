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

def carregar_dados():
    try:
        G_original = nx.read_graphml("grafo_original.graphml")
        G_seir = nx.read_graphml("grafo_seir.graphml")
        df_status = pd.read_csv("status.csv")
        df_top10 = pd.read_csv("top10.csv")
        return G_original, G_seir, df_status, df_top10
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.stop()

# Carregar os dados
G_original, G_seir, df_status, df_top10 = carregar_dados()

# Função simplificada para gerar grafo com PyVis
def exibir_grafo(G, color_map=None, height=750, width="100%"):
    net = Network(height=f"{height}px", width=width, bgcolor="#FFFFFF", font_color="black")

    # Adicionar nós
    for node, data in G.nodes(data=True):
        status = data.get('status_label', 'Desconhecido')
        color = color_map.get(status, '#999999') if color_map else '#C6E5B1'
        label = f"Nó {node}"
        net.add_node(node, label=label, color=color, title=f"<b>{label}</b><br>Status: {status}", size=10)

    # Adicionar arestas
    for source, target in G.edges():
        net.add_edge(source, target)

    # Configurações mínimas de física
    net.set_options('''
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 250
        }
      }
    }
    ''')

    # Renderizar HTML no Streamlit
    components.html(net.generate_html(), height=height + 50)

# Exibir métricas do grafo original
st.header("Grafo Original")
st.markdown(f"**Nós**: {G_original.number_of_nodes()}")
st.markdown(f"**Arestas**: {G_original.number_of_edges()}")
st.markdown(f"**Densidade**: {nx.density(G_original):.2f}")
st.markdown(f"**Assortatividade**: {nx.degree_assortativity_coefficient(G_original):.2f}")
st.markdown(f"**Clustering Médio**: {nx.average_clustering(G_original):.2f}")

# Visualizar grafo original
exibir_grafo(G_original)

# Exibir métricas do grafo SEIR
st.header("Grafo após Simulação SEIR")
st.markdown(f"**Nós**: {G_seir.number_of_nodes()}")
st.markdown(f"**Arestas**: {G_seir.number_of_edges()}")
st.markdown(f"**Densidade**: {nx.density(G_seir):.2f}")
st.markdown(f"**Assortatividade**: {nx.degree_assortativity_coefficient(G_seir):.2f}")
st.markdown(f"**Clustering Médio**: {nx.average_clustering(G_seir):.2f}")
st.markdown(f"**Componentes Conectados**: {len(list(nx.connected_components(G_seir)))}")

# Contagem de estados
st.subheader("Quantidade por Estado")
st.table(df_status['status_label'].value_counts())

# Configurar status e cores para o grafo SEIR
color_map = {'Suscetível': '#669BBC', 'Exposto': '#F4A261', 'Infectado': '#C1121F', 'Removido': '#4A5759'}
for node in G_seir.nodes():
    status = df_status.loc[df_status['Node'] == int(node), 'status_label'].values
    G_seir.nodes[node]['status_label'] = status[0] if len(status) > 0 else 'Desconhecido'

# Visualizar grafo SEIR
exibir_grafo(G_seir, color_map=color_map)

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
exibir_grafo(G_risco, color_map=color_risco_map)

# Legenda
st.markdown("""
**Legenda das Cores:**  
- Vermelho: Infectado  
- Verde Escuro: Removido  
- Azul Claro: Suscetível  
- Amarelo: Exposto  
- Roxo: Nós em risco (Link Prediction)
""")
