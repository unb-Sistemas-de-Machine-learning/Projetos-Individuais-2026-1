# src/ids/inference.py

import mlflow
import pandas as pd
import numpy as np
import os

# --- Configurações ---
MODEL_NAME = "ids_model"

# --- Funções de Inferência ---

def load_ids_model(model_name=MODEL_NAME):
    """Carrega a versão mais recente do modelo IDS via MLflow Registry."""
    print(f"Carregando modelo '{model_name}' via MLflow...")
    # Usando o Model Registry (forma mais robusta)
    model_uri = f"models:/{model_name}/latest"
    try:
        return mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        print(f"Erro ao carregar modelo do Registry: {e}. Tente treinar e registrar o modelo primeiro.")
        raise

def predict_traffic(df, model):
    """
    Realiza a inferência em um DataFrame de tráfego de rede.
    """
    # Guardrail: Seleciona apenas colunas numéricas
    X = df.select_dtypes(include=[np.number])
    
    # Tratamento preventivo de valores nulos
    if X.isnull().values.any():
        print("Aviso: Dados de entrada contêm valores nulos. Preenchendo com 0.")
        X = X.fillna(0)

    # Inferência: IsolationForest retorna -1 para anomalia, 1 para normal
    predictions = model.predict(X)
    df['anomaly_label'] = ['anomaly' if p == -1 else 'normal' for p in predictions]
    
    return df

if __name__ == "__main__":
    # Caminho do teste
    test_path = "data/ids/test_data.csv"
    
    if os.path.exists(test_path):
        model = load_ids_model()
        df = pd.read_csv(test_path)
        
        results = predict_traffic(df, model)
        
        output_path = "data/ids/predictions.csv"
        results.to_csv(output_path, index=False)
        print(f"Inferência concluída. {len(results)} registros processados. Resultados em: {output_path}")
    else:
        print(f"Arquivo de teste '{test_path}' não encontrado.")
