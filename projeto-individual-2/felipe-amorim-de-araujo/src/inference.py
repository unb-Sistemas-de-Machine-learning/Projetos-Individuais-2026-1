# src/inference.py
"""
Call the MLflow-served space-detector pyfunc endpoint.

The model server bundles guardrails + arcsinh preprocessing + YOLOS inference,
so callers only need to send the raw image — no preprocessing on the client side.

Usage
-----
    # 1. Start the MLflow model server (loads from registry):
    mlflow models serve -m "models:/space-detector/1" --port 5001 --no-conda

    # 2. Run inference on an image:
    python -m src.inference --image data/raw/field_0000.jpg

    # Optional: override confidence threshold at call time:
    python -m src.inference --image data/raw/field_0000.jpg --confidence-threshold 0.5
"""
import argparse
import base64
import json
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from src.model.guardrails import GuardrailError, validate_input


def image_to_base64(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def run_inference(
    image_path: Path,
    endpoint: str = "http://localhost:5001",
    confidence_threshold: float | None = None,
) -> dict:
    """
    Send a raw image to the MLflow pyfunc endpoint and return parsed detections.

    The endpoint accepts a DataFrame with column "b64_image".
    All preprocessing and guardrail logic lives inside the pyfunc model.

    A client-side guardrail check runs first for fast rejection before hitting
    the network (avoids a round-trip for obviously invalid images).
    """
    img = Image.open(image_path).convert("RGB")

    # Client-side fast guardrail — same check as the server, avoids network round-trip.
    validate_input(img)

    payload: dict = {
        "dataframe_records": [{"b64_image": image_to_base64(img)}],
    }
    if confidence_threshold is not None:
        payload["params"] = {"confidence_threshold": confidence_threshold}

    response = requests.post(
        f"{endpoint}/invocations",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()

    # MLflow pyfunc serving returns {"predictions": [{"result": "<json string>"}]}
    raw = response.json()
    predictions = raw.get("predictions", raw)
    result_str = predictions[0]["result"] if isinstance(predictions, list) else predictions
    return json.loads(result_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run inference on a space image via MLflow endpoint")
    parser.add_argument("--image", type=Path, required=True, help="Path to input image")
    parser.add_argument("--endpoint", default="http://localhost:5001")
    parser.add_argument("--confidence-threshold", type=float, default=None,
                        help="Override confidence threshold (default: uses value baked into model)")
    args = parser.parse_args()

    try:
        result = run_inference(args.image, args.endpoint, args.confidence_threshold)
        print(json.dumps(result, indent=2))
    except GuardrailError as e:
        print(f"Guardrail rejected image: {e}")
