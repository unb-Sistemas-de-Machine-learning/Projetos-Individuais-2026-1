# src/model/guardrails.py
import numpy as np
from PIL import Image


class GuardrailError(ValueError):
    """Raised when an image fails input validation."""
    def __init__(self, message: str, reason: str = "unknown"):
        super().__init__(message)
        self.reason = reason  # e.g. "blank", "overexposed", "too_small", "too_large", "wrong_mode"


MIN_DIM = 100
MAX_DIM = 4096
BLANK_THRESHOLD = 2       # mean pixel value below this → blank
OVEREXPOSED_THRESHOLD = 250  # mean pixel value above this → overexposed
MAX_DETECTIONS = 150
MAX_BOX_AREA_RATIO = 0.25  # detections covering >25% of the image are artifacts


def validate_input(img: Image.Image) -> None:
    """
    Validate image before inference. Raises GuardrailError with a
    descriptive message if the image should not be processed.
    """
    if img.mode != "RGB":
        raise GuardrailError(f"Image must be RGB, got {img.mode}", reason="wrong_mode")

    w, h = img.size
    if min(w, h) < MIN_DIM:
        raise GuardrailError(f"Image too small: {w}x{h} (minimum {MIN_DIM}px on shortest edge)", reason="too_small")
    if max(w, h) > MAX_DIM:
        raise GuardrailError(f"Image too large: {w}x{h} (maximum {MAX_DIM}px on longest edge)", reason="too_large")

    mean_val = np.array(img).mean()
    if mean_val < BLANK_THRESHOLD:
        raise GuardrailError(f"Image appears blank (mean pixel value: {mean_val:.1f})", reason="blank")
    if mean_val > OVEREXPOSED_THRESHOLD:
        raise GuardrailError(f"Image appears overexposed (mean pixel value: {mean_val:.1f})", reason="overexposed")


def validate_output(
    detections: list[dict],
    confidence_threshold: float = 0.4,
    img_size: tuple[int, int] | None = None,  # (width, height)
    max_box_area_ratio: float = MAX_BOX_AREA_RATIO,
) -> dict:
    """
    Filter detections by confidence and box size, and attach warnings for anomalous outputs.
    Returns dict with 'detections' (filtered) and 'warnings' (list of strings).

    Boxes covering more than max_box_area_ratio of the image are dropped — these are
    typically satellite trails, diffraction spikes, or other imaging artifacts that
    YOLOS mistakes for objects.
    """
    img_area = (img_size[0] * img_size[1]) if img_size else None

    filtered = []
    for d in detections:
        if d["score"] < confidence_threshold:
            continue
        if img_area:
            x1, y1, x2, y2 = d["box"]
            box_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
            if box_area / img_area > max_box_area_ratio:
                continue
        filtered.append(d)

    warnings = []
    if len(filtered) == 0:
        warnings.append("no_detections")
    elif len(filtered) > MAX_DETECTIONS:
        warnings.append("too_many_detections")

    return {"detections": filtered, "warnings": warnings}
