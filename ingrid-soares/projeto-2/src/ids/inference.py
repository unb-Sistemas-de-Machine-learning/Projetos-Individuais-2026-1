import mlflow
import mlflow.sklearn
import pandas as pd
import os

# Define a pasta raiz do projeto de forma dinâmica
PROJECT_ROOT = os.path.join("ingrid-soares", "projeto-2")

def predict_traffic(test_data_path, model_uri="models:/ids_model/latest"):
    """
    Carrega o modelo do MLflow e faz a inferência no tráfego de rede.
    """
    print(f"Carregando modelo de: {model_uri}")
    try:
        model = mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}. Certifique-se que o modelo foi registrado.")
        return None

    df = pd.read_csv(test_data_path)
    X = df.select_dtypes(include=['number'])
    
    # IsolationForest: 1 para normal, -1 para anomalia
    df['is_anomaly'] = model.predict(X)
    
    return df

if __name__ == "__main__":
    # Caminho do teste dentro da estrutura correta
    test_path = os.path.join(PROJECT_ROOT, "data", "ids", "test_data.csv")
    
    if os.path.exists(test_path):
        results = predict_traffic(test_path)
        if results is not None:
            output_path = os.path.join(PROJECT_ROOT, "data", "ids", "predictions.csv")
            results.to_csv(output_path, index=False)
            print(f"Inferência concluída e salva em {output_path}")
    else:
        print(f"Arquivo de teste {test_path} não encontrado.")
