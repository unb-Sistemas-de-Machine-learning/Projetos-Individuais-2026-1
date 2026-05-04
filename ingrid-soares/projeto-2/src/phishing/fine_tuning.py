import pandas as pd
import torch
import numpy as np
import optuna
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import mlflow
import mlflow.pytorch
import os
import evaluate

# --- Configurações ---
DATA_DIR = os.path.join("ingrid-soares", "projeto-2", "data", "phishing")
CSV_PATH = os.path.join(DATA_DIR, "phishing_data.csv")
PARQUET_PATH = os.path.join(DATA_DIR, "phishing_data.parquet")

EPOCHS = int(os.getenv("TRAIN_EPOCHS", 3))
BATCH_SIZE = int(os.getenv("TRAIN_BATCH_SIZE", 8))

def load_data(csv_path, parquet_path):
    """Carrega dados em Parquet (preferencial) ou CSV."""
    if os.path.exists(parquet_path):
        print(f"Carregando Phishing via Parquet (otimizado): {parquet_path}")
        return pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        print(f"Carregando Phishing via CSV: {csv_path}")
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(f"Dados não encontrados em {csv_path} ou {parquet_path}")

def compute_metrics(eval_pred):
    metric = evaluate.load("accuracy")
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

def model_init():
    return DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)

def run_optuna_tuning():
    df = load_data(CSV_PATH, PARQUET_PATH).rename(columns={'url': 'text', 'label': 'labels'})
    dataset = Dataset.from_pandas(df).train_test_split(test_size=0.2)
    
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    tokenized_datasets = dataset.map(lambda x: tokenizer(x['text'], padding="max_length", truncation=True), batched=True)

    mlflow.set_experiment("Phishing_Optuna_Tuning")
    
    with mlflow.start_run(run_name="DistilBERT_Optuna_Search"):
        trainer = Trainer(
            model_init=model_init,
            args=TrainingArguments(
                output_dir="./results",
                evaluation_strategy="epoch",
                save_strategy="epoch",
                num_train_epochs=2,
                report_to="mlflow"
            ),
            train_dataset=tokenized_datasets['train'],
            eval_dataset=tokenized_datasets['test'],
            compute_metrics=compute_metrics,
        )

        print("Iniciando busca de hiperparâmetros com Optuna...")
        best_run = trainer.hyperparameter_search(
            direction="maximize",
            backend="optuna",
            hp_space=lambda trial: {
                "learning_rate": trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True),
                "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", [8, 16]),
            },
            n_trials=3
        )

        print(f"Melhores parâmetros encontrados: {best_run.hyperparameters}")
        mlflow.log_params(best_run.hyperparameters)
        mlflow.pytorch.log_model(trainer.model, "best_model_optuna")
        print("Modelo otimizado registrado com sucesso.")

if __name__ == "__main__":
    run_optuna_tuning()
