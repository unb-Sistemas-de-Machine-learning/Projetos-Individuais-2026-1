# tests/model/test_guardrails.py
import pytest
import numpy as np
from PIL import Image
from src.model.guardrails import (
    validate_input,
    validate_output,
    GuardrailError,
)


def make_image(w=640, h=640, mode="RGB", value=30):
    arr = np.full((h, w, 3), value, dtype=np.uint8)
    return Image.fromarray(arr, mode=mode)


# --- Input guardrails ---

def test_valid_image_passes():
    img = make_image()
    validate_input(img)  # should not raise


def test_rejects_non_rgb():
    img = Image.new("L", (640, 640))  # grayscale
    with pytest.raises(GuardrailError, match="RGB") as exc:
        validate_input(img)
    assert exc.value.reason == "wrong_mode"


def test_rejects_too_small():
    img = make_image(w=50, h=50)
    with pytest.raises(GuardrailError, match="too small") as exc:
        validate_input(img)
    assert exc.value.reason == "too_small"


def test_rejects_too_large():
    img = make_image(w=5000, h=5000)
    with pytest.raises(GuardrailError, match="too large") as exc:
        validate_input(img)
    assert exc.value.reason == "too_large"


def test_rejects_blank_image():
    img = make_image(value=1)  # below BLANK_THRESHOLD=2
    with pytest.raises(GuardrailError, match="blank") as exc:
        validate_input(img)
    assert exc.value.reason == "blank"


def test_rejects_overexposed_image():
    img = make_image(value=255)  # all white
    with pytest.raises(GuardrailError, match="overexposed") as exc:
        validate_input(img)
    assert exc.value.reason == "overexposed"


# --- Output guardrails ---

def test_filters_low_confidence_detections():
    detections = [
        {"box": [10, 10, 50, 50], "score": 0.8},
        {"box": [60, 60, 90, 90], "score": 0.2},  # below threshold
    ]
    result = validate_output(detections, confidence_threshold=0.4)
    assert len(result["detections"]) == 1
    assert result["detections"][0]["score"] == 0.8


def test_warns_zero_detections():
    result = validate_output([], confidence_threshold=0.4)
    assert result["warnings"] == ["no_detections"]


def test_warns_too_many_detections():
    detections = [{"box": [i, i, i+10, i+10], "score": 0.9} for i in range(200)]
    result = validate_output(detections, confidence_threshold=0.4)
    assert "too_many_detections" in result["warnings"]


def test_clean_output_no_warnings():
    detections = [{"box": [10, 10, 50, 50], "score": 0.7}]
    result = validate_output(detections, confidence_threshold=0.4)
    assert result["warnings"] == []


def test_filters_oversized_boxes():
    """Boxes covering >25% of the image should be dropped as artifacts."""
    # 400x400 box on a 640x640 image = 39% — should be filtered
    artifact = {"box": [0.0, 0.0, 400.0, 400.0], "score": 0.9}
    small = {"box": [10.0, 10.0, 50.0, 50.0], "score": 0.9}
    result = validate_output([artifact, small], confidence_threshold=0.4, img_size=(640, 640))
    assert len(result["detections"]) == 1
    assert result["detections"][0] == small


def test_oversized_box_filter_skipped_without_img_size():
    """Without img_size the area filter should not apply."""
    artifact = {"box": [0.0, 0.0, 400.0, 400.0], "score": 0.9}
    result = validate_output([artifact], confidence_threshold=0.4, img_size=None)
    assert len(result["detections"]) == 1
