from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import mlflow
import mlflow.transformers
from transformers import pipeline

from src.model.load_model import load_model_and_tokenizer


MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
MLFLOW_EXPERIMENT_NAME = "phishing-email-mlflow"
REGISTERED_MODEL_NAME = "phishing-email-detector"


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    model, tokenizer = load_model_and_tokenizer()

    clf_pipeline = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer
    )

    input_example = [
        "Dear user, please verify your account immediately by clicking the secure link below."
    ]

    with mlflow.start_run(run_name="register-phishing-model") as run:
        mlflow.log_param("source_model_name", "ElSlay/BERT-Phishing-Email-Model")
        mlflow.log_param("registered_model_name", REGISTERED_MODEL_NAME)

        mlflow.transformers.log_model(
            transformers_model=clf_pipeline,
            name="model",
            input_example=input_example,
        )

        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(
        model_uri=model_uri,
        name=REGISTERED_MODEL_NAME
    )

    print("Modelo logado e enviado para registro com sucesso.")
    print(f"Run ID: {run_id}")
    print(f"Model URI: {model_uri}")
    print(f"Registered model: {REGISTERED_MODEL_NAME}")
    print(f"Version: {result.version}")


if __name__ == "__main__":
    main()