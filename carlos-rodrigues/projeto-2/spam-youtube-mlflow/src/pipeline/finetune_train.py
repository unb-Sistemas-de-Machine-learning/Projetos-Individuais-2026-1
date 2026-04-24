import json
import logging
from pathlib import Path

import mlflow
import pandas as pd
from mlflow.models import infer_signature

from src.config import (
    ARTIFACTS_DIR,
    CONTENT_COLUMN,
    FINETUNE_BATCH_SIZE,
    FINETUNE_LEARNING_RATE,
    FINETUNE_NUM_EPOCHS,
    FINETUNING_VALIDATION_SIZE,
    FINETUNED_MODEL_DIR,
    HF_MODEL_NAME,
    MLFLOW_EXPERIMENT_FINETUNING,
    MLFLOW_TRACKING_URI,
    REGISTERED_MODEL_NAME,
    SPAM_THRESHOLD,
    TARGET_COLUMN,
)
from src.data.ingestion import data_quality_report, load_raw_comments, temporal_split
from src.model.classifier import PretrainedSpamModel
from src.model.finetuning import FinetuneSpamModel
from src.pipeline.evaluation import evaluate_predictions
from src.pipeline.mlflow_model import SpamClassifierPyfuncModel

logger = logging.getLogger(__name__)


