from pprint import pformat
from typing import Optional

import mlflow
import mlflow.transformers

import config
from data_pipeline import load_dataset, split_dataset
from evaluation import (
    compute_classification_metrics,
    save_confusion_matrix,
    save_prediction_report,
)
from model_pipeline import load_classifier, predict_batch


def ensure_directories() -> None:
    config.MLRUNS_DIR.mkdir(parents=True, exist_ok=True)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def try_register_model(model_uri: str) -> Optional[str]:
    try:
        result = mlflow.register_model(
            model_uri=model_uri,
            name=config.REGISTERED_MODEL_NAME,
        )
        return str(result.version)
    except Exception as exc:
        print(f"[WARN] Nao foi possivel registrar o modelo: {exc}")
        return None


def main() -> None:
    ensure_directories()

    mlflow.set_tracking_uri(config.TRACKING_URI)
    mlflow.set_experiment(config.EXPERIMENT_NAME)

    df = load_dataset()
    train_df, test_df = split_dataset(df)

    classifier = load_classifier()

    with mlflow.start_run(run_name="distilbert_baseline") as run:
        mlflow.log_params(
            {
                "dataset_file": config.DATASET_FILE.name,
                "model_name": config.MODEL_NAME,
                "test_size": config.TEST_SIZE,
                "batch_size": config.BATCH_SIZE,
                "dataset_size": len(df),
                "train_size": len(train_df),
                "test_size_rows": len(test_df),
            }
        )

        predictions = predict_batch(
            classifier=classifier,
            texts=test_df[config.TEXT_COLUMN].tolist(),
            batch_size=config.BATCH_SIZE,
        )
        y_true = test_df[config.LABEL_COLUMN].tolist()
        y_pred = [pred["label"] for pred in predictions]

        metrics = compute_classification_metrics(y_true=y_true, y_pred=y_pred)
        mlflow.log_metrics(metrics)

        cm_path = save_confusion_matrix(
            y_true=y_true,
            y_pred=y_pred,
            output_dir=config.REPORTS_DIR,
        )
        pred_report_path = save_prediction_report(
            texts=test_df[config.TEXT_COLUMN].tolist(),
            y_true=y_true,
            predictions=predictions,
            output_dir=config.REPORTS_DIR,
        )

        mlflow.log_artifact(str(cm_path), artifact_path="reports")
        mlflow.log_artifact(str(pred_report_path), artifact_path="reports")

        logged_model_info = mlflow.transformers.log_model(
            transformers_model=classifier,
            name="model",
            task=config.TASK_NAME,
            input_example=["This movie is visually stunning and deeply emotional."],
            pip_requirements=[
                "mlflow>=3.11,<4.0",
                "transformers>=4.40,<5.0",
                "torch>=2.2,<3.0",
                "torchvision>=0.26,<1.0",
            ],
        )

        model_uri_for_registration = getattr(
            logged_model_info,
            "model_uri",
            f"runs:/{run.info.run_id}/model",
        )
        model_version = try_register_model(model_uri_for_registration)
        if model_version:
            mlflow.set_tag("registered_model_version", model_version)

        print(f"Run concluida: {run.info.run_id}")
        print("Metricas registradas:")
        print(pformat(metrics))
        if model_version:
            print(
                f"Modelo registrado como versao {model_version} em "
                f"{config.REGISTERED_MODEL_NAME}"
            )
        else:
            print("Modelo salvo no run, sem registro de versao.")


if __name__ == "__main__":
    main()
