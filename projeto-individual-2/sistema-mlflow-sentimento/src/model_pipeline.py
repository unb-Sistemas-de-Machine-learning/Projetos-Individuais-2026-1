from typing import Dict, List

from transformers import pipeline

import config


def load_classifier(model_name: str = config.MODEL_NAME):
    return pipeline(
        task=config.TASK_NAME,
        model=model_name,
        tokenizer=model_name,
        truncation=True,
    )


def normalize_prediction_label(raw_label: str) -> str:
    label = raw_label.strip().upper()
    mapping = {
        "POSITIVE": "positive",
        "NEGATIVE": "negative",
        "LABEL_1": "positive",
        "LABEL_0": "negative",
    }
    if label not in mapping:
        raise ValueError(f"Label inesperado retornado pelo modelo: {raw_label}")
    return mapping[label]


def predict_batch(
    classifier,
    texts: List[str],
    batch_size: int = config.BATCH_SIZE,
) -> List[Dict[str, float]]:
    raw_predictions = classifier(texts, truncation=True, batch_size=batch_size)
    normalized_predictions: List[Dict[str, float]] = []

    for item in raw_predictions:
        normalized_predictions.append(
            {
                "label": normalize_prediction_label(item["label"]),
                "score": float(item["score"]),
            }
        )

    return normalized_predictions
