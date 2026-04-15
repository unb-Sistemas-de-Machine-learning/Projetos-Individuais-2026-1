"""End-to-end IMDb sentiment analysis pipeline.

Single entry point for the project. Orchestrates the four stages:
    1. Ingest   - load aclImdb from disk
    2. Preprocess - strip HTML, normalize whitespace
    3. Load model - build the DistilBERT classifier
    4. Evaluate - run inference and compute metrics

Run from the project root:
    python -m src.pipeline --sample-size 200
"""

import argparse
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.data.ingest import load_imdb
from src.data.preprocess import preprocess_dataframe
from src.model.evaluate import (
    compute_metrics,
    extract_predictions,
    run_inference,
)
from src.model.loader import DEFAULT_MAX_LENGTH, MODEL_NAME, build_classifier


@dataclass
class PipelineResult:
    """Everything a downstream consumer might need from one pipeline run.

    `run()` returns this instead of just the metrics dict so that the MLflow
    tracking wrapper (src/tracking.py) can log artifacts (predictions CSV,
    classification report, confusion matrix) and register the model, without
    having to re-run any pipeline stage.
    """

    metrics: dict[str, float]
    predictions: list[int]
    confidences: list[float]
    true_labels: list[int]
    texts: list[str]
    classifier: Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="IMDb sentiment analysis pipeline (DistilBERT + aclImdb)."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw/aclImdb"),
        help="Path to the Stanford aclImdb root directory.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["train", "test"],
        help="Which dataset split to evaluate on.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=200,
        help="Number of reviews to evaluate. Use 0 for the full split (25,000).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Inference batch size.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help="Maximum token length. DistilBERT caps at 512.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Seed used for sampling. Passed through for reproducibility.",
    )
    parser.add_argument(
        "--track",
        action="store_true",
        help="Wrap the run in mlflow.start_run() and log params, metrics, artifacts.",
    )
    parser.add_argument(
        "--register-model",
        action="store_true",
        help="Also register the model in the MLflow Model Registry. Requires --track.",
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Optional MLflow run name. Auto-generated from params if omitted.",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> PipelineResult:
    """Execute the pipeline end-to-end and return a PipelineResult."""
    sample = None if args.sample_size == 0 else args.sample_size

    print(f"[1/4] Loading dataset from {args.data_dir} (split={args.split})...")
    df = load_imdb(
        args.data_dir,
        split=args.split,
        sample_size=sample,
        random_seed=args.random_seed,
    )
    print(
        f"      Loaded {len(df)} reviews | "
        f"label distribution: {df['label'].value_counts().to_dict()}"
    )

    print("[2/4] Preprocessing (HTML strip + whitespace normalize)...")
    df = preprocess_dataframe(df)
    print(f"      Avg text length: {df['text'].str.len().mean():.0f} chars")

    print(f"[3/4] Loading model: {MODEL_NAME}")
    classifier = build_classifier(device=-1, max_length=args.max_length)
    print(f"      Device: CPU | max_length: {args.max_length}")

    print(f"[4/4] Running inference (batch_size={args.batch_size})...")
    t0 = time.perf_counter()
    texts = df["text"].tolist()
    true_labels = df["label"].tolist()
    results = run_inference(classifier, texts, batch_size=args.batch_size)
    elapsed = time.perf_counter() - t0
    preds, confs = extract_predictions(results)
    metrics = compute_metrics(true_labels, preds)
    print(
        f"      Inference time: {elapsed:.1f}s "
        f"({elapsed / len(df) * 1000:.0f} ms/sample)"
    )

    print("\nResults:")
    for name, value in metrics.items():
        print(f"  {name:9s} {value:.4f}")

    return PipelineResult(
        metrics=metrics,
        predictions=preds,
        confidences=confs,
        true_labels=true_labels,
        texts=texts,
        classifier=classifier,
    )


if __name__ == "__main__":
    args = parse_args()
    if args.track:
        # Local import so the mlflow dependency stays off the import path
        # when --track is not passed. The pipeline stages themselves must
        # never import mlflow — that keeps `run()` testable without it.
        from src.tracking import run_with_tracking

        run_with_tracking(args)
    else:
        if args.register_model:
            raise SystemExit("--register-model requires --track")
        run(args)
