# src/inference.py
"""
Load the registered YOLOS-small model from MLflow registry and run inference.

Usage:
    # Start the MLflow model server first:
    mlflow models serve -m "models:/space-detector/1" --port 5001 --no-conda

    # Then call the endpoint:
    python src/inference.py --image data/raw/field_0000.jpg
"""
import json
import argparse
import requests
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO

from src.model.guardrails import validate_input, GuardrailError
from src.data.preprocess import preprocess_image


def image_to_base64(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def run_inference(image_path: Path, endpoint: str = "http://localhost:5001") -> dict:
    img = Image.open(image_path).convert("RGB")

    # Guardrail: validate before sending
    validate_input(img)

    preprocessed = preprocess_image(img)
    payload = {"instances": [{"b64": image_to_base64(preprocessed)}]}

    response = requests.post(
        f"{endpoint}/invocations",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run inference on a space image")
    parser.add_argument("--image", type=Path, required=True, help="Path to input image")
    parser.add_argument("--endpoint", default="http://localhost:5001")
    args = parser.parse_args()

    try:
        result = run_inference(args.image, args.endpoint)
        print(json.dumps(result, indent=2))
    except GuardrailError as e:
        print(f"Guardrail rejected image: {e}")
