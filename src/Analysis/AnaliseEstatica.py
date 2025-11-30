import pandas as pd
import networkx as nx
import os
import json 
import community.community_louvain as community_louvain

def analisar_rede_estatica():
    #Definição dos Caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) 

    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Outputs', 'EnronEmailsTratados.csv')

    caminho_saida_dir = os.path.join(root_dir, 'dataSets', 'Outputs')
    caminho_saida_centralidade = os.path.join(caminho_saida_dir, 'centralidade_estatica.csv')
    caminho_saida_comunidades = os.path.join(caminho_saida_dir, 'comunidades_estaticas.json')
    
    caminho_saida_top10_csv = os.path.join(caminho_saida_dir, 'top10_intermediarios.csv')
    caminho_saida_analise_comunidades_csv = os.path.join(caminho_saida_dir, 'analise_comunidades.csv')
    caminho_saida_top5_comunidades_csv = os.path.join(caminho_saida_dir, 'top5_maiores_comunidades.csv')

    caminho_saida_top10_pagerank_csv = os.path.join(caminho_saida_dir, 'top10_pagerank.csv')
    caminho_saida_top10_closeness_csv = os.path.join(caminho_saida_dir, 'top10_closeness.csv')

    #Carregamento dos Dados
    print(f"Carregando dados tratados de: {caminho_entrada}")
    try:
        df = pd.read_csv(caminho_entrada, parse_dates=['data'])
    except FileNotFoundError:
        print(f"ERRO: Arquivo tratado não encontrado em '{caminho_entrada}'.")
        print("Certifique-se de que o script 'PreProcessamento.py' foi executado com sucesso.")
        return

    #Construção do Grafo 
    print("Construindo o grafo")
    
    G = nx.from_pandas_edgelist(
        df,
        'remetente',
        'destinatario',
        create_using=nx.DiGraph()
    )
    print(f"Grafo construído com {G.number_of_nodes()} nós (pessoas) e {G.number_of_edges()} arestas (e-mails).")

    #Cálculo das Métricas de Centralidade
    print("Calculando métricas de centralidade...")
    
    in_degree_centrality = {node: val for node, val in G.in_degree()}
    out_degree_centrality = {node: val for node, val in G.out_degree()}

    print("Calculando centralidade de intermediação")
    betweenness_centrality = nx.betweenness_centrality(G)

    print("Calculando PageRank (para grau de autoridade)")
    pagerank = nx.pagerank(G, alpha=0.85)

    print("Calculando centralidade de proximidade")
    try:
        closeness_centrality = nx.closeness_centrality(G)
    except Exception as e:
        print(f"ERRO ao calcular Closeness Centrality: {e}. Pulando esta métrica.")
        closeness_centrality = {}

    print("Cálculos concluídos.")

    #Organização e Salvamento dos Resultados
    print("Organizando e salvando rankings de centralidade...")
    
    df_centralidade = pd.DataFrame.from_dict({
        'in_degree': in_degree_centrality,
        'out_degree': out_degree_centrality,
        'betweenness': betweenness_centrality,
        'pagerank': pagerank,
        'closeness': closeness_centrality
    })

    df_centralidade = df_centralidade.fillna(0)
    
    df_centralidade.to_csv(caminho_saida_centralidade)
    print(f"Resultados de centralidade salvos em: {caminho_saida_centralidade}")

    print("Salvando o Top 10 de intermediários em um arquivo CSV...")
    df_top10 = df_centralidade.sort_values(by='betweenness', ascending=False).head(10)
    df_top10_betweenness_filtrado = df_top10[['in_degree', 'out_degree', 'betweenness']]
    df_top10_betweenness_filtrado.to_csv(caminho_saida_top10_csv)
    print(f"Top 10 salvo em: {caminho_saida_top10_csv}")

    print("\n--- Top 10 Atores por Intermediação (Betweenness) ---")
    print(df_top10_betweenness_filtrado)

    print("\n--- Top 10 Atores por Autoridade (PageRank) ---")
    df_top10_pagerank = df_centralidade.sort_values(by='pagerank', ascending=False).head(10)
    df_top10_pagerank_filtrado = df_top10_pagerank[['in_degree', 'out_degree', 'pagerank']]
    print(df_top10_pagerank_filtrado)
    
    print("Salvando o Top 10 de PageRank em um arquivo CSV...")
    df_top10_pagerank_filtrado.to_csv(caminho_saida_top10_pagerank_csv)
    print(f"Top 10 PageRank salvo em: {caminho_saida_top10_pagerank_csv}")
    
    print("\n--- Top 10 Atores por Proximidade (Closeness) ---")
    df_top10_closeness = df_centralidade.sort_values(by='closeness', ascending=False).head(10)
    df_top10_closeness_filtrado = df_top10_closeness[['in_degree', 'out_degree', 'closeness']]
    print(df_top10_closeness_filtrado)
    
    print("Salvando o Top 10 de Closeness em um arquivo CSV...")
    df_top10_closeness_filtrado.to_csv(caminho_saida_top10_closeness_csv)
    print(f"Top 10 Closeness salvo em: {caminho_saida_top10_closeness_csv}")
    
    
    #Detecção de Comunidades
    if community_louvain:
        print("\nDetectando comunidades (subgrupos)...")
        G_nao_direcionado = G.to_undirected()
        
        particao = community_louvain.best_partition(G_nao_direcionado, random_state=42)
        
        print(f"Foram detectadas {len(set(particao.values()))} comunidades.")
        
        with open(caminho_saida_comunidades, 'w') as f:
            json.dump(particao, f, indent=4)
        print(f"Mapeamento de comunidades salvo em: {caminho_saida_comunidades}")
        
        #Análise das Comunidades
        print("Realizando análise das comunidades...")
        
        df_centralidade['comunidade_id'] = df_centralidade.index.map(particao)
        
        analise_comunidades_lista = []
        for comm_id, grupo in df_centralidade.groupby('comunidade_id'):
            if grupo.empty:
                continue
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
        
        print("Salvando as 5 maiores comunidades em um arquivo CSV...")
        df_top5_comunidades = df_analise_comunidades.head(5)
        df_top5_comunidades.to_csv(caminho_saida_top5_comunidades_csv, index=False)
        print(f"Top 5 comunidades salvas em: {caminho_saida_top5_comunidades_csv}")
        
        print("\n--- Análise das 5 Maiores Comunidades ---")
        print(df_top5_comunidades)

if __name__ == "__main__":
    analisar_rede_estatica()