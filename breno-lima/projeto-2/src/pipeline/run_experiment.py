import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import mlflow
import mlflow.pytorch
from model.model_service import ModelService

MODELS = [
    "gianlab/swin-tiny-patch4-window7-224-finetuned-skin-cancer",
]


def run_experiment(model_name: str):
    mlflow.set_experiment("Skin Cancer Classification")

    with mlflow.start_run():
        mlflow.log_param("model_name", model_name)

        model_service = ModelService(model_name)
        image_url = "https://huggingface.co/gianlab/swin-tiny-patch4-window7-224-finetuned-skin-cancer/resolve/main/skin.png"

        result = model_service.predict(image_url)

        mlflow.log_metric("confidence", result["confidence"])

        mlflow.log_dict(result, "prediction_result.json")

        mlflow.pytorch.log_model(
            model_service.model,
            artifact_path="model",
        )

        print("Result:", result)


if __name__ == "__main__":
    for model in MODELS:
        run_experiment(model)
