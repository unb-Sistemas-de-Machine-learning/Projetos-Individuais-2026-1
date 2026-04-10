import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import mlflow
import mlflow.pytorch
import os

# Caminho relativo a partir da raiz do repositório
DATA_PATH = os.path.join("ingrid-soares", "projeto-2", "data", "phishing", "phishing_data.csv")

def run_fine_tuning():
    """Realiza o fine-tuning do DistilBERT para classificação de URLs."""
    if not os.path.exists(DATA_PATH):
        print(f"Erro: Arquivo '{DATA_PATH}' não encontrado.")
        return

    print("Carregando e processando dados para fine-tuning...")
    df = pd.read_csv(DATA_PATH)
    # Renomear colunas para o esperado pelo dataset HuggingFace
    df = df.rename(columns={'url': 'text', 'label': 'labels'})
    dataset = Dataset.from_pandas(df)
    
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    
    print("Carregando DistilBERT...")
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
    
    mlflow.set_experiment("Phishing_FineTuning_NLP")
    
    print("Iniciando treinamento com MLflow...")
    with mlflow.start_run(run_name="DistilBERT_FineTuning"):
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=3,
            per_device_train_batch_size=4,
            logging_steps=1,
            report_to="mlflow"
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets,
        )
        
        trainer.train()
        
        # Log do modelo fine-tuned
        mlflow.pytorch.log_model(model, "fine_tuned_distilbert")
        print("Fine-tuning concluído e modelo registrado no MLflow.")

if __name__ == "__main__":
    run_fine_tuning()
