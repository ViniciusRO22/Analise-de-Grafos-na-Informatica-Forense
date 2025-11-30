import pandas as pd
import re
import os

def processar_dados():    
    #Definição dos Caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Inputs', 'EnronEmails.csv')
    caminho_saida_dir = os.path.join(root_dir, 'dataSets', 'Outputs')
    caminho_saida_arquivo = os.path.join(caminho_saida_dir, 'EnronEmailsTratados.csv')

    print(f"Carregando dataset de: {caminho_entrada}")
    
    #Carregamento dos Dados
    try:
        df = pd.read_csv(caminho_entrada)
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em '{caminho_entrada}'.")
        return

    #Extração dos Campos do E-mail
    def extrair_campo(texto_mensagem, campo):
        padrao = re.search(f"^{campo}: (.*)", texto_mensagem, re.MULTILINE)
        if padrao:
            return padrao.group(1).strip()
        return None

    print("Extraindo campos 'From', 'To' e 'Date'...")
    df['remetente'] = df['message'].apply(lambda msg: extrair_campo(msg, 'From'))
    df['destinatario_raw'] = df['message'].apply(lambda msg: extrair_campo(msg, 'To'))
    df['data_raw'] = df['message'].apply(lambda msg: extrair_campo(msg, 'Date'))

    #Limpeza e Padronização dos Dados
    print("Limpando e padronizando os dados...")
    
    df['data'] = pd.to_datetime(df['data_raw'], errors='coerce', utc=True)
    df_limpo = df.dropna(subset=['remetente', 'destinatario_raw', 'data'])
    df_limpo['destinatarios_lista'] = df_limpo['destinatario_raw'].str.split(',')

    #Normalização da Tabela (Explode)
    print("Normalizando a tabela de interações...")
    
    df_final = df_limpo.explode('destinatarios_lista')
    df_final = df_final.rename(columns={'destinatarios_lista': 'destinatario'})
    df_final['remetente'] = df_final['remetente'].str.strip().str.lower()
    df_final['destinatario'] = df_final['destinatario'].str.strip().str.lower()
    df_final = df_final[['remetente', 'destinatario', 'data']]
    df_final.dropna(inplace=True)
    df_final = df_final[df_final['destinatario'] != '']
    
    #Filtro de Datas Inválidas
    print(f"Dados brutos: {len(df_final)} interações.")
    
    start_date = pd.to_datetime('1985-01-01', utc=True)
    end_date = pd.to_datetime('2003-12-31', utc=True)
    
    print(f"Filtrando datas para o período principal: {start_date.year} a {end_date.year}")
    
    df_final = df_final[(df_final['data'] >= start_date) & (df_final['data'] <= end_date)]
    
    print(f"Dados limpos (filtrados por data): {len(df_final)} interações.")

    #Salvando o Resultado
    print(f"Salvando o arquivo processado em: {caminho_saida_arquivo}")

    os.makedirs(caminho_saida_dir, exist_ok=True)
    df_final.to_csv(caminho_saida_arquivo, index=False)
    
    print("\n--- Pré-processamento concluído com sucesso!")

if __name__ == "__main__":
    processar_dados()