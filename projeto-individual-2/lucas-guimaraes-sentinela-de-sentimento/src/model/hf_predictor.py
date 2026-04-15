"""Carregamento do modelo pré-treinado (Hugging Face) e avaliação."""

from __future__ import annotations

from typing import Any

import numpy as np
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from transformers import pipeline


def build_pipeline(model_id: str, task: str = "text-classification") -> Any:
    """
    Integra o modelo pré-treinado via `transformers.pipeline` (sem treino do zero).

    `device` é escolhido automaticamente (CUDA se disponível).
    """
    return pipeline(task, model=model_id, tokenizer=model_id)


def evaluate_on_split(
    clf: Any,
    split: Dataset,
    text_column: str,
    label_column: str,
    batch_size: int = 16,
) -> dict[str, float]:
    """
    Avaliação apenas (inferência em lote). Labels SST-2: 0 negativo, 1 positivo.
    """
    texts = [str(t) for t in split[text_column]]
    y_true = np.array(split[label_column])
    preds: list[int] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        out = clf(batch)
        if not isinstance(out, list):
            out = [out]
        preds.extend(_labels_from_outputs(out))

    y_pred = np.array(preds[: len(y_true)])
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro")),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def _labels_from_outputs(outputs: list[Any]) -> list[int]:
    """Converte saída do pipeline em ids 0/1 compatíveis com SST-2."""
    labels: list[int] = []
    for o in outputs:
        lab = o.get("label", "")
        s = str(lab).upper()
        if "LABEL_0" in s or s == "NEGATIVE" or s.endswith("_0"):
            labels.append(0)
        elif "LABEL_1" in s or s == "POSITIVE" or s.endswith("_1"):
            labels.append(1)
        elif "NEG" in s:
            labels.append(0)
        elif "POS" in s:
            labels.append(1)
        else:
            labels.append(0)
    return labels
