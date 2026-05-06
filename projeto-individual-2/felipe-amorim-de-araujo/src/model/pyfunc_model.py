# src/model/pyfunc_model.py
"""
MLflow PythonModel wrapper for the full space-object detection pipeline.

Bundles guardrails + arcsinh preprocessing + YOLOS inference into a single
deployable artifact so that `mlflow models serve` exposes a complete, safe
endpoint — callers send raw JPEG bytes; detections come back as JSON.

Input DataFrame columns
-----------------------
b64_image : str
    Base64-encoded JPEG image (RFC 4648, standard alphabet).

Output DataFrame columns
------------------------
result : str
    JSON object with keys:
      - "detections": list of {"box": [x1,y1,x2,y2], "score": float[, "label": str]}
      - "warnings":   list of str  (e.g. "no_detections", "too_many_detections")
      - "error":      str | null   (set when input guardrail rejects the image)
      - "reason":     str | null   (guardrail rejection reason code)

Usage
-----
    # Serve from registry (version 1):
    mlflow models serve -m "models:/space-detector/1" --port 5001 --no-conda

    # Call the endpoint:
    python -m src.inference --image data/raw/field_0000.jpg
"""
from __future__ import annotations

import base64
import json
from io import BytesIO
from pathlib import Path

import mlflow.pyfunc
import pandas as pd
from PIL import Image

# Dual-import: works when run from project root (src.* style) and when loaded
# by MLflow serving after code_paths=["src"] adds `src/` to sys.path.
try:
    from src.data.preprocess import preprocess_image
    from src.model.detector import SpaceDetector
    from src.model.guardrails import GuardrailError, validate_input, validate_output
except ImportError:
    from data.preprocess import preprocess_image  # type: ignore[no-redef]
    from model.detector import SpaceDetector  # type: ignore[no-redef]
    from model.guardrails import GuardrailError, validate_input, validate_output  # type: ignore[no-redef]


class SpaceDetectorPyfunc(mlflow.pyfunc.PythonModel):
    """
    End-to-end inference pipeline as an MLflow PythonModel.

    load_context reads the model checkpoint directory and config from the
    artifact store; predict runs the full pipeline on every image in the batch.
    """

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        with open(context.artifacts["config"]) as f:
            config = json.load(f)

        self.confidence_threshold: float = float(config.get("confidence_threshold", 0.4))
        self.detector = SpaceDetector(model_name=context.artifacts["checkpoint"])

    def predict(
        self,
        context: mlflow.pyfunc.PythonModelContext,
        model_input: pd.DataFrame,
        params: dict | None = None,
    ) -> pd.DataFrame:
        """
        Run inference on a batch of base64-encoded images.

        Parameters
        ----------
        model_input : pd.DataFrame
            Must contain column "b64_image" with base64-encoded JPEG strings.
        params : dict, optional
            "confidence_threshold" (float) overrides the value baked into the model.

        Returns
        -------
        pd.DataFrame with column "result" (JSON string per row).
        """
        confidence_threshold = self.confidence_threshold
        if params and "confidence_threshold" in params:
            confidence_threshold = float(params["confidence_threshold"])

        results = []
        for b64_str in model_input["b64_image"]:
            result = self._run_single(b64_str, confidence_threshold)
            results.append(json.dumps(result))

        return pd.DataFrame({"result": results})

    def _run_single(self, b64_str: str, confidence_threshold: float) -> dict:
        try:
            img_bytes = base64.b64decode(b64_str)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
        except Exception as exc:
            return {"detections": [], "warnings": [], "error": f"Cannot decode image: {exc}", "reason": "decode_error"}

        try:
            validate_input(img)
        except GuardrailError as exc:
            return {"detections": [], "warnings": [], "error": str(exc), "reason": exc.reason}

        preprocessed = preprocess_image(img)
        raw_detections = self.detector.detect(preprocessed)
        output = validate_output(
            raw_detections,
            confidence_threshold=confidence_threshold,
            img_size=img.size,
        )

        return {
            "detections": output["detections"],
            "warnings": output["warnings"],
            "error": None,
            "reason": None,
        }
