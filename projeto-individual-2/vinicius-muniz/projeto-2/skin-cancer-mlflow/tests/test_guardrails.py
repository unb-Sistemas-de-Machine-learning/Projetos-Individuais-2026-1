import numpy as np
from PIL import Image
from src.guardrails import apply_confidence_guard, compute_ita, check_input


def test_low_confidence_returns_uncertain():
    out = apply_confidence_guard({"benign": 0.55, "malignant": 0.45}, 0.70)
    assert out["decision"] == "uncertain"
    assert out["label"] is None


def test_high_confidence_classifies():
    out = apply_confidence_guard({"benign": 0.95, "malignant": 0.05}, 0.70)
    assert out["decision"] == "classified"
    assert out["label"] == "benign"


def test_ita_light_skin():
    arr = np.full((224, 224, 3), 230, dtype=np.uint8)
    img = Image.fromarray(arr)
    L = compute_ita(img)
    assert L > 80


def test_ita_dark_skin_rejected():
    arr = np.full((224, 224, 3), 70, dtype=np.uint8)
    arr[..., 0] = 90
    arr[..., 1] = 60
    arr[..., 2] = 45
    img = Image.fromarray(arr)
    guard = check_input(img, {"skin_tone_check": True, "skin_tone_ita_min": 55.0})
    assert not guard.allowed
