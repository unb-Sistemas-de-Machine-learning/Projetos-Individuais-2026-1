import pandas as pd
import os

def load_and_clean_phishing(file_path):
    """Carrega dados de URLs e limpa para o pipeline NLP."""
    print(f"Lendo dados de phishing: {file_path}")
    df = pd.read_csv(file_path)
    # Limpeza básica (ex: remover linhas com URL vazia)
    df = df.dropna(subset=['url'])
    return df

if __name__ == "__main__":
    # Caminho ajustado para a pasta correta
    data_path = os.path.join("data", "phishing", "phishing_data.csv")
    if os.path.exists(data_path):
        df = load_and_clean_phishing(data_path)
        print(f"Dados carregados. Shape: {df.shape}")
    else:
        print(f"Arquivo {data_path} não encontrado.")
