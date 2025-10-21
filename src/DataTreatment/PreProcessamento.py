import pandas as pd
import re
import os 

def processar_dados():
    """
    Função principal que carrega, processa e salva os dados de e-mail da Enron.
    """
    
    # --- 1. Definição dos Caminhos (MÉTODO ROBUSTO) ---
    
    # Pega o caminho absoluto do diretório onde este script (PreProcessamento.py) está
    # Ex: C:/.../COMO A ANÁLISE DE CENTRALI.../src/DataTreatment
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Constrói o caminho para o diretório raiz do projeto (voltando duas pastas)
    # Ex: C:/.../COMO A ANÁLISE DE CENTRALI.../
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))

    # Agora, constrói os caminhos de entrada e saída a partir da raiz do projeto
    # Isso funcionará independentemente de onde você executar o script
    caminho_entrada = os.path.join(root_dir, 'dataSets', 'Inputs', 'EnronEmails.csv')
    caminho_saida_dir = os.path.join(root_dir, 'dataSets', 'Outputs')
    caminho_saida_arquivo = os.path.join(caminho_saida_dir, 'EnronEmailsTratados.csv')

    print(f"Carregando dataset de: {caminho_entrada}")
    
    # --- 2. Carregamento dos Dados ---
    try:
        # Carrega o dataset completo. Remova nrows para processar tudo.
        df = pd.read_csv(caminho_entrada)
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em '{caminho_entrada}'. Verifique a estrutura de pastas.")
        return

    # --- 3. Extração dos Campos do E-mail ---
    def extrair_campo(texto_mensagem, campo):
        padrao = re.search(f"^{campo}: (.*)", texto_mensagem, re.MULTILINE)
        if padrao:
            return padrao.group(1).strip()
        return None

    print("Extraindo campos 'From', 'To' e 'Date'...")
    # (O resto do seu código continua exatamente igual...)
    # ... (cole o restante do seu código a partir daqui)
    df['remetente'] = df['message'].apply(lambda msg: extrair_campo(msg, 'From'))
    df['destinatario_raw'] = df['message'].apply(lambda msg: extrair_campo(msg, 'To'))
    df['data_raw'] = df['message'].apply(lambda msg: extrair_campo(msg, 'Date'))

    # --- 4. Limpeza e Padronização ---
    print("Limpando e padronizando os dados...")
    
    df['data'] = pd.to_datetime(df['data_raw'], errors='coerce')
    df_limpo = df.dropna(subset=['remetente', 'destinatario_raw', 'data'])
    
    # O aviso 'SettingWithCopyWarning' pode aparecer aqui, é esperado com esta abordagem.
    df_limpo['destinatarios_lista'] = df_limpo['destinatario_raw'].str.split(',')

    # --- 5. Normalização da Tabela (Explode) ---
    print("Normalizando a tabela de interações...")
    
    df_final = df_limpo.explode('destinatarios_lista')
    df_final = df_final.rename(columns={'destinatarios_lista': 'destinatario'})

    df_final['remetente'] = df_final['remetente'].str.strip().str.lower()
    df_final['destinatario'] = df_final['destinatario'].str.strip().str.lower()

    df_final = df_final[['remetente', 'destinatario', 'data']]
    df_final.dropna(inplace=True)
    df_final = df_final[df_final['destinatario'] != '']
    
    # --- 6. Salvando o Resultado ---
    print(f"Salvando o arquivo processado em: {caminho_saida_arquivo}")

    # Garante que o diretório de saída exista antes de salvar
    os.makedirs(caminho_saida_dir, exist_ok=True)
    
    # Salva o DataFrame final em um novo arquivo CSV, sem o índice.
    df_final.to_csv(caminho_saida_arquivo, index=False)
    
    print("\n--- Pré-processamento concluído com sucesso! ---")
    print(f"Total de {len(df_final)} interações salvas.")

# Bloco principal para executar a função quando o script for chamado
if __name__ == "__main__":
    processar_dados()