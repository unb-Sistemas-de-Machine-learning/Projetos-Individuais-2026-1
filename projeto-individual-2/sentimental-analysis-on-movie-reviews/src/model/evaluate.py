"""Inference and metric computation.

Pure functions that take a classifier (or its raw outputs) and produce
predictions and metrics. No logging, no side effects — the pipeline
orchestrator decides what to do with the results.
"""

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from src.model.loader import LABEL_MAP


def run_inference(classifier, texts: list[str], batch_size: int = 8) -> list[dict]:
    """Run the classifier over a list of texts. Returns raw HuggingFace result dicts."""
    return classifier(texts, batch_size=batch_size)


def extract_predictions(results: list[dict]) -> tuple[list[int], list[float]]:
    """Map HuggingFace results to (predicted integer labels, confidences)."""
    preds = [LABEL_MAP[r["label"]] for r in results]
    confs = [r["score"] for r in results]
    return preds, confs


def compute_metrics(
    true_labels: list[int], pred_labels: list[int]
) -> dict[str, float]:
    """Compute accuracy, precision, recall, and F1 for binary classification."""
    return {
        "accuracy": accuracy_score(true_labels, pred_labels),
        "precision": precision_score(true_labels, pred_labels, zero_division=0),
        "recall": recall_score(true_labels, pred_labels, zero_division=0),
        "f1": f1_score(true_labels, pred_labels, zero_division=0),
    }
