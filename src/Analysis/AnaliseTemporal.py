import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt

def analisar_rede_temporal():
    """
    Função principal que carrega os dados tratados e analisa a evolução
    das métricas de centralidade ao longo do tempo (por "janelas").
    """
    
    # --- 1. Definição dos Caminhos ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..')) # Volta para a raiz do projeto

    # Caminho de entrada (os dados limpos da etapa 1)
    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Outputs', 'EnronEmailsTratados.csv')

    # Caminhos de saída para os resultados desta análise
    caminho_saida_dir = os.path.join(root_dir, 'dataSets', 'Outputs')
    caminho_saida_csv = os.path.join(caminho_saida_dir, 'centralidade_temporal.csv')
    caminho_saida_grafico = os.path.join(caminho_saida_dir, 'evolucao_centralidade.png')

# --- 2. Carregamento e Preparação dos Dados ---
    print(f"Carregando dados tratados de: {caminho_entrada}")
    try:
        df = pd.read_csv(caminho_entrada) # 1. Carregue sem o parse_dates
    except FileNotFoundError:
        print(f"ERRO: Arquivo tratado não encontrado em '{caminho_entrada}'.")
        print("Certifique-se de que o script 'PreProcessamento.py' foi executado com sucesso.")
        return

    # 2. Forçar a conversão para datetime APÓS carregar
    # 'errors='coerce'' transforma datas inválidas (como "2044") em NaT (Not a Time)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    
    # 3. Remover quaisquer linhas que falharam na conversão
    df = df.dropna(subset=['data'])

    # 4. Agora sim, definir a coluna 'data' como o índice do DataFrame.
    df = df.set_index('data')   
    df = df.sort_index()
    
    print(f"Dados carregados. Período total: {df.index.min()} a {df.index.max()}")

    # --- 3. Análise por Janelas de Tempo ---
    
    # Definir a janela de tempo. 'Q' = Trimestral (Quarterly).
    # Você pode mudar para 'M' (Mensal) se quiser mais granularidade,
    # mas 'Q' é um bom começo.
    janela_de_tempo = 'QE'
    
    print(f"Iniciando análise temporal com janelas '{janela_de_tempo}' (Trimestral)...")
    
    # Agrupar o DataFrame por trimestre
    # 'resample' cria "caixas" de tempo (neste caso, trimestres)
    grupos_temporais = df.resample(janela_de_tempo)
    
    # Lista para armazenar os resultados de cada trimestre
    resultados_temporais = []

    for periodo, df_periodo in grupos_temporais:
        print(f"Processando período: {periodo.strftime('%Y-%m')}...")
        
        if df_periodo.empty:
            print("  - Nenhum dado neste período, pulando.")
            continue
            
        # 1. Criar o grafo para este período específico
        G_periodo = nx.from_pandas_edgelist(
            df_periodo,
            'remetente',
            'destinatario',
            create_using=nx.DiGraph()
        )
        
        if G_periodo.number_of_nodes() == 0:
            print("  - Grafo vazio neste período, pulando.")
            continue
            
        # 2. Calcular a centralidade de intermediação (pode demorar)
        # Usamos a aproximação 'k=100' para ser rápido.
        # Remova 'k=100' para um cálculo exato (muito lento).
        try:
            betweenness_periodo = nx.betweenness_centrality(G_periodo)
        except Exception as e:
            print(f"  - Erro ao calcular betweenness: {e}")
            continue

        # 3. Formatar os resultados
        for pessoa, centralidade in betweenness_periodo.items():
            resultados_temporais.append({
                'data': periodo,
                'pessoa': pessoa,
                'betweenness': centralidade
            })
            
    print("Análise temporal concluída.")

    # --- 4. Consolidação e Salvamento dos Resultados ---
    if not resultados_temporais:
        print("Nenhum resultado temporal foi gerado. Encerrando.")
        return
        
    # Converter a lista de resultados em um DataFrame
    df_temporal = pd.DataFrame(resultados_temporais)
    
    # Pivotar a tabela para que as colunas sejam as pessoas e as linhas sejam as datas
    # Isso facilita a leitura e a plotagem
    df_pivot = df_temporal.pivot(index='data', columns='pessoa', values='betweenness')
    
    # Preencher com 0 os períodos em que uma pessoa não estava ativa
    df_pivot = df_pivot.fillna(0)
    
    # Salvar o DataFrame temporal em CSV
    df_pivot.to_csv(caminho_saida_csv)
    print(f"Resultados da análise temporal salvos em: {caminho_saida_csv}")
    
    # --- 5. Visualização (Exemplo) ---
    print("Gerando gráfico de exemplo...")
    
    # Vamos plotar a evolução dos Top 5 atores da análise ESTÁTICA
    atores_estaticos_top = [
        'jeff.dasovich@enron.com',
        'tana.jones@enron.com',
        'vince.kaminski@enron.com',
        'sara.shackleton@enron.com',
        'gerald.nemec@enron.com'
    ]
    
    # Filtrar o DataFrame para incluir apenas colunas que realmente existem
    atores_para_plotar = [ator for ator in atores_estaticos_top if ator in df_pivot.columns]
    
    if atores_para_plotar:
        plt.figure(figsize=(15, 7))
        df_pivot[atores_para_plotar].plot(ax=plt.gca())
        
        plt.title('Evolução da Centralidade de Intermediação (Betweenness) - Top 5 Atores Estáticos')
        plt.xlabel('Período (Trimestral)')
        plt.ylabel('Pontuação de Betweenness')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid(True)
        plt.tight_layout()
        
        plt.savefig(caminho_saida_grafico, bbox_inches='tight')
        print(f"Gráfico de evolução salvo em: {caminho_saida_grafico}")
    else:
        print("Nenhum dos atores estáticos top foi encontrado nos dados temporais para plotar.")


# Bloco principal
if __name__ == "__main__":
    analisar_rede_temporal()