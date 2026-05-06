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
    # Caminho ajustado: partindo da raiz do projeto (ingrid-soares/projeto-2/)
    data_dir = os.path.join("data", "ids")
    file_name = "Monday-WorkingHours.pcap_ISCX.csv"
    input_path = os.path.join(data_dir, file_name)
    
    output_csv = os.path.join(data_dir, "cleaned_ids_data.csv")
    output_parquet = os.path.join(data_dir, "cleaned_ids_data.parquet")
    
    try:
        df = preprocess_ids_data(input_path)
        # Salva o arquivo limpo para uso no treinamento em CSV e Parquet
        df.to_csv(output_csv, index=False)
        df.to_parquet(output_parquet, index=False, engine='pyarrow', compression='snappy')
        print(f"Arquivos salvos em {output_csv} e {output_parquet}")
    except Exception as e:
        print(f"Erro: {e}")
