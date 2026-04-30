import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_clean_data(file_path: str, sample_size: int = None) -> pd.DataFrame:
    """
    Carrega o dataset de tickets, limpa dados ausentes e padroniza as colunas de inferência.

    Args:
        file_path (str): Caminho local para o dataset CSV.
        sample_size (int, opcional): Limite de linhas para processamento (útil para testes de latência).

    Returns:
        pd.DataFrame: Dados higienizados.
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"Dataset não encontrado no path: {file_path}")
        raise FileNotFoundError(f"Arquivo ausente: {file_path}")

    logger.info(f"Iniciando ingestão: {file_path}")
    
    try:
        df = pd.read_csv(path)
        target_columns = ['Ticket Description', 'Ticket Type']
        
        missing_cols = [col for col in target_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Quebra de schema. Colunas ausentes: {missing_cols}")

        df = df[target_columns].copy()
        
        # O modelo falha ao processar tensores com descrições nulas
        initial_len = len(df)
        df.dropna(subset=['Ticket Description'], inplace=True)
        
        if (dropped_len := initial_len - len(df)) > 0:
            logger.warning(f"Qualidade de dados: {dropped_len} linhas descartadas por descrição nula.")

        if sample_size and sample_size < len(df):
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            logger.info(f"Amostragem ativa. Dataset reduzido para {len(df)} amostras.")
            
        return df

    except Exception as e:
        logger.error(f"Falha no pipeline de ingestão: {str(e)}")
        raise

if __name__ == "__main__":
    df_clean = load_and_clean_data("data/customer_support_tickets.csv", sample_size=50)
    print(df_clean.head())
