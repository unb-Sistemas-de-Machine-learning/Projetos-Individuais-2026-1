import argparse
from typing import Any, Dict

import mlflow
import mlflow.transformers
from mlflow.tracking import MlflowClient

import config
from guardrails import validate_inference_text, validate_prediction_confidence
from model_pipeline import normalize_prediction_label


def resolve_model_uri() -> str:
    client = MlflowClient(tracking_uri=config.TRACKING_URI)

    try:
        versions = client.search_model_versions(
            f"name='{config.REGISTERED_MODEL_NAME}'"
        )
        if versions:
            latest_version = max(versions, key=lambda v: int(v.version))
            return f"models:/{config.REGISTERED_MODEL_NAME}/{latest_version.version}"
    except Exception:
        pass

    experiments = client.search_experiments(
        filter_string=f"name = '{config.EXPERIMENT_NAME}'"
    )
    if not experiments:
        raise RuntimeError(
            "Experimento nao encontrado. Execute primeiro: python src/main.py"
        )

    latest_runs = client.search_runs(
        experiment_ids=[experiments[0].experiment_id],
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )
    if not latest_runs:
        raise RuntimeError(
            "Nenhum run encontrado. Execute primeiro: python src/main.py"
        )

    return f"runs:/{latest_runs[0].info.run_id}/model"


def predict_text(text: str) -> Dict[str, Any]:
    is_valid, reason = validate_inference_text(text)
    if not is_valid:
        return {"status": "rejected", "reason": reason}

    mlflow.set_tracking_uri(config.TRACKING_URI)
    model_uri = resolve_model_uri()
    classifier = mlflow.transformers.load_model(model_uri)

    raw_prediction = classifier(text, truncation=True)[0]
    label = normalize_prediction_label(raw_prediction["label"])
    confidence = float(raw_prediction["score"])

    is_safe, safe_reason = validate_prediction_confidence(confidence)
    if not is_safe:
        return {
            "status": "abstain",
            "reason": safe_reason,
            "prediction": label,
            "confidence": round(confidence, 4),
            "model_uri": model_uri,
        }

    return {
        "status": "ok",
        "prediction": label,
        "confidence": round(confidence, 4),
        "model_uri": model_uri,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inferencia local com modelo do MLflow")
    parser.add_argument(
        "--text",
        required=True,
        help="Texto para classificacao de sentimento",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = predict_text(args.text)

    print("Resultado da inferencia:")
    for key, value in result.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
