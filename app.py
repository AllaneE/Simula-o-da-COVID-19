import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tempfile
import streamlit.components.v1 as components

# Mapa de cores para os estados
color_map = {0: '#669BBC', 1: '#F4A261', 2: '#C1121F', 3: '#4A5759'}

# Função para calcular métricas do grafo
def calculate_graph_metrics(G, graph_name):
    try:
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        avg_degree = sum(dict(G.degree()).values()) / num_nodes if num_nodes > 0 else 0.0
        density = nx.density(G)
        try:
            avg_clustering = nx.average_clustering(G)
        except ZeroDivisionError:
            avg_clustering = 0.0
        try:
            assortativity = nx.degree_assortativity_coefficient(G)
        except ZeroDivisionError:
            assortativity = 0.0
        connected_components = len(list(nx.connected_components(G)))
        
        metrics = f"""# Métricas do {graph_name}
- Número de nós: {num_nodes}
- Número de arestas: {num_edges}
- Grau médio: {avg_degree:.2f}
- Densidade: {density:.4f}
- Coeficiente de aglomeração médio: {avg_clustering:.4f}
- Assortatividade: {assortativity:.2f}
- Número de componentes conectados: {connected_components}
"""
        return metrics, num_nodes, num_edges, avg_degree, density, avg_clustering, assortativity, connected_components
    except Exception as e:
        st.error(f"Erro ao calcular métricas para {graph_name}: {str(e)}")
        return None, 0, 0, 0.0, 0.0, 0.0, 0.0, 0

# Função para carregar o grafo original
def load_original_graph():
    try:
        G = nx.read_graphml('grafo_original.graphml')
        st.write("Grafo original carregado de grafo_original.graphml")
    except FileNotFoundError:
        G = nx.read_edgelist('facebook_combined.txt', nodetype=int, create_using=nx.Graph())
        st.write("Grafo original carregado de facebook_combined.txt")
    return G

# Função para carregar o grafo SEIR e os estados
def load_seir_graph():
    try:
        G_seir = nx.read_graphml('grafo_seir.graphml')
        status_df = pd.read_csv('status.csv')
        
        # Verificar nomes das colunas
        if 'Node' in status_df.columns and 'Status' in status_df.columns:
            node_col, status_col = 'Node', 'Status'
        elif 'node' in status_df.columns and 'status' in status_df.columns:
            node_col, status_col = 'node', 'status'
        else:
            st.error("As colunas esperadas ('Node'/'node' e 'Status'/'status') não foram encontradas em status.csv")
            return G_seir, {}
        
        # Converter IDs para inteiros
        status_df[node_col] = pd.to_numeric(status_df[node_col], errors='coerce')
        status_df = status_df.dropna(subset=[node_col])
        status_df[node_col] = status_df[node_col].astype(int)
        
        # Validar valores de status
        valid_statuses = {0, 1, 2, 3}
        invalid_statuses = set(status_df[status_col]) - valid_statuses
        if invalid_statuses:
            st.warning(f"Valores inválidos encontrados em {status_col}: {invalid_statuses}. Usando estado padrão (0) para esses nós.")
        
        status_dict = dict(zip(status_df[node_col], status_df[status_col]))
        st.write(f"Nós em status.csv ({node_col}): {status_df[node_col].tolist()[:5]}")
        st.write(f"Estados em status.csv ({status_col}): {status_df[status_col].tolist()[:5]}")
        st.write(f"Nós no grafo SEIR: {list(G_seir.nodes())[:5]}")
        return G_seir, status_dict
    except Exception as e:
        st.error(f"Erro ao carregar grafo SEIR ou status.csv: {str(e)}")
        return None, {}

# Função para carregar dados de link prediction
def load_link_prediction_data():
    try:
        top10_df = pd.read_csv('top10.csv')
        if 'Node' in top10_df.columns:
            node_col = 'Node'
        elif 'node' in top10_df.columns:
            node_col = 'node'
        else:
            st.error("Coluna 'Node' ou 'node' não encontrada em top10.csv")
            return set(), pd.DataFrame()
        
        top10_df[node_col] = pd.to_numeric(top10_df[node_col], errors='coerce')
        top10_df = top10_df.dropna(subset=[node_col])
        top10_df[node_col] = top10_df[node_col].astype(int)
        
        top_risk_nodes = set(top10_df[node_col][:5])
        st.write(f"Top 5 nós de risco: {top_risk_nodes}")
        return top_risk_nodes, top10_df
    except Exception as e:
        st.error(f"Erro ao carregar top10.csv: {str(e)}")
        return set(), pd.DataFrame()

