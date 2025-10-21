import pandas as pd
import networkx as nx
import os
import json 
import matplotlib.pyplot as plt

# Importa a biblioteca 'python-louvain' (instalada como 'community')
# com um nome claro para não confundir com o módulo do networkx
try:
    from networkx import community as community_louvain
except ImportError:
    print("Biblioteca 'python-louvain' não encontrada. Detecção de comunidade será pulada.")
    print("Para instalar, rode: pip install python-louvain community")
    community_louvain = None

def analisar_rede_estatica():
    """
    Função principal que carrega os dados tratados, constrói um grafo estático,
    calcula métricas de centralidade e detecta comunidades.
    """
    
    # --- 1. Definição dos Caminhos ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) 

    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Outputs', 'EnronEmailsTratados.csv')

    caminho_saida_dir = os.path.join(root_dir, 'dataSets', 'Outputs')
    caminho_saida_centralidade = os.path.join(caminho_saida_dir, 'centralidade_estatica.csv')
    caminho_saida_comunidades = os.path.join(caminho_saida_dir, 'comunidades_estaticas.json')
    
    caminho_saida_top10_csv = os.path.join(caminho_saida_dir, 'top10_intermediarios.csv')
    caminho_saida_analise_comunidades_csv = os.path.join(caminho_saida_dir, 'analise_comunidades.csv')
    caminho_saida_grafo_comunidades_png = os.path.join(caminho_saida_dir, 'grafo_comunidades.png')
    caminho_saida_grafo_completo_png = os.path.join(caminho_saida_dir, 'grafo_completo.png')

    # --- NOVO Caminho de Saída ---
    caminho_saida_top5_comunidades_csv = os.path.join(caminho_saida_dir, 'top5_maiores_comunidades.csv')


    # --- 2. Carregamento dos Dados ---
    print(f"Carregando dados tratados de: {caminho_entrada}")
    try:
        df = pd.read_csv(caminho_entrada, parse_dates=['data'])
    except FileNotFoundError:
        print(f"ERRO: Arquivo tratado não encontrado em '{caminho_entrada}'.")
        print("Certifique-se de que o script 'PreProcessamento.py' foi executado com sucesso.")
        return

    # --- 3. Construção do Grafo Estático ---
    print("Construindo o grafo estático agregado...")
    
    G = nx.from_pandas_edgelist(
        df,
        'remetente',
        'destinatario',
        create_using=nx.DiGraph()
    )
    print(f"Grafo construído com {G.number_of_nodes()} nós (pessoas) e {G.number_of_edges()} arestas (e-mails).")

    # --- 4. Cálculo das Métricas de Centralidade ---
    print("Calculando métricas de centralidade...")
    
    in_degree_centrality = {node: val for node, val in G.in_degree()}
    out_degree_centrality = {node: val for node, val in G.out_degree()}

    print("Calculando centralidade de intermediação (pode demorar)...")
    
    betweenness_centrality = nx.betweenness_centrality(G)

    print("Cálculo de centralidade concluído.")

    # --- 5. Organização e Salvamento dos Resultados ---
    print("Organizando e salvando rankings de centralidade...")
    
    df_centralidade = pd.DataFrame.from_dict({
        'in_degree': in_degree_centrality,
        'out_degree': out_degree_centrality,
        'betweenness': betweenness_centrality,
    })
    
    df_centralidade = df_centralidade.sort_values(by='betweenness', ascending=False)
    
    df_centralidade.to_csv(caminho_saida_centralidade)
    print(f"Resultados de centralidade salvos em: {caminho_saida_centralidade}")

    # --- 5.1. Salvar o Top 10 Intermediários ---
    print("Salvando o Top 10 de intermediários em um arquivo CSV...")
    df_top10 = df_centralidade.head(10)
    df_top10.to_csv(caminho_saida_top10_csv)
    print(f"Top 10 salvo em: {caminho_saida_top10_csv}")

    print("\n--- Top 10 Atores por Intermediação (Betweenness) ---")
    print(df_top10)
    
    # --- 5.2. Visualização do Grafo Completo (Com Aviso) ---
    print(f"AVISO: Iniciando a renderização do grafo completo ({G.number_of_nodes()} nós)...")
    print("Isto pode demorar MUITO e a imagem final será muito densa e ilegível.")
    
    try:
        plt.figure(figsize=(50, 50)) 
        # (Requer 'pip install scipy')
        pos = nx.spring_layout(G, k=0.01, iterations=10, seed=42) 
        
        nx.draw_networkx_nodes(G, pos, node_size=1, node_color='k', alpha=0.5)
        nx.draw_networkx_edges(G, pos, width=0.01, edge_color='gray', alpha=0.1)
        
        plt.title("Visualização do Grafo Completo (Renderização de Alta Densidade)", fontsize=50)
        plt.axis('off')
        plt.savefig(caminho_saida_grafo_completo_png, dpi=300, bbox_inches='tight')
        plt.close() 
        print(f"Imagem do grafo completo salva em: {caminho_saida_grafo_completo_png}")
    except ImportError:
        print("ERRO: 'scipy' não encontrado. Não foi possível gerar a imagem do grafo.")
        print("Para instalar, rode: pip install scipy")
    except Exception as e:
        print(f"ERRO ao gerar imagem do grafo completo: {e}")
        print("Pulando esta etapa. O grafo é provavelmente grande demais para renderizar.")


    # --- 6. Detecção de Comunidades ---
    if community_louvain:
        print("\nDetectando comunidades (subgrupos)...")
        G_nao_direcionado = G.to_undirected()
        
        particao = community_louvain.best_partition(G_nao_direcionado, random_state=42)
        print(f"Foram detectadas {len(set(particao.values()))} comunidades.")
        
        with open(caminho_saida_comunidades, 'w') as f:
            json.dump(particao, f, indent=4)
        print(f"Mapeamento de comunidades salvo em: {caminho_saida_comunidades}")
        
        # --- 6.1. Análise Robusta das Comunidades ---
        print("Realizando análise das comunidades...")
        
        df_centralidade['comunidade_id'] = df_centralidade.index.map(particao)
        
        analise_comunidades_lista = []
        for comm_id, grupo in df_centralidade.groupby('comunidade_id'):
            lider_comm = grupo['betweenness'].idxmax()
            num_membros = len(grupo)
            
            analise_comunidades_lista.append({
                'id_comunidade': comm_id,
                'num_membros': num_membros,
                'lider_intermediario_interno': lider_comm
            })
            
        df_analise_comunidades = pd.DataFrame(analise_comunidades_lista)
        df_analise_comunidades = df_analise_comunidades.sort_values(by='num_membros', ascending=False)
        
        df_analise_comunidades.to_csv(caminho_saida_analise_comunidades_csv, index=False)
        print(f"Análise de comunidades salva em: {caminho_saida_analise_comunidades_csv}")
        
        # --- ALTERAÇÃO SOLICITADA ---
        # Salva as 5 maiores comunidades em um arquivo CSV separado
        print("Salvando as 5 maiores comunidades em um arquivo CSV...")
        df_top5_comunidades = df_analise_comunidades.head(5)
        df_top5_comunidades.to_csv(caminho_saida_top5_comunidades_csv, index=False)
        print(f"Top 5 comunidades salvas em: {caminho_saida_top5_comunidades_csv}")
        
        # Você pode manter ou remover o print no terminal, vou mantê-lo por clareza.
        print("\n--- Análise das 5 Maiores Comunidades ---")
        print(df_top5_comunidades)

        # --- 6.2. Visualização do Grafo de Comunidades (Metagrafo) ---
        print("Gerando o metagrafo de comunidades...")
        
        M = community_louvain.induced_graph(particao, G_nao_direcionado)
        
        plt.figure(figsize=(20, 20))
        
        # Requer 'pip install scipy'
        pos = nx.spring_layout(M, k=0.2, iterations=50, seed=42)
        
        mapa_tamanhos = df_analise_comunidades.set_index('id_comunidade')['num_membros'].to_dict()
        tamanhos_nos = [mapa_tamanhos.get(node, 0) * 0.1 for node in M.nodes()]
        
        larguras_arestas = [d.get('weight', 0) / 10 for u, v, d in M.edges(data=True)]
        
        nx.draw_networkx_nodes(M, pos, node_size=tamanhos_nos, node_color='lightblue', alpha=0.8)
        nx.draw_networkx_edges(M, pos, width=larguras_arestas, edge_color='gray', alpha=0.5)
        
        top_10_comm_ids = df_analise_comunidades.head(10)['id_comunidade'].tolist()
        labels = {n: str(n) for n in M.nodes() if n in top_10_comm_ids}
        
        nx.draw_networkx_labels(M, pos, font_size=12, labels=labels)
        
        plt.title("Metagrafo de Comunidades (Nós = Comunidades, Arestas = Conexões entre elas)")
        plt.axis('off')
        plt.savefig(caminho_saida_grafo_comunidades_png)
        plt.close() 
        print(f"Metagrafo de comunidades salvo em: {caminho_saida_grafo_comunidades_png}")


# Bloco principal
if __name__ == "__main__":
    analisar_rede_estatica()