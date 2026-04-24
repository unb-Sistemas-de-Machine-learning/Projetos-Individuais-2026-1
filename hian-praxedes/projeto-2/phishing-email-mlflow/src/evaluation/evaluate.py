from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


REPORTS_DIR = Path("reports")
PREDICTIONS_PATH = REPORTS_DIR / "test_predictions.csv"

OUTPUT_REPORT = REPORTS_DIR / "classification_report.json"
OUTPUT_ERRORS = REPORTS_DIR / "error_examples.csv"
OUTPUT_CONFUSION = REPORTS_DIR / "confusion_matrix.png"


LABEL_TO_ID = {
    "legitimate": 0,
    "phishing": 1,
}


def main():
    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {PREDICTIONS_PATH}")

    df = pd.read_csv(PREDICTIONS_PATH)

    required_columns = {
        "text",
        "true_label",
        "pred_label",
        "confidence",
        "guardrail_status",
        "guardrail_reason",
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"O arquivo {PREDICTIONS_PATH} precisa ter as colunas {required_columns}. "
            f"Faltando: {missing}"
        )

    total_rows = len(df)
    accepted_df = df[df["guardrail_status"] == "accepted"].copy()
    rejected_df = df[df["guardrail_status"] == "rejected"].copy()
    abstain_df = df[df["guardrail_status"] == "abstain"].copy()

    accepted_count = len(accepted_df)
    rejected_count = len(rejected_df)
    abstain_count = len(abstain_df)

    report = {
        "total_rows": int(total_rows),
        "accepted_count": int(accepted_count),
        "rejected_count": int(rejected_count),
        "abstain_count": int(abstain_count),
        "accept_rate": accepted_count / total_rows if total_rows else 0,
        "rejection_rate": rejected_count / total_rows if total_rows else 0,
        "abstain_rate": abstain_count / total_rows if total_rows else 0,
    }

    # Se nao houver exemplos aceitos, nao da para calcular metricas de classificacao
    if accepted_count == 0:
        report.update(
            {
                "accuracy": None,
                "precision": None,
                "recall": None,
                "f1": None,
                "message": "Nao ha exemplos aceitos para calcular metricas."
            }
        )

        with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # cria arquivo vazio de erros
        accepted_df.to_csv(OUTPUT_ERRORS, index=False, encoding="utf-8")

        print("Nao ha exemplos aceitos para calcular metricas.")
        print(f"Relatorio salvo em: {OUTPUT_REPORT}")
        return

    # Converte labels previstos em numero
    accepted_df["pred_label_id"] = accepted_df["pred_label"].map(LABEL_TO_ID)

    if accepted_df["pred_label_id"].isnull().any():
        invalid_labels = accepted_df[accepted_df["pred_label_id"].isnull()]["pred_label"].unique()
        raise ValueError(
            f"Foram encontradas labels previstas invalidas: {invalid_labels}. "
            f"Esperado: {list(LABEL_TO_ID.keys())}"
        )

    y_true = accepted_df["true_label"].astype(int)
    y_pred = accepted_df["pred_label_id"].astype(int)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    report.update(
        {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
        }
    )

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # erros: somente exemplos aceitos em que o modelo errou
    errors_df = accepted_df[accepted_df["true_label"] != accepted_df["pred_label_id"]].copy()
    errors_df.to_csv(OUTPUT_ERRORS, index=False, encoding="utf-8")

    # matriz de confusao
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Confusion Matrix")
    plt.colorbar()

    tick_labels = ["legitimate", "phishing"]
    plt.xticks([0, 1], tick_labels)
    plt.yticks([0, 1], tick_labels)

    plt.xlabel("Predicted label")
    plt.ylabel("True label")

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(OUTPUT_CONFUSION, dpi=150)
    plt.close()

    print("Avaliacao concluida.")
    print(f"Relatorio salvo em: {OUTPUT_REPORT}")
    print(f"Erros salvos em: {OUTPUT_ERRORS}")
    print(f"Matriz de confusao salva em: {OUTPUT_CONFUSION}")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()