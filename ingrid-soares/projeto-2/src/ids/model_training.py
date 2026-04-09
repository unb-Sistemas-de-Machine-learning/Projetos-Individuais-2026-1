import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest
import os

# Define a pasta raiz do projeto de forma dinâmica
PROJECT_ROOT = os.path.join("ingrid-soares", "projeto-2")

def train_and_log_model(data_path, contamination=0.01):
    """
    Treina um modelo Isolation Forest para detecção de anomalias (Port Scanning)
    e registra o modelo, parâmetros e métricas no MLflow.
    """
    if not os.path.exists(data_path):
        print(f"Erro: Arquivo {data_path} não encontrado. Execute o pré-processamento primeiro.")
        return

    print("Carregando dados para treinamento...")
    df = pd.read_csv(data_path)
    # Seleção de colunas numéricas para o Isolation Forest
    X = df.select_dtypes(include=['number'])
    
    # Iniciar experimento no MLflow
    mlflow.set_experiment("IDS_CICIDS2017_Anomalia")
    
    print("Iniciando treinamento com MLflow...")
    with mlflow.start_run(run_name="IsolationForest_PortScan"):
        # Treinar modelo
        model = IsolationForest(contamination=contamination, random_state=42)
        model.fit(X)
        
        # Log de parâmetros e modelo
        mlflow.log_param("model_type", "IsolationForest")
        mlflow.log_param("contamination", contamination)
        
        # Log do modelo registrado como artefato
        mlflow.sklearn.log_model(model, "ids_model")
        
        print("Modelo treinado e registrado com sucesso no MLflow.")

if __name__ == "__main__":
    data_path = os.path.join(PROJECT_ROOT, "data", "ids", "cleaned_ids_data.csv")
    train_and_log_model(data_path)
