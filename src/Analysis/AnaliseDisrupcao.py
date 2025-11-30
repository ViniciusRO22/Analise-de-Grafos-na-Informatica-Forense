import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt

def simular_ataque(G_original, lista_alvos, nome_estrategia):
    #Remove nós da lista um a um e mede o tamanho do maior componente conectado.
   
    print(f"--- Iniciando simulação: {nome_estrategia} ---")
    
    G = G_original.copy()
    G_und = G.to_undirected()
    
    if len(G_und) > 0:
        maior_componente_inicial = len(max(nx.connected_components(G_und), key=len))
    else:
        maior_componente_inicial = 0
        
    print(f"  Tamanho inicial: {maior_componente_inicial} nós")
    
    historico_integridade = [100.0]
    
    for i, alvo in enumerate(lista_alvos):
        if alvo in G:
            G.remove_node(alvo)
            if alvo in G_und:
                G_und.remove_node(alvo)
            
            if len(G_und) > 0:
                maior_componente = len(max(nx.connected_components(G_und), key=len))
                porcentagem = (maior_componente / maior_componente_inicial) * 100
            else:
                porcentagem = 0.0
            
            historico_integridade.append(porcentagem)
            print(f"    - Removido {alvo}: {porcentagem:.2f}% restante")
        else:
            historico_integridade.append(historico_integridade[-1])
            print(f"    - Alvo {alvo} não encontrado no grafo.")
            
    return historico_integridade

def executar_analise_disrupcao():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) 

    caminho_dados = os.path.join(root_dir, 'dataSets', 'Outputs', 'EnronEmailsTratados.csv')
    caminho_top10_betweenness = os.path.join(root_dir, 'dataSets', 'Outputs', 'top10_intermediarios.csv')
    caminho_top10_pagerank = os.path.join(root_dir, 'dataSets', 'Outputs', 'top10_pagerank.csv')
    caminho_saida_grafico = os.path.join(root_dir, 'dataSets', 'Outputs', 'analise_disrupcao.png')

    print("Carregando grafo...")
    try:
        df = pd.read_csv(caminho_dados)
        G = nx.from_pandas_edgelist(df, 'remetente', 'destinatario', create_using=nx.DiGraph())
    except Exception as e:
        print(f"Erro ao carregar grafo: {e}")
        return

    try:
        # Lista 1: Intermediários (Betweenness) -> Estratégia de Fragmentação
        df_bet = pd.read_csv(caminho_top10_betweenness)
        alvos_brokers = df_bet.iloc[:, 0].tolist()

        # Lista 2: Autoridades (PageRank) -> Estratégia de Decapitação
        df_page = pd.read_csv(caminho_top10_pagerank)
        alvos_autoridades = df_page.iloc[:, 0].tolist()
        
        # Lista 3: Elite Estrutural 
        alvos_elite = [
            'kenneth.lay@enron.com',
            'jeff.skilling@enron.com',
            'tana.jones@enron.com',
            'sally.beck@enron.com',
            'louise.kitchen@enron.com',
            'jeff.dasovich@enron.com'   
        ]
        
    except Exception as e:
        print(f"Erro ao carregar listas: {e}")
        return

    # Simulações
    res_brokers = simular_ataque(G, alvos_brokers, "Intermediários (Betweenness)")
    res_autoridades = simular_ataque(G, alvos_autoridades, "Autoridades (PageRank)")
    res_elite = simular_ataque(G, alvos_elite, "Elite Estrutural (Manual)")

    print("Gerando gráfico...")
    plt.figure(figsize=(10, 6))
    
    plt.plot(res_brokers, marker='o', color='red', label='Intermediários (Fragmentação)')
    plt.plot(res_autoridades, marker='s', color='blue', linestyle='--', label='Autoridades (Decapitação)')
    plt.plot(res_elite, marker='^', color='green', linestyle='-.', label='Elite Estrutural')
    
    plt.title('Simulação de Disrupção da Rede: Comparação de Estratégias')
    plt.xlabel('Número de Nós Removidos')
    plt.ylabel('Tamanho do Componente Gigante (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(caminho_saida_grafico)
    print(f"Gráfico salvo em: {caminho_saida_grafico}")

if __name__ == "__main__":
    executar_analise_disrupcao()