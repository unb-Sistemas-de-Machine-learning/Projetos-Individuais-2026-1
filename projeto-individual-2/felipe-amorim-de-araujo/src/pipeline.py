# src/pipeline.py
import json
import mlflow
import mlflow.pytorch
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

from src.data.ingest import build_dataset
from src.data.preprocess import preprocess_image
from src.model.detector import SpaceDetector
from src.model.guardrails import validate_input, validate_output, GuardrailError

EXPERIMENT_NAME = "space-object-detection"


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
):
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():
        # --- Log params ---
        mlflow.log_params({
            "n_regions": n_regions,
            "radius_deg": radius_deg,
            "scale": scale,
            "confidence_threshold": confidence_threshold,
            "model_name": "hustvl/yolos-small",
        })

        # --- Ingest ---
        print(f"[1/4] Ingesting data: n_regions={n_regions}")
        stats = build_dataset(data_dir, n_regions=n_regions, radius_deg=radius_deg, scale=scale)
        mlflow.log_metrics({
            "n_images_downloaded": stats["downloaded"],
            "n_regions_skipped": stats["skipped"],
        })

        # --- Load model ---
        print("[2/4] Loading YOLOS-small")
        detector = SpaceDetector()

        # --- Inference over all downloaded images ---
        print("[3/4] Running inference")
        raw_dir = data_dir / "raw"
        processed_dir = data_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)

        all_detections = []
        guardrail_rejections = 0
        all_scores = []

        image_paths = sorted(raw_dir.glob("*.jpg"))

        for img_path in image_paths:
            img = Image.open(img_path).convert("RGB")

            # Input guardrail
            try:
                validate_input(img)
            except GuardrailError as e:
                print(f"  [guardrail] Rejected {img_path.name}: {e}")
                guardrail_rejections += 1
                continue

            # Preprocess + detect
            preprocessed = preprocess_image(img)
            raw_detections = detector.detect(preprocessed)

            # Output guardrail
            result = validate_output(raw_detections, confidence_threshold=confidence_threshold)
            detections = result["detections"]

            if result["warnings"]:
                print(f"  [guardrail] {img_path.name}: {result['warnings']}")

            all_detections.append({"image": img_path.name, "detections": detections})
            all_scores.extend([d["score"] for d in detections])

            # Save annotated image as artifact
            annotated = _draw_detections(img, detections)
            annotated.save(processed_dir / img_path.name)

        # --- Log metrics ---
        total_detections = sum(len(r["detections"]) for r in all_detections)
        avg_confidence = float(np.mean(all_scores)) if all_scores else 0.0

        mlflow.log_metrics({
            "n_detections_total": total_detections,
            "avg_confidence": avg_confidence,
            "guardrail_rejections": guardrail_rejections,
        })

        # --- Log artifacts ---
        print("[4/4] Logging artifacts")
        detections_path = data_dir / "detections.json"
        detections_path.write_text(json.dumps(all_detections, indent=2))
        mlflow.log_artifact(str(detections_path))

        for img_path in list((processed_dir).glob("*.jpg"))[:5]:  # log up to 5 sample images
            mlflow.log_artifact(str(img_path), artifact_path="annotated_samples")

        # --- Register model ---
        mlflow.pytorch.log_model(
            detector.model,
            artifact_path="model",
            registered_model_name="space-detector",
        )

        print(f"Done. {total_detections} detections across {len(image_paths)} images.")
        print(f"Guardrail rejections: {guardrail_rejections}")
        print(f"Average confidence: {avg_confidence:.3f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run space object detection pipeline")
    parser.add_argument("--n-regions", type=int, default=20)
    parser.add_argument("--radius-deg", type=float, default=0.05)
    parser.add_argument("--scale", type=float, default=0.2)
    parser.add_argument("--confidence-threshold", type=float, default=0.4)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    run_pipeline(
        data_dir=args.data_dir,
        n_regions=args.n_regions,
        radius_deg=args.radius_deg,
        scale=args.scale,
        confidence_threshold=args.confidence_threshold,
    )
