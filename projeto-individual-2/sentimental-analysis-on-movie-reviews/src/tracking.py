"""MLflow tracking wrapper around the pipeline.

This is the only module in the project that imports mlflow. The pipeline
stages themselves (ingest, preprocess, loader, evaluate, pipeline.run)
stay MLflow-free so they can be run, imported, and tested without it.

Usage: invoked from src/pipeline.py's __main__ block when --track is passed.
    python -m src.pipeline --sample-size 200 --track
    python -m src.pipeline --sample-size 200 --track --register-model
"""

import argparse
import tempfile
from pathlib import Path

import mlflow
import mlflow.transformers  # noqa: F401  (registers the transformers flavor)
from mlflow.data import from_pandas
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from src.data.preprocess import PREPROCESS_VERSION
from src.model.loader import MODEL_NAME
from src.pipeline import PipelineResult, run

EXPERIMENT_NAME = "sentiment-imdb"
REGISTERED_MODEL_NAME = "sentiment-imdb"

# Argparse attributes that describe *how* we tracked the run, not *what*
# the run computed. We strip them before logging so the MLflow params block
# stays focused on experiment inputs.
_TRACKING_CONTROL_FLAGS = frozenset({"track", "register_model", "run_name"})


def _build_run_name(args: argparse.Namespace) -> str:
    """Return the user-supplied run name or auto-generate a descriptive one."""
    if args.run_name:
        return args.run_name
    return (
        f"sample-{args.sample_size}"
        f"_bs-{args.batch_size}"
        f"_maxlen-{args.max_length}"
    )


def _collect_params(args: argparse.Namespace) -> dict[str, object]:
    """Build the params dict for mlflow.log_params from the CLI namespace."""
    params: dict[str, object] = {
        key: value
        for key, value in vars(args).items()
        if key not in _TRACKING_CONTROL_FLAGS
    }
    # Path objects serialize weirdly in MLflow; force a clean string.
    if "data_dir" in params:
        params["data_dir"] = str(params["data_dir"])
    params["model_name"] = MODEL_NAME
    params["preprocess_version"] = PREPROCESS_VERSION
    return params


def _format_confusion_matrix(result: PipelineResult) -> str:
    """Return a 2x2 labeled confusion matrix as a plain-text table."""
    cm = confusion_matrix(result.true_labels, result.predictions, labels=[0, 1])
    (tn, fp), (fn, tp) = cm
    return (
        "             pred_neg  pred_pos\n"
        f"true_neg     {tn:>8d}  {fp:>8d}\n"
        f"true_pos     {fn:>8d}  {tp:>8d}\n"
    )


def _log_artifacts(result: PipelineResult) -> None:
    """Write artifact files to a temp dir and hand them to mlflow.log_artifact.

    Three files are produced per run:
        classification_report.txt - per-class precision/recall/F1/support
        predictions.csv           - one row per sample for error analysis
        confusion_matrix.txt      - 2x2 labeled text table
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 1. Classification report (per-class precision/recall/F1/support)
        report_text = classification_report(
            result.true_labels,
            result.predictions,
            target_names=["neg", "pos"],
            digits=4,
        )
        report_path = tmp / "classification_report.txt"
        report_path.write_text(report_text, encoding="utf-8")
        mlflow.log_artifact(str(report_path))

        # 2. Predictions CSV (text + true + predicted + confidence)
        preds_df = pd.DataFrame(
            {
                "text": result.texts,
                "true_label": result.true_labels,
                "predicted_label": result.predictions,
                "confidence": result.confidences,
            }
        )
        preds_path = tmp / "predictions.csv"
        preds_df.to_csv(preds_path, index=False, encoding="utf-8")
        mlflow.log_artifact(str(preds_path))

        # 3. Confusion matrix (text table)
        cm_path = tmp / "confusion_matrix.txt"
        cm_path.write_text(_format_confusion_matrix(result), encoding="utf-8")
        mlflow.log_artifact(str(cm_path))


def run_with_tracking(args: argparse.Namespace) -> PipelineResult:
    """Execute the pipeline inside an MLflow run, logging params and metrics."""
    mlflow.set_experiment(EXPERIMENT_NAME)
    run_name = _build_run_name(args)

    with mlflow.start_run(run_name=run_name):
        # Log params up front so a mid-pipeline crash still yields context.
        mlflow.log_params(_collect_params(args))

        result = run(args)

        mlflow.log_metrics(result.metrics)
        _log_artifacts(result)

        df = pd.DataFrame({
            "text": result.texts,
            "label": result.true_labels
        })

        dataset = from_pandas(
            df,
            source=str(args.data_dir),
            name=f"imdb-{args.split}"
        )

        mlflow.log_input(dataset, context="evaluation")

        if args.register_model:
            _register_model(result)

        print(f"\nMLflow run logged: experiment={EXPERIMENT_NAME} name={run_name}")
        return result


def _register_model(result: PipelineResult) -> None:
    """Log the HuggingFace pipeline as an MLflow model and register a new version.

    Only called when --register-model is passed. This writes the full model
    weights (~268MB for DistilBERT) to the current run's artifact directory
    and creates a new version under the REGISTERED_MODEL_NAME entry in the
    Model Registry.
    """
    print(f"\nRegistering model as '{REGISTERED_MODEL_NAME}'...")
    model_info = mlflow.transformers.log_model(
        transformers_model=result.classifier,
        artifact_path="model",
        registered_model_name=REGISTERED_MODEL_NAME,
    )
    print(f"      model_uri: {model_info.model_uri}")
