import pandas as pd
import mlflow
import mlflow.pytorch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import os

# Caminho relativo simples a partir da pasta ingrid-soares/projeto-2/
DATA_PATH = os.path.join("data", "phishing", "phishing_data.csv")

def train_phishing_model(data_path):
    """
    Treina/Carrega um modelo DistilBERT para detecção de Phishing.
    """
    if not os.path.exists(data_path):
        print(f"Erro: Arquivo '{data_path}' não encontrado.")
        return

    print(f"Carregando dados de: {data_path}")
    df = pd.read_csv(data_path)
    
    # Carregar modelo pré-treinado (DistilBERT)
    print("Carregando DistilBERT...")
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
    
    # Iniciar experimento no MLflow
    mlflow.set_experiment("Phishing_Detection_NLP")
    
    print("Iniciando registro no MLflow...")
    with mlflow.start_run(run_name="DistilBERT_FineTuning"):
        mlflow.log_param("model_type", "DistilBERT")
        mlflow.log_param("num_labels", 2)
        
        # Log do modelo
        mlflow.pytorch.log_model(model, "phishing_model")
        print("Modelo DistilBERT registrado no MLflow.")

if __name__ == "__main__":
    train_phishing_model(DATA_PATH)
