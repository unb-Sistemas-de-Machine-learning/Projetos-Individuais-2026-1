from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

import config


def compute_classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, pos_label="positive", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, pos_label="positive", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, pos_label="positive", zero_division=0)),
    }


def save_confusion_matrix(y_true: List[str], y_pred: List[str], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=["negative", "positive"])

    fig, ax = plt.subplots(figsize=(5, 5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["negative", "positive"],
    )
    disp.plot(ax=ax, cmap="Blues", values_format="d")
    ax.set_title("Matriz de confusao - conjunto de teste")

    output_path = output_dir / "confusion_matrix.png"
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    return output_path


def save_prediction_report(
    texts: List[str],
    y_true: List[str],
    predictions: List[Dict[str, float]],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for text, label_real, pred in zip(texts, y_true, predictions):
        rows.append(
            {
                config.TEXT_COLUMN: text,
                "label_real": label_real,
                "label_predito": pred["label"],
                "confianca": round(pred["score"], 4),
                "acertou": label_real == pred["label"],
            }
        )

    output_path = output_dir / "predicoes_teste.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False)
    return output_path
