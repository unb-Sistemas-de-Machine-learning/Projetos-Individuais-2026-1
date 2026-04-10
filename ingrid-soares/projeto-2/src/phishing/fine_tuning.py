import pandas as pd
import torch
import numpy as np
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import mlflow
import mlflow.pytorch
import os
import evaluate

# --- Configurações Dinâmicas ---
DATA_PATH = os.path.join("ingrid-soares", "projeto-2", "data", "phishing", "phishing_data.csv")
EPOCHS = int(os.getenv("TRAIN_EPOCHS", 3))
BATCH_SIZE = int(os.getenv("TRAIN_BATCH_SIZE", 8))

def compute_metrics(eval_pred):
    metric = evaluate.load("accuracy")
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

def run_fine_tuning():
    if not os.path.exists(DATA_PATH):
        print(f"Erro: Arquivo '{DATA_PATH}' não encontrado.")
        return

    print(f"Carregando dados (Epochs: {EPOCHS}, Batch Size: {BATCH_SIZE})...")
    df = pd.read_csv(DATA_PATH).rename(columns={'url': 'text', 'label': 'labels'})
    dataset = Dataset.from_pandas(df)
    
    # 1. Split Treino/Validação
    dataset = dataset.train_test_split(test_size=0.2)
    
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    tokenized_datasets = dataset.map(lambda x: tokenizer(x['text'], padding="max_length", truncation=True), batched=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Utilizando dispositivo: {device}")
    
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2).to(device)
    
    mlflow.set_experiment("Phishing_FineTuning_NLP")
    
    with mlflow.start_run(run_name=f"DistilBERT_E{EPOCHS}_B{BATCH_SIZE}"):
        training_args = TrainingArguments(
            output_dir="./results",
            evaluation_strategy="epoch", # Avalia a cada época
            save_strategy="epoch",
            num_train_epochs=EPOCHS,
            per_device_train_batch_size=BATCH_SIZE,
            report_to="mlflow"
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets['train'],
            eval_dataset=tokenized_datasets['test'],
            compute_metrics=compute_metrics,
        )
        
        trainer.train()
        
        # Log final do modelo
        mlflow.pytorch.log_model(model, "fine_tuned_distilbert")
        print("Fine-tuning profissional concluído.")

if __name__ == "__main__":
    run_fine_tuning()
