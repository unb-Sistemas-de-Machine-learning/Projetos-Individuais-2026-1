# src/phishing/inference.py

import mlflow
import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from pydantic import BaseModel, Field, validator, ValidationError
import os

# --- Configurações ---
# Nome do artefato registrado no MLflow para o modelo fine-tuned
MODEL_ARTIFACT_NAME = "fine_tuned_distilbert" 
# Experimento onde o fine-tuning foi registrado
EXPERIMENT_NAME = "Phishing_FineTuning_NLP"

# Definição do modelo de entrada para validação de URL
class URLInput(BaseModel):
    url: str

    @validator('url')
    def validate_url_format(cls, value):
        # Validação básica para garantir que parece uma URL válida
        # Pode ser aprimorada com regex mais robustos ou bibliotecas dedicadas
        if not (value.startswith('http://') or value.startswith('https://')):
            raise ValueError('A URL deve começar com http:// ou https://')
        # Adicionar mais validações se necessário (ex: domínio, TLD)
        return value

# --- Funções de Carregamento e Inferência ---

def load_model_and_tokenizer(model_artifact_path=MODEL_ARTIFACT_NAME, experiment_name=EXPERIMENT_NAME, tracking_uri=None):
    """
    Carrega o tokenizer e o modelo fine-tuned do MLflow.
    Busca o último run no experimento especificado.
    """
    print("Carregando tokenizer...")
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

    # Define o tracking URI se fornecido, caso contrário usa o padrão
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    print(f"Buscando último run no experimento: '{experiment_name}'...")
    try:
        # Encontra o último run para o experimento especificado
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if not experiment:
            raise Exception(f"Experimento '{experiment_name}' não encontrado.")
            
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=1
        )
        
        if runs.empty:
            raise Exception(f"Nenhum run encontrado para o experimento '{experiment_name}'. Certifique-se de que o fine-tuning foi executado.")
            
        latest_run_id = runs.iloc[0].run_id
        print(f"Último run ID encontrado: {latest_run_id}")
        
        model_uri = f"runs:/{latest_run_id}/{model_artifact_path}"
        
    except Exception as e:
        print(f"Erro ao buscar run ou modelo no MLflow: {e}")
        raise

    print(f"Carregando modelo do MLflow URI: {model_uri}")
    # Carrega o modelo PyTorch usando o mlflow.pytorch flavor
    model = mlflow.pytorch.load_model(model_uri)
    model.eval() # Coloca o modelo em modo de avaliação

    print("Modelo e Tokenizer carregados com sucesso.")
    return tokenizer, model

def predict_url(url: str, tokenizer, model, device='cpu'):
    """
    Realiza a predição de uma URL usando o modelo carregado.
    Inclui validação de Guardrail e retorna predição e confiança.
    """
    try:
        # Validação de Guardrail via Pydantic
        validated_input = URLInput(url=url)
        safe_url = validated_input.url # A URL validada
    except ValidationError as e:
        print(f"Erro de validação de URL: {e.errors()}")
        return {"url": url, "prediction": "invalid_input", "confidence": 0.0, "error": str(e.errors())}

    print(f"Processando URL validada: {safe_url}")

    # Tokenização da URL
    # max_length=512 é um valor comum para modelos baseados em BERT/DistilBERT
    inputs = tokenizer(safe_url, return_tensors="pt", padding="max_length", truncation=True, max_length=512)

    # Mover tensores para o dispositivo correto (CPU ou GPU se disponível)
    inputs = {key: val.to(device) for key, val in inputs.items()}
    model.to(device)

    # Realizar predição
    with torch.no_grad(): # Desabilita o cálculo de gradientes para inferência
        outputs = model(**inputs)
        logits = outputs.logits
        # Calcula as probabilidades usando softmax
        probabilities = torch.softmax(logits, dim=-1)
        
        # Assumindo que a classe 1 é Phishing e a classe 0 é Legítimo
        # O modelo foi treinado com num_labels=2 no fine_tuning.py
        prediction_class = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][prediction_class].item() # Confiança na classe predita

        prediction_label = "phishing" if prediction_class == 1 else "legitimo"

    return {
        "url": safe_url,
        "prediction": prediction_label,
        "confidence": confidence,
        "raw_probabilities": probabilities.tolist()[0] # Retorna as probabilidades brutas para ambas as classes
    }

# --- Execução Principal (para teste local) ---
if __name__ == "__main__":
    # Este bloco permite testar o script localmente executando:
    # python src/phishing/inference.py
    
    print("--- Iniciando teste local do módulo de inferência de Phishing ---")
    
    try:
        # Tenta carregar o modelo e tokenizer
        # Use TRACKING_URI=http://localhost:5000 se o MLflow estiver rodando em um servidor separado
        # ou apenas deixe None para usar o padrão (geralmente baseado em arquivos locais)
        tokenizer, model = load_model_and_tokenizer()

        # Teste com uma URL legítima conhecida
        print("
--- Testando URL Legítima ---")
        legit_url = "https://www.google.com"
        result_legit = predict_url(legit_url, tokenizer, model)
        print(f"Resultado para '{legit_url}': {result_legit}")

        # Teste com uma URL de phishing conhecida (exemplo)
        print("
--- Testando URL de Phishing ---")
        phishing_url = "http://this-is-a-fake-bank-login.com/login.php?user=admin"
        result_phishing = predict_url(phishing_url, tokenizer, model)
        print(f"Resultado para '{phishing_url}': {result_phishing}")

        # Teste com uma URL inválida para o guardrail de validação
        print("
--- Testando URL Inválida (Guardrail) ---")
        invalid_url = "www.google.com" # Falta o schema http/https
        result_invalid = predict_url(invalid_url, tokenizer, model)
        print(f"Resultado para '{invalid_url}': {result_invalid}")
        
        # Teste com outra URL legítima
        print("
--- Testando outra URL Legítima ---")
        another_legit_url = "https://github.com/ingrid-soares/projeto-2"
        result_another_legit = predict_url(another_legit_url, tokenizer, model)
        print(f"Resultado para '{another_legit_url}': {result_another_legit}")

    except Exception as e:
        print(f"
Ocorreu um erro durante a execução do teste local: {e}")
        print("Por favor, verifique:")
        print("1. Se você executou o fine-tuning (`python src/phishing/fine_tuning.py`) recentemente para que o modelo seja registrado no MLflow.")
        print("2. Se o nome do experimento ('Phishing_FineTuning_NLP') e o nome do artefato ('fine_tuned_distilbert') estão corretos.")
        print("3. Se o MLflow está acessível (se estiver usando um servidor remoto).")
        print("4. Se há GPUs disponíveis e configuradas se você espera usar CUDA.")
