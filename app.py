import networkx as nx
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Mapa de cores para os estados
color_map = {0: '#669BBC', 1: '#F4A261', 2: '#C1121F', 3: '#4A5759'}

# Função para carregar o grafo original
def load_original_graph():
    try:
        G = nx.read_graphml('grafo_original.graphml')
        print("Grafo original carregado de grafo_original.graphml")
    except FileNotFoundError:
        G = nx.read_edgelist('facebook_combined.txt', nodetype=int, create_using=nx.Graph())
        print("Grafo original carregado de facebook_combined.txt")
    print("Tipos dos nós:", type(list(G.nodes())[0]))
    print("Exemplo de nós:", list(G.nodes())[:5])
    return G

# Função para carregar o grafo SEIR e os estados
def load_seir_graph():
    G_seir = nx.read_graphml('grafo_seir.graphml')
    status_df = pd.read_csv('status.csv')
    print("Nós em status.csv:", status_df['node'].tolist()[:5])
    print("Nós no grafo SEIR:", list(G_seir.nodes())[:5])
    status_dict = dict(zip(status_df['node'], status_df['status']))
    return G_seir, status_dict

# Função para carregar dados de link prediction
def load_link_prediction_data():
    top10_df = pd.read_csv('top10.csv')
    top_risk_nodes = set(top10_df['node'][:5])  # Top 5 nós de risco
    print("Top 5 nós de risco:", top_risk_nodes)
    return top_risk_nodes

# Função para criar visualização com PyVis
def create_pyvis_graph(G, node_colors, title, output_file):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=False)
    net.from_nx(G)
    
    # Aplicar cores aos nós
    for node in net.nodes:
        node_id = int(node['id'])  # Converter para inteiro
        # Usar cor padrão se node_id não estiver em node_colors
        node['color'] = node_colors.get(node_id, '#669BBC')  # Cor padrão para suscetível
        node['title'] = f"Nó {node_id}"
    
    # Configurações de layout
    net.set_options("""
    var options = {
      "nodes": {
        "shape": "dot",
        "size": 10
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
    
    net.save_graph(output_file)
    print(f"Visualização salva em: {output_file}")

# Visualização do grafo original
def visualize_original_graph():
    G = load_original_graph()
    sample_nodes = list(G.nodes())[:1000]  # Subgrafo com 1000 nós
    # Validar que sample_nodes contém nós válidos
    sample_nodes = [node for node in sample_nodes if node in G.nodes()]
    H = G.subgraph(sample_nodes)
    
    # Todos os nós são suscetíveis (estado 0) no grafo original
    node_colors = {node: color_map[0] for node in H.nodes()}
    
    create_pyvis_graph(H, node_colors, "Grafo Original", "grafo_original.html")

# Visualização do grafo SEIR
def visualize_seir_graph():
    G_seir, status_dict = load_seir_graph()
    sample_nodes = list(G_seir.nodes())[:1000]
    # Validar que sample_nodes contém nós válidos
    sample_nodes = [node for node in sample_nodes if node in G_seir.nodes()]
    H = G_seir.subgraph(sample_nodes)
    
    # Mapear
