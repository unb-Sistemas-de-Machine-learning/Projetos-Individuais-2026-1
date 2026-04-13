import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import mlflow
import mlflow.pytorch
from model.model_service import ModelService
from data.ingestion import ISICClient
from data.dataset import SkinCancerDataset

client = ISICClient()
client.download_batch(limit=10)

dataset = SkinCancerDataset()


MODELS = [
    "gianlab/swin-tiny-patch4-window7-224-finetuned-skin-cancer",
]


def evaluate(model_service: ModelService, dataset):
    results = []

    for image_path in dataset:
        result = model_service.predict(image_path)
        results.append(result)

    return results


def run_experiment(model_name: str):
    mlflow.set_experiment("Skin Cancer Classification")
    model_service = ModelService(model_name)

    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("dataset_size", len(dataset))

        result = evaluate(model_service, dataset)

        confidence_scores = [r["confidence"] for r in result]

        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        mlflow.log_metric("confidence", avg_confidence)

        mlflow.log_dict(
            {
                "predictions": result[:10],
            },
            "sample_predictions.json",
        )

        mlflow.pytorch.log_model(
            model_service.model,
            artifact_path="model",
        )

        print(f"[{model_name}] Average Confidence: {avg_confidence:.4f}")


if __name__ == "__main__":
    for model in MODELS:
        run_experiment(model)
