import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest
import os

# Caminho relativo simples: a partir de ingrid-soares/projeto-2/
DATA_PATH = os.path.join("data", "ids", "cleaned_ids_data.csv")

def train_and_log_model(data_path, contamination=0.01):
    """
    Treina um modelo Isolation Forest, registra métricas de anomalia e o modelo no MLflow.
    """
    if not os.path.exists(data_path):
        print(f"Erro: Arquivo '{data_path}' não encontrado. Verifique se você está na pasta 'ingrid-soares/projeto-2/'.")
        return

    print(f"Carregando dados de: {data_path}")
    df = pd.read_csv(data_path)
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
        
        # Log de métricas (para gerar gráficos no MLflow)
        mlflow.log_metric("n_anomalies", n_anomalies)
        mlflow.log_metric("n_normal", n_normal)
        
        # Log do modelo
        mlflow.sklearn.log_model(model, "ids_model")
        
        print(f"Treino finalizado. Anomalias detectadas: {n_anomalies}")
        print("Modelo registrado com sucesso no MLflow.")

if __name__ == "__main__":
    train_and_log_model(DATA_PATH)
