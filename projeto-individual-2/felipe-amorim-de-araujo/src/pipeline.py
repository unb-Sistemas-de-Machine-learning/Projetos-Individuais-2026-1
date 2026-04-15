# src/pipeline.py
import json
import subprocess
import time
import mlflow
import mlflow.pytorch
import numpy as np
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw

from src.data.ingest import build_dataset
from src.data.preprocess import preprocess_image
from src.model.detector import SpaceDetector
from src.model.guardrails import validate_input, validate_output, GuardrailError

EXPERIMENT_NAME = "space-object-detection"


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _box_area(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def _draw_detections(img: Image.Image, detections: list[dict]) -> Image.Image:
    """Draw bounding boxes on image for artifact logging."""
    out = img.copy()
    draw = ImageDraw.Draw(out)
    for det in detections:
        x1, y1, x2, y2 = det["box"]
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.text((x1, max(0, y1 - 12)), f"{det['score']:.2f}", fill="red")
    return out


def run_pipeline(
    data_dir: Path = Path("data"),
    n_regions: int = 20,
    radius_deg: float = 0.05,
    scale: float = 0.2,
    confidence_threshold: float = 0.4,
    model_path: str = "hustvl/yolos-small",
):
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():
        # --- Tags ---
        mlflow.set_tags({
            "git_commit": _git_commit(),
            "model": model_path,
        })

        # --- Log params ---
        mlflow.log_params({
            "n_regions": n_regions,
            "radius_deg": radius_deg,
            "scale": scale,
            "confidence_threshold": confidence_threshold,
            "model_name": model_path,
        })

        # --- Ingest ---
        print(f"[1/4] Ingesting data: n_regions={n_regions}")
        t0 = time.perf_counter()
        stats = build_dataset(data_dir, n_regions=n_regions, radius_deg=radius_deg, scale=scale)
        ingest_time = time.perf_counter() - t0

        mlflow.log_metrics({
            "n_images_downloaded": stats["downloaded"],
            "n_regions_skipped": stats["skipped"],
            "ingest_time_s": round(ingest_time, 2),
        })

        # --- Load model ---
        print(f"[2/4] Loading model: {model_path}")
        detector = SpaceDetector(model_name=model_path)

        # --- Inference over all downloaded images ---
        print("[3/4] Running inference")
        raw_dir = data_dir / "raw"
        processed_dir = data_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)

        all_detections = []
        all_scores = []
        all_areas = []
        guardrail_counts = defaultdict(int)
        per_image_times = []

        image_paths = sorted(raw_dir.glob("*.jpg"))

        for step, img_path in enumerate(image_paths):
            img = Image.open(img_path).convert("RGB")

            # Input guardrail
            try:
                validate_input(img)
            except GuardrailError as e:
                print(f"  [guardrail] Rejected {img_path.name}: {e}")
                guardrail_counts[e.reason] += 1
                continue

            # Preprocess + detect
            t_img = time.perf_counter()
            preprocessed = preprocess_image(img)
            raw_detections = detector.detect(preprocessed)
            img_time = time.perf_counter() - t_img
            per_image_times.append(img_time)

            # Output guardrail
            result = validate_output(
                raw_detections,
                confidence_threshold=confidence_threshold,
                img_size=img.size,
            )
            detections = result["detections"]

            if result["warnings"]:
                print(f"  [guardrail] {img_path.name}: {result['warnings']}")

            scores = [d["score"] for d in detections]
            areas = [_box_area(d["box"]) for d in detections]
            all_scores.extend(scores)
            all_areas.extend(areas)
            all_detections.append({"image": img_path.name, "detections": detections})

            # Per-image step metrics (shows as charts in MLflow UI)
            mlflow.log_metrics({
                "img_detections": len(detections),
                "img_avg_confidence": float(np.mean(scores)) if scores else 0.0,
                "img_inference_time_s": round(img_time, 3),
            }, step=step)

            # Save annotated image as artifact
            annotated = _draw_detections(img, detections)
            annotated.save(processed_dir / img_path.name)

        # --- Aggregate metrics ---
        total_detections = sum(len(r["detections"]) for r in all_detections)
        n_processed = len(all_detections)
        n_with_detections = sum(1 for r in all_detections if r["detections"])
        total_guardrail_rejections = sum(guardrail_counts.values())

        detection_rate = n_with_detections / n_processed if n_processed > 0 else 0.0
        avg_inference_time = float(np.mean(per_image_times)) if per_image_times else 0.0
        total_inference_time = sum(per_image_times)

        summary_metrics: dict = {
            # Throughput
            "n_detections_total": total_detections,
            "n_images_processed": n_processed,
            "n_images_with_detections": n_with_detections,
            "detection_rate": round(detection_rate, 4),
            # Timing
            "inference_time_total_s": round(total_inference_time, 2),
            "inference_time_avg_s": round(avg_inference_time, 3),
            # Guardrails
            "guardrail_rejections_total": total_guardrail_rejections,
            "guardrail_rejections_blank": guardrail_counts["blank"],
            "guardrail_rejections_overexposed": guardrail_counts["overexposed"],
            "guardrail_rejections_too_small": guardrail_counts["too_small"],
            "guardrail_rejections_too_large": guardrail_counts["too_large"],
        }

        # Confidence distribution (only when detections exist)
        if all_scores:
            scores_arr = np.array(all_scores)
            summary_metrics.update({
                "confidence_min": round(float(scores_arr.min()), 4),
                "confidence_p25": round(float(np.percentile(scores_arr, 25)), 4),
                "confidence_p50": round(float(np.percentile(scores_arr, 50)), 4),
                "confidence_avg": round(float(scores_arr.mean()), 4),
                "confidence_p75": round(float(np.percentile(scores_arr, 75)), 4),
                "confidence_p95": round(float(np.percentile(scores_arr, 95)), 4),
                "confidence_max": round(float(scores_arr.max()), 4),
            })

        # Box size distribution (only when detections exist)
        if all_areas:
            areas_arr = np.array(all_areas)
            summary_metrics.update({
                "box_area_min": round(float(areas_arr.min()), 1),
                "box_area_avg": round(float(areas_arr.mean()), 1),
                "box_area_max": round(float(areas_arr.max()), 1),
            })

        mlflow.log_metrics(summary_metrics)

        # --- Log artifacts ---
        print("[4/4] Logging artifacts")
        detections_path = data_dir / "detections.json"
        detections_path.write_text(json.dumps(all_detections, indent=2))
        mlflow.log_artifact(str(detections_path))

        for img_path in list(processed_dir.glob("*.jpg"))[:5]:
            mlflow.log_artifact(str(img_path), artifact_path="annotated_samples")

        # --- Register model ---
        mlflow.pytorch.log_model(
            detector.model,
            artifact_path="model",
            registered_model_name="space-detector",
        )

        print(f"Done. {total_detections} detections across {n_processed} images "
              f"(detection rate: {detection_rate:.0%}).")
        print(f"Guardrail rejections: {total_guardrail_rejections} "
              f"(blank={guardrail_counts['blank']}, "
              f"overexposed={guardrail_counts['overexposed']})")
        if all_scores:
            print(f"Confidence — min: {summary_metrics['confidence_min']:.3f}  "
                  f"p50: {summary_metrics['confidence_p50']:.3f}  "
                  f"max: {summary_metrics['confidence_max']:.3f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run space object detection pipeline")
    parser.add_argument("--n-regions", type=int, default=20)
    parser.add_argument("--radius-deg", type=float, default=0.05)
    parser.add_argument("--scale", type=float, default=0.2)
    parser.add_argument("--confidence-threshold", type=float, default=0.4)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--model-path", type=str, default="hustvl/yolos-small",
                        help="HuggingFace model name or path to a local fine-tuned checkpoint")
    args = parser.parse_args()

    run_pipeline(
        data_dir=args.data_dir,
        n_regions=args.n_regions,
        radius_deg=args.radius_deg,
        scale=args.scale,
        confidence_threshold=args.confidence_threshold,
        model_path=args.model_path,
    )
