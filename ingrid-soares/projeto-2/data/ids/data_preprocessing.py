import pandas as pd
import numpy as np
import os

def clean_column_names(df):
    """Remove espaços em branco dos nomes das colunas."""
    df.columns = df.columns.str.strip()
    return df

def preprocess_ids_data(file_path):
    """Carrega e limpa o dataset CICIDS2017."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    print(f"Lendo: {file_path}")
    df = pd.read_csv(file_path)
    df = clean_column_names(df)
    
    # Tratamento de valores infinitos e nulos
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    
    print(f"Limpeza concluída. Shape final: {df.shape}")
    return df

if __name__ == "__main__":
    # Exemplo de uso
    data_dir = "data/ids"
    file_name = "Monday-WorkingHours.pcap_ISCX.csv"
    path = os.path.join(data_dir, file_name)
    
    try:
        df = preprocess_ids_data(path)
        # Salva o arquivo limpo para uso no treinamento
        df.to_csv(os.path.join(data_dir, "cleaned_ids_data.csv"), index=False)
        print("Arquivo limpo salvo em data/ids/cleaned_ids_data.csv")
    except Exception as e:
        print(f"Erro: {e}")
