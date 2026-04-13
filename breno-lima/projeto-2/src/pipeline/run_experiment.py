import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import mlflow
import mlflow.pytorch
from mlflow import MlflowClient
from model.model_service import ModelService
from data.ingestion import ISICClient
from data.dataset import SkinCancerDataset

mlflow.set_tracking_uri("sqlite:///mlflow.db")

client = ISICClient()
client.download_batch(limit=10)

dataset = SkinCancerDataset()


MODELS = [
    "gianlab/swin-tiny-patch4-window7-224-finetuned-skin-cancer",
]

REGISTERED_MODEL_NAME = "SkinCancerClassifier"


def evaluate(model_service: ModelService, paths):
    results = []

    for step, image_path in enumerate(paths):
        result = model_service.predict(image_path)
        mlflow.log_metric("confidence_per_image", result["confidence"], step=step)
        results.append(result)

    return results


def run_experiment(model_name: str):
    mlflow.set_experiment("Skin Cancer Classification")
    model_service = ModelService(model_name)

    split_sizes = dataset.split_sizes()
    test_paths = dataset.get_split("test")

    with mlflow.start_run(run_name=model_name) as run:
        mlflow.set_tags({
            "model_source": "huggingface",
            "domain": "skin_cancer",
            "split": "test",
        })

        mlflow.log_param("model_name", model_name)
        mlflow.log_param("dataset_size", len(dataset))
        mlflow.log_param("train_size", split_sizes["train"])
        mlflow.log_param("val_size", split_sizes["val"])
        mlflow.log_param("test_size", split_sizes["test"])

        result = evaluate(model_service, test_paths)

        confidence_scores = [r["confidence"] for r in result]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        min_confidence = min(confidence_scores)
        max_confidence = max(confidence_scores)

        mlflow.log_metric("avg_confidence", avg_confidence)
        mlflow.log_metric("min_confidence", min_confidence)
        mlflow.log_metric("max_confidence", max_confidence)
        mlflow.log_metric("warnings_count", sum(1 for r in result if r["warnings"]))

        mlflow.log_dict({"predictions": result[:10]}, "sample_predictions.json")

        model_info = mlflow.pytorch.log_model(
            model_service.model,
            artifact_path="model",
            registered_model_name=REGISTERED_MODEL_NAME,
        )

        mlflow_client = MlflowClient()
        mlflow_client.set_registered_model_tag(
            REGISTERED_MODEL_NAME, "task", "image-classification"
        )

        print(f"[{model_name}] Test size: {len(test_paths)} | Avg Confidence: {avg_confidence:.4f}")
        print(f"Model registered as '{REGISTERED_MODEL_NAME}' — URI: {model_info.model_uri}")


if __name__ == "__main__":
    for model in MODELS:
        run_experiment(model)