# Função para criar visualização com PyVis
def create_pyvis_graph(G, node_colors, title, output_file, top10_df=None):
    if G is None:
        st.error("Erro: Grafo não foi carregado corretamente.")
        return
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=False)
    net.from_nx(G)
    
    for node in net.nodes:
        node_id = int(node['id'])
        node['color'] = node_colors.get(node_id, '#669BBC')
        node['title'] = f"Nó {node_id}"
    
    net.set_options("""
    var options = {
      "nodes": {
        "shape": "dot",
        "size": 20
      },
      "edges": {
        "color": {
          "color": "#808080",
          "highlight": "#808080",
          "hover": "#808080"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.3,
          "springLength": 95
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    if top10_df is not None and not top10_df.empty:
        html_table = top10_df.head(10).to_html(index=False, classes="table table-bordered table-dark")
        net.html = f"""
        <html>
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <style>
                body {{ background-color: #222222; color: white; }}
                .table {{ margin: 20px auto; width: 80%; }}
            </style>
        </head>
        <body>
            <h1 style="text-align: center;">{title}</h1>
            {html_table}
            {net.html}
        </body>
        </html>
        """
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        path = tmp_file.name
        net.save_graph(path)
    
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        st.components.v1.html(html, height=750)
    st.write(f"Visualização salva em: {path}")

# Visualização do grafo original
def visualize_original_graph():
    st.title("Simulação da COVID-19 com SEIR")
    st.markdown("""
    Este projeto visa simular a propagação de uma doença infecciosa (como a COVID-19) em uma rede social utilizando o modelo epidemiológico SEIR (Suscetível, Exposto, Infectado, Recuperado). O grafo original representa uma rede social extraída de dados do Facebook, onde os nós são indivíduos e as arestas representam conexões entre eles. A análise inclui a visualização do grafo original, a simulação SEIR e a previsão de nós de alto risco usando técnicas de link prediction.
    """)
    
    G = load_original_graph()
    if G is None:
        st.error("Não foi possível carregar o grafo original. Verifique os arquivos de entrada.")
        return
    
    sample_nodes = list(G.nodes())[:500]
    sample_nodes = [node for node in sample_nodes if node in G.nodes()]
    H = G.subgraph(sample_nodes)
    
    metrics_data = calculate_graph_metrics(G, "Grafo Original")
    if metrics_data[0] is None:
        st.error("Não foi possível calcular as métricas do grafo original.")
        return
    metrics, num_nodes, num_edges, avg_degree, density, avg_clustering, assortativity, connected_components = metrics_data
    
    with open("grafo_original_metrics.md", "w") as f:
        f.write(metrics)
    st.subheader("Métricas do Grafo Original")
    st.markdown(f"- Número de nós: {num_nodes}")
    st.markdown(f"- Número de arestas: {num_edges}")
    st.markdown(f"- Grau médio: {avg_degree:.2f}")
    st.markdown(f"- Densidade: {density:.4f}")
    st.markdown(f"- Coeficiente de aglomeração médio: {avg_clustering:.4f}")
    st.markdown(f"- Assortatividade: {assortativity:.2f}")
    
    st.subheader("Distribuição do Grau dos Nós")
    degree_sequence = [d for n, d in H.degree()]
    fig, ax = plt.subplots()
    ax.hist(degree_sequence, bins=range(1, max(degree_sequence)+2), color='skyblue', edgecolor='black')
    ax.set_title("Distribuição de Grau dos Nós")
    ax.set_xlabel("Grau")
    ax.set_ylabel("Quantidade de Nós")
    st.pyplot(fig)
    
    node_colors = {node: color_map[0] for node in H.nodes()}
    st.subheader("Visualização Interativa do Grafo Original")
    create_pyvis_graph(H, node_colors, "Grafo Original", "grafo_original.html")

# Visualização do grafo SEIR
def visualize_seir_graph():
    st.title("Visualização do Grafo SEIR")
    G_seir, status_dict = load_seir_graph()
    if G_seir is None or not status_dict
