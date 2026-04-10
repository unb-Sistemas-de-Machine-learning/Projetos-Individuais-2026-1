import pandas as pd
import os

DATA_DIR = os.path.join("data", "phishing")
CSV_PATH = os.path.join(DATA_DIR, "phishing_data.csv")
PARQUET_PATH = os.path.join(DATA_DIR, "phishing_data.parquet")

def preprocess_phishing():
    """Carrega dados, limpa e salva em Parquet para performance."""
    if not os.path.exists(CSV_PATH):
        print(f"Erro: Arquivo original {CSV_PATH} não encontrado.")
        return
    
    print(f"Lendo: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    
    # Limpeza básica (ex: remover duplicatas e valores nulos se houver)
    df = df.drop_duplicates()
    df = df.dropna()
    
    # Salvar em Parquet para performance
    df.to_parquet(PARQUET_PATH, index=False, engine='pyarrow', compression='snappy')
    print(f"Dataset processado e salvo em Parquet: {PARQUET_PATH}")

if __name__ == "__main__":
    preprocess_phishing()
