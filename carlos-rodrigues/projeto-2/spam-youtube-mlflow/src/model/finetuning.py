import logging
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

logger = logging.getLogger(__name__)


class SpamDataset(Dataset):

    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


class FinetuneSpamModel:

    def __init__(self, model_name, output_dir="./finetuned_model"):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

        logger.info(f"Modelo carregado: {model_name}")

    def prepare_datasets(
        self, train_texts, train_labels, val_texts, val_labels
    ):
        train_dataset = SpamDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = SpamDataset(val_texts, val_labels, self.tokenizer)

        logger.info(f"Train dataset size: {len(train_dataset)}")
        logger.info(f"Validation dataset size: {len(val_dataset)}")

        return train_dataset, val_dataset

    def train(
        self,
        train_texts,
        train_labels,
        val_texts,
        val_labels,
        num_epochs=3,
        batch_size=16,
        learning_rate=2e-5,
    ):
        train_dataset, val_dataset = self.prepare_datasets(train_texts, train_labels, val_texts, val_labels)

        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=50,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            learning_rate=learning_rate,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        logger.info("Iniciando fine-tuning...")
        train_result = trainer.train()

        logger.info(f"Fine-tuning concluído. Loss final: {train_result.training_loss:.4f}")

        eval_result = trainer.evaluate()
        logger.info(f"Métricas de validação: {eval_result}")

        self.model.save_pretrained(str(self.output_dir))
        self.tokenizer.save_pretrained(str(self.output_dir))
        logger.info(f"Modelo salvo em: {self.output_dir}")

        return {
            "training_loss": train_result.training_loss,
            "eval_loss": eval_result.get("eval_loss", None),
            "model_path": str(self.output_dir),
        }

    def evaluate_on_data(self, texts, labels):
        dataset = SpamDataset(texts, labels, self.tokenizer)
        loader = DataLoader(dataset, batch_size=16)

        self.model.eval()
        predictions = []
        true_labels = []

        with torch.no_grad():
            for batch in loader:
                input_ids = batch["input_ids"].to(self.model.device)
                attention_mask = batch["attention_mask"].to(self.model.device)
                labels = batch["labels"].to(self.model.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits

                preds = torch.argmax(logits, dim=1)
                predictions.extend(preds.cpu().numpy().tolist())
                true_labels.extend(labels.cpu().numpy().tolist())

        predictions = np.array(predictions)
        true_labels = np.array(true_labels)

        accuracy = (predictions == true_labels).mean()
        logger.info(f"Acurácia no conjunto: {accuracy:.4f}")

        return {
            "accuracy": float(accuracy),
            "predictions": predictions.tolist(),
            "true_labels": true_labels.tolist(),
        }
