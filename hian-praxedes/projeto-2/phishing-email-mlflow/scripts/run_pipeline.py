from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import json
import time
import subprocess

import mlflow
import pandas as pd

from src.model.load_model import load_model_and_tokenizer
from src.model.predict import predict_text
from src.serving.guardrails import apply_guardrails


TEST_PATH = Path("data/processed/test.csv")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PREDICTIONS = REPORTS_DIR / "test_predictions.csv"
OUTPUT_SUMMARY = REPORTS_DIR / "monitoring_summary.json"
CLASSIFICATION_REPORT = REPORTS_DIR / "classification_report.json"
ERROR_EXAMPLES = REPORTS_DIR / "error_examples.csv"
CONFUSION_MATRIX = REPORTS_DIR / "confusion_matrix.png"

DATA_VALIDATION_REPORT = REPORTS_DIR / "data_validation.json"
MANIFEST_PATH = Path("data/raw/manifest.json")

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
MLFLOW_EXPERIMENT_NAME = "phishing-email-mlflow"


def run_batch_inference():
    if not TEST_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {TEST_PATH}")

    df = pd.read_csv(TEST_PATH)

    required_columns = {"text", "label"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"O arquivo {TEST_PATH} precisa ter as colunas {required_columns}. "
            f"Faltando: {missing}"
        )

    model, tokenizer = load_model_and_tokenizer()

    results = []
    latencies_ms = []

    total_rows = len(df)
    print(f"Iniciando inferencia em lote para {total_rows} exemplos...")

    for idx, row in df.iterrows():
        text = row["text"]
        true_label = row["label"]

        # Guardrail antes da predicao
        pre_guardrail = apply_guardrails(text)

        if pre_guardrail["status"] == "rejected":
            results.append(
                {
                    "text": text,
                    "true_label": true_label,
                    "pred_label": None,
                    "confidence": None,
                    "guardrail_status": pre_guardrail["status"],
                    "guardrail_reason": pre_guardrail["reason"],
                }
            )
            continue

        # Predicao
        start = time.perf_counter()
        prediction = predict_text(text, model, tokenizer)
        end = time.perf_counter()

        latency_ms = (end - start) * 1000
        latencies_ms.append(latency_ms)

        # Guardrail depois da predicao
        post_guardrail = apply_guardrails(text, prediction=prediction)

        results.append(
            {
                "text": text,
                "true_label": true_label,
                "pred_label": prediction["label"],
                "confidence": prediction["confidence"],
                "guardrail_status": post_guardrail["status"],
                "guardrail_reason": post_guardrail["reason"],
            }
        )

        if (idx + 1) % 100 == 0 or (idx + 1) == total_rows:
            print(f"Processados: {idx + 1}/{total_rows}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PREDICTIONS, index=False, encoding="utf-8")

    accepted_count = int((results_df["guardrail_status"] == "accepted").sum())
    rejected_count = int((results_df["guardrail_status"] == "rejected").sum())
    abstain_count = int((results_df["guardrail_status"] == "abstain").sum())

    summary = {
        "total_rows": int(total_rows),
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "abstain_count": abstain_count,
        "accept_rate": accepted_count / total_rows if total_rows else 0,
        "rejection_rate": rejected_count / total_rows if total_rows else 0,
        "abstain_rate": abstain_count / total_rows if total_rows else 0,
        "avg_latency_ms": sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0,
    }

    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\nInferencia finalizada.")
    print(f"Predicoes salvas em: {OUTPUT_PREDICTIONS}")
    print(f"Resumo salvo em: {OUTPUT_SUMMARY}")

    return summary


def run_evaluation():
    print("Executando avaliacao...")
    subprocess.run(
        [sys.executable, "-m", "src.evaluation.evaluate"],
        check=True,
    )


def load_metrics_for_mlflow():
    metrics = {}

    if OUTPUT_SUMMARY.exists():
        with open(OUTPUT_SUMMARY, "r", encoding="utf-8") as f:
            summary = json.load(f)
        for key in [
            "accept_rate",
            "rejection_rate",
            "abstain_rate",
            "avg_latency_ms",
        ]:
            if key in summary and summary[key] is not None:
                metrics[key] = float(summary[key])

    if CLASSIFICATION_REPORT.exists():
        with open(CLASSIFICATION_REPORT, "r", encoding="utf-8") as f:
            report = json.load(f)
        for key in [
            "accuracy",
            "precision",
            "recall",
            "f1",
            "accept_rate",
            "rejection_rate",
            "abstain_rate",
        ]:
            if key in report and report[key] is not None:
                metrics[key] = float(report[key])

    return metrics


def log_artifacts_if_exist():
    artifact_paths = [
        MANIFEST_PATH,
        DATA_VALIDATION_REPORT,
        OUTPUT_PREDICTIONS,
        OUTPUT_SUMMARY,
        CLASSIFICATION_REPORT,
        ERROR_EXAMPLES,
        CONFUSION_MATRIX,
    ]

    for path in artifact_paths:
        if path.exists():
            mlflow.log_artifact(str(path))


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    threshold = 0.70
    max_length = 512
    random_state = 42

    with mlflow.start_run():
        # params
        mlflow.log_params(
            {
                "model_name": "ElSlay/BERT-Phishing-Email-Model",
                "dataset_name": "zefang-liu/phishing-email-dataset",
                "confidence_threshold": threshold,
                "max_length": max_length,
                "random_state": random_state,
                "test_path": str(TEST_PATH),
            }
        )

        # tags
        mlflow.set_tags(
            {
                "project": "phishing-email-mlflow",
                "task": "phishing-email-classification",
                "framework": "transformers",
            }
        )

        # batch inference
        summary = run_batch_inference()

        # evaluation
        run_evaluation()

        # metrics
        metrics = load_metrics_for_mlflow()
        if metrics:
            mlflow.log_metrics(metrics)

        # artifacts
        log_artifacts_if_exist()

        print("\nRun registrada no MLflow com sucesso.")
        print("Resumo de inferencia:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print("Metricas logadas:")
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()