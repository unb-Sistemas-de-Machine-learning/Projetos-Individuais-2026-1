import os
import numpy as np
import pandas as pd
import mlflow
import dagshub
import torch

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from datasets import Dataset
from transformers import (
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

from model.cross_encoder import load_tokenizer_and_model, tokenize_nli_batch
from model.metrics import compute_metrics


def train_cross_encoder():
    dagshub.init(repo_owner='Ana-Luiza-SC', repo_name='contraditory', mlflow=True)
    mlflow.set_tracking_uri("https://dagshub.com/Ana-Luiza-SC/contraditory.mlflow")
    mlflow.set_experiment("contraditory")

    df = pd.read_csv("data/processed/train_en.csv")

    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["label"]
    )

    model_name = "cross-encoder/nli-deberta-v3-small"
    max_length = 128
    train_batch_size = 4
    eval_batch_size = 8
    learning_rate = 2e-5
    num_train_epochs = 3
    weight_decay = 0.01

    tokenizer, model = load_tokenizer_and_model(model_name)

    train_ds = Dataset.from_pandas(
        train_df[["premise", "hypothesis", "label"]],
        preserve_index=False
    )
    val_ds = Dataset.from_pandas(
        val_df[["premise", "hypothesis", "label"]],
        preserve_index=False
    )

    train_ds = train_ds.map(
        lambda batch: tokenize_nli_batch(batch, tokenizer, max_length=max_length),
        batched=True
    )
    val_ds = val_ds.map(
        lambda batch: tokenize_nli_batch(batch, tokenizer, max_length=max_length),
        batched=True
    )

    train_ds = train_ds.remove_columns(["premise", "hypothesis"])
    val_ds = val_ds.remove_columns(["premise", "hypothesis"])

    train_ds = train_ds.rename_column("label", "labels")
    val_ds = val_ds.rename_column("label", "labels")

    train_ds.set_format("torch")
    val_ds.set_format("torch")

    os.makedirs("models", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)

    args = TrainingArguments(
        output_dir="models/cross_encoder_en_small",
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        learning_rate=learning_rate,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        num_train_epochs=num_train_epochs,
        weight_decay=weight_decay,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        report_to="none",
        save_total_limit=1
    )

    with mlflow.start_run(run_name="CrossEncoder_English_DeBERTaSmall_v1"):
        mlflow.log_param("model_family", "CrossEncoder")
        mlflow.log_param("language_scope", "English only")
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("max_length", max_length)
        mlflow.log_param("train_batch_size", train_batch_size)
        mlflow.log_param("eval_batch_size", eval_batch_size)
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_param("num_train_epochs", num_train_epochs)
        mlflow.log_param("weight_decay", weight_decay)
        mlflow.log_param("split_random_state", 42)
        mlflow.log_param("train_samples", len(train_df))
        mlflow.log_param("val_samples", len(val_df))
        mlflow.log_param("device", "cuda" if torch.cuda.is_available() else "cpu")

        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=train_ds,
            eval_dataset=val_ds,
            processing_class=tokenizer,
            compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=1)]
        )

        print("Iniciando treino do cross-encoder...")
        trainer.train()

        print("Avaliando modelo...")
        eval_metrics = trainer.evaluate()

        for key, value in eval_metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, float(value))

        preds_output = trainer.predict(val_ds)
        y_pred = np.argmax(preds_output.predictions, axis=1)
        y_true = np.array(val_df["label"])

        cm = confusion_matrix(y_true, y_pred)
        np.savetxt("artifacts/confusion_matrix_cross_encoder_small.csv", cm, delimiter=",", fmt="%d")
        mlflow.log_artifact("artifacts/confusion_matrix_cross_encoder_small.csv")

        print("Métricas finais:")
        for key, value in eval_metrics.items():
            print(f"{key}: {value}")

        print("Matriz de confusão:")
        print(cm)
        trainer.save_model("models/best_model")
        
        # Registra essa pasta como um artefato no MLflow/DagsHub
        mlflow.log_artifacts("models/best_model", artifact_path="model_files")


if __name__ == "__main__":
    train_cross_encoder()