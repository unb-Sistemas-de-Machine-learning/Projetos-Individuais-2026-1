import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def evaluate_predictions(y_true, spam_proba, threshold):
    y_pred = [1 if score >= threshold else 0 for score in spam_proba]

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }

    if len(set(y_true)) > 1:
        metrics["roc_auc"] = roc_auc_score(y_true, spam_proba)
    else:
        metrics["roc_auc"] = 0.0

    return metrics
