import pandas as pd
import networkx as nx
import os
from pyvis.network import Network

def plotar_subgrafo_interativo(no_de_interesse):
    print(f"\n--- Iniciando visualização interativa de subgrafo para: {no_de_interesse} ---")
    
    #Definição dos Caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) 

    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Outputs', 'EnronEmailsTratados.csv')
    caminho_saida_html = os.path.join(root_dir, 'dataSets', 'Outputs', f'subgrafo_interativo_{no_de_interesse}.html')

    #Carregamento e Criação do Grafo Completo 
    print("Carregando e criando o grafo completo G...")
    try:
        df = pd.read_csv(caminho_entrada)
    except FileNotFoundError:
        print(f"ERRO: Arquivo tratado não encontrado em '{caminho_entrada}'.")
        return
        
    G = nx.from_pandas_edgelist(
        df,
        'remetente',
        'destinatario',
        create_using=nx.DiGraph()
    )
    
    if no_de_interesse not in G:
        print(f"ERRO: Nó '{no_de_interesse}' não existe no grafo. Pulando este nó.")
        return

    #Criação do Subgrafo
    print("Extraindo o subgrafo (vizinhos de 1º grau)")
    
    sucessores = list(G.successors(no_de_interesse))
    predecessores = list(G.predecessors(no_de_interesse))
    
    nos_do_subgrafo = set(sucessores + predecessores + [no_de_interesse])
    
    G_sub = G.subgraph(nos_do_subgrafo)
    
    print(f"Subgrafo criado com {G_sub.number_of_nodes()} nós e {G_sub.number_of_edges()} arestas.")

    # Criação da Visualização Interativa
    print("Renderizando o grafo interativo com Pyvis...")
    
    net = Network(height="900px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.from_nx(G_sub)
    
    try:
        net.get_node(no_de_interesse)['color'] = 'red'
        net.get_node(no_de_interesse)['size'] = 50
    except:
        pass 

    net.toggle_physics(True)
    net.save_graph(caminho_saida_html)
    
    print(f"Grafo interativo salvo em: {caminho_saida_html}")


if __name__ == "__main__":
    
    #Lista 1: Top 10 Betweenness
    list_betweenness = [
        'jeff.dasovich@enron.com',
        'tana.jones@enron.com',
        'vince.kaminski@enron.com',
        'sara.shackleton@enron.com',
        'gerald.nemec@enron.com',
        'sally.beck@enron.com',
        'louise.kitchen@enron.com',
        'kenneth.lay@enron.com',
        'jeff.skilling@enron.com',
        'kay.mann@enron.com'
    ]
    
    #Lista 2: Top 10 PageRank
    list_pagerank = [
        'klay@enron.com',
        'jeff.skilling@enron.com',
        'kenneth.lay@enron.com',
        'sara.shackleton@enron.com',
        'tana.jones@enron.com',
        'ebass@enron.com',
        'louise.kitchen@enron.com',
        'jeff.dasovich@enron.com',
        'sally.beck@enron.com',
        'gerald.nemec@enron.com'
    ]
    
    #Lista 3: Top 10 Closeness
    list_closeness = [
        'louise.kitchen@enron.com',
        'john.lavorato@enron.com',
        'sally.beck@enron.com',
        'tim.belden@enron.com',
        'greg.whalley@enron.com',
        'kenneth.lay@enron.com',
        'david.delainey@enron.com',
        'jeff.skilling@enron.com',
        'tana.jones@enron.com',
        'elizabeth.sager@enron.com'
    ]
    
    lista_combinada = list_betweenness + list_pagerank + list_closeness
    atores_unicos = set(lista_combinada)
    
    print(f"--- Iniciando a geração de {len(atores_unicos)} subgrafos interativos ---")
    
    for ator in atores_unicos:
        plotar_subgrafo_interativo(no_de_interesse=ator)
        
    print(f"\n--- Geração de subgrafos concluída. {len(atores_unicos)} arquivos .html foram criados na pasta 'dataSets/Outputs/'. ---")