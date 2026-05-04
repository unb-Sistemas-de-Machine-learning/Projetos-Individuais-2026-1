import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest
import os

# Caminho base para os dados (CSV e Parquet)
DATA_DIR = os.path.join("data", "ids")
CSV_PATH = os.path.join(DATA_DIR, "cleaned_ids_data.csv")
PARQUET_PATH = os.path.join(DATA_DIR, "cleaned_ids_data.parquet")

def load_data(csv_path, parquet_path):
    """Carrega dados em Parquet (preferencial) ou CSV."""
    if os.path.exists(parquet_path):
        print(f"Carregando dados via Parquet: {parquet_path}")
        return pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        print(f"Carregando dados via CSV: {csv_path}")
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(f"Dados não encontrados em {csv_path} ou {parquet_path}")

def train_and_log_model(csv_path, parquet_path, contamination=0.01):
    """
    Treina um modelo Isolation Forest, registra métricas de anomalia e o modelo no MLflow.
    """
    df = load_data(csv_path, parquet_path)
    X = df.select_dtypes(include=['number'])
    
    # Iniciar experimento no MLflow
    mlflow.set_experiment("IDS_CICIDS2017_Anomalia")
    
    print("Iniciando treinamento com MLflow...")
    with mlflow.start_run(run_name="IsolationForest_PortScan"):
        # Treinar modelo
        model = IsolationForest(contamination=contamination, random_state=42)
        preds = model.fit_predict(X)
        
        # Contagem de anomalias (-1 é a classe de anomalia no IsolationForest)
        n_anomalies = (preds == -1).sum()
        n_normal = (preds == 1).sum()
        
        # Log de parâmetros
        mlflow.log_param("model_type", "IsolationForest")
        mlflow.log_param("contamination", contamination)
        
        # Log de métricas
        mlflow.log_metric("n_anomalies", n_anomalies)
        mlflow.log_metric("n_normal", n_normal)
        
        # Log do modelo
        mlflow.sklearn.log_model(model, "ids_model")
        
        print(f"Treino finalizado. Anomalias detectadas: {n_anomalies}")
        print("Modelo registrado com sucesso no MLflow.")

if __name__ == "__main__":
    train_and_log_model(CSV_PATH, PARQUET_PATH)