def run_finetuning_pipeline(register_model=True):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_FINETUNING)

    logger.info("=" * 80)
    logger.info("INICIANDO PIPELINE COM FINE-TUNING")
    logger.info("=" * 80)

    logger.info("Carregando dados...")
    dataset = load_raw_comments()
    train_df, test_df = temporal_split(dataset, test_size=0.2)
    quality = data_quality_report(dataset)

    logger.info(f"Dataset carregado: {len(dataset)} comentários")
    logger.info(f"  Train: {len(train_df)} comentários")
    logger.info(f"  Test: {len(test_df)} comentários")

    logger.info("\n" + "-" * 80)
    logger.info("ETAPA 1: FINE-TUNING DO MODELO")
    logger.info("-" * 80)

    with mlflow.start_run(run_name="finetuning-phase") as finetune_run:
        finetune_run_id = finetune_run.info.run_id

        train_size = len(train_df)
        val_size = int(train_size * FINETUNING_VALIDATION_SIZE)
        finetune_train_size = train_size - val_size

        finetune_train_df = train_df.iloc[:finetune_train_size]
        finetune_val_df = train_df.iloc[finetune_train_size:]

        logger.info(f"Fine-tuning com {len(finetune_train_df)} exemplos (train) e {len(finetune_val_df)} (val)")

        texts_train = finetune_train_df[CONTENT_COLUMN].tolist()
        labels_train = finetune_train_df[TARGET_COLUMN].tolist()
        texts_val = finetune_val_df[CONTENT_COLUMN].tolist()
        labels_val = finetune_val_df[TARGET_COLUMN].tolist()

        finetuner = FinetuneSpamModel(
            model_name=HF_MODEL_NAME,
            output_dir=FINETUNED_MODEL_DIR,
        )

        finetune_result = finetuner.train(
            train_texts=texts_train,
            train_labels=labels_train,
            val_texts=texts_val,
            val_labels=labels_val,
            num_epochs=FINETUNE_NUM_EPOCHS,
            batch_size=FINETUNE_BATCH_SIZE,
            learning_rate=FINETUNE_LEARNING_RATE,
        )

        mlflow.log_param("base_model", HF_MODEL_NAME)
        mlflow.log_param("num_epochs", FINETUNE_NUM_EPOCHS)
        mlflow.log_param("batch_size", FINETUNE_BATCH_SIZE)
        mlflow.log_param("learning_rate", FINETUNE_LEARNING_RATE)
        mlflow.log_param("train_samples", len(finetune_train_df))
        mlflow.log_param("val_samples", len(finetune_val_df))
        mlflow.log_param("class_ratio_ham_0", quality["class_ratio_ham_0"])
        mlflow.log_param("class_ratio_spam_1", quality["class_ratio_spam_1"])
        mlflow.log_param("missing_date_rows", quality["missing_date_rows"])

        mlflow.log_metric("training_loss", finetune_result["training_loss"])
        if finetune_result["eval_loss"] is not None:
            mlflow.log_metric("eval_loss", finetune_result["eval_loss"])

    logger.info(f"Fine-tuning concluído (Run ID: {finetune_run_id})")

    logger.info("\n" + "-" * 80)
    logger.info("ETAPA 2: AVALIAÇÃO NO CONJUNTO DE TESTE")
    logger.info("-" * 80)

    model_to_use = str(FINETUNED_MODEL_DIR)

    logger.info(f"Usando modelo fine-tuned local: {model_to_use}")

    model = PretrainedSpamModel(model_name=model_to_use)
    spam_proba = model.predict_proba(test_df[CONTENT_COLUMN].tolist())
    metrics = evaluate_predictions(test_df[TARGET_COLUMN], spam_proba, threshold=SPAM_THRESHOLD)

    logger.info(f"Métricas no teste:")
    for metric_name, metric_value in metrics.items():
        logger.info(f"  {metric_name}: {metric_value:.4f}")

    logger.info("\n" + "-" * 80)
    logger.info("ETAPA 3: REGISTRO NO MLFLOW")
    logger.info("-" * 80)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    predictions_df = test_df[["comment_id", CONTENT_COLUMN, TARGET_COLUMN]].copy()
    predictions_df["spam_probability"] = spam_proba
    predictions_df["prediction"] = (predictions_df["spam_probability"] >= SPAM_THRESHOLD).astype(int)

    with mlflow.start_run(run_name="evaluation-phase") as eval_run:
        run_id = eval_run.info.run_id

        mlflow.log_param("model_type", "finetuned")
        mlflow.log_param("base_model", HF_MODEL_NAME)
        mlflow.log_param("threshold", SPAM_THRESHOLD)
        mlflow.log_param("test_size", len(test_df))

        mlflow.log_metrics(metrics)

        predictions_artifact = ARTIFACTS_DIR / "test_predictions_finetuned.csv"
        predictions_df.to_csv(predictions_artifact, index=False)
        mlflow.log_artifact(str(predictions_artifact), artifact_path="predictions")
        logger.info(f"Predições salvas em: {predictions_artifact}")

        summary_artifact = ARTIFACTS_DIR / "run_summary_finetuned.json"
        summary_artifact.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "finetune_run_id": finetune_run_id,
                    "model_type": "finetuned",
                    "metrics": metrics,
                    "dataset_size": len(dataset),
                    "test_size": len(test_df),
                },
                ensure_ascii=True,
                indent=2,
            ),
            encoding="utf-8",
        )
        mlflow.log_artifact(str(summary_artifact), artifact_path="summary")
        logger.info(f"Resumo salvo em: {summary_artifact}")

        quality_artifact = ARTIFACTS_DIR / "data_quality_report_finetuned.json"
        quality_artifact.write_text(
            json.dumps(quality, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        mlflow.log_artifact(str(quality_artifact), artifact_path="data_quality")

        input_example = pd.DataFrame({CONTENT_COLUMN: ["subscribe to my channel now"]})
        output_example = pd.DataFrame(
            [
                {
                    "content": "subscribe to my channel now",
                    "allowed": True,
                    "guardrail_reason": "ok",
                    "spam_probability": 0.9,
                    "prediction": "spam",
                }
            ]
        )
        signature = infer_signature(input_example, output_example)

        model_info = mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=SpamClassifierPyfuncModel(
                model_name=model_to_use,
                threshold=SPAM_THRESHOLD,
            ),
            signature=signature,
            input_example=input_example,
            registered_model_name=REGISTERED_MODEL_NAME if register_model else None,
            pip_requirements=[
                "mlflow==2.22.0",
                "pandas==2.2.3",
                "transformers==4.51.3",
                "torch==2.7.0",
            ],
        )

        logger.info(f"Modelo registrado em MLflow: {model_info.model_uri}")

    logger.info("\n" + "=" * 80)
    logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
    logger.info("=" * 80)

    result = {
        "finetune_run_id": finetune_run_id,
        "evaluation_run_id": run_id,
        "metrics": metrics,
        "model_uri": model_info.model_uri,
        "model_type": "finetuned",
    }
    return result
