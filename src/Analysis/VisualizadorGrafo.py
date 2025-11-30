import pandas as pd
import networkx as nx
import os

def exportar_estrutura_grafo_txt():

    print("Iniciando a exportação da estrutura do grafo para validação...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) 

    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Outputs', 'EnronEmailsTratados.csv')
    caminho_saida_txt = os.path.join(root_dir, 'dataSets', 'Outputs', 'visualizador_grafo.txt')

    print(f"Carregando dados tratados de: {caminho_entrada}")
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
    
    print(f"Grafo construído com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")

    #Extração da Estrutura do Grafo
    print("Extraindo predecessores e sucessores de cada nó...")
    
    estrutura_grafo = {}
    for node in G.nodes():
        predecessores = list(G.predecessors(node))
        sucessores = list(G.successors(node))
        
        estrutura_grafo[node] = {
            'recebeu_de_predecessores': predecessores,
            'enviou_para_sucessores': sucessores
        }
    
    print("Extração concluída.")

    print(f"Salvando a estrutura do grafo em: {caminho_saida_txt}")
    
    with open(caminho_saida_txt, 'w', encoding='utf-8') as f:
        
        for node, data in estrutura_grafo.items():
            
            f.write("==================================================\n")
            f.write(f" NÓ (PESSOA): {node}\n")
            f.write("==================================================\n\n")
            
            f.write("--> RECEBEU E-MAIL DE (Predecessores):\n")
            if data['recebeu_de_predecessores']:
                for predecessor in data['recebeu_de_predecessores']:
                    f.write(f"    - {predecessor}\n")
            else:
                f.write("    (Nenhum)\n")
            
            f.write("\n") 
    
            f.write("--> ENVIOU E-MAIL PARA (Sucessores):\n")
            if data['enviou_para_sucessores']:
                for sucessor in data['enviou_para_sucessores']:
                    f.write(f"    - {sucessor}\n")
            else:
                f.write("    (Nenhum)\n")
            
            f.write("\n\n") 
        
    print(f"\nArquivo de validação '{os.path.basename(caminho_saida_txt)}' foi criado.")

if __name__ == "__main__":
    exportar_estrutura_grafo_txt()