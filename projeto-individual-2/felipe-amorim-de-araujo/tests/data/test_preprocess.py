# tests/data/test_preprocess.py
import numpy as np
import pytest
from PIL import Image
from src.data.preprocess import arcsinh_stretch, preprocess_image


def test_arcsinh_stretch_output_range():
    """Output should be uint8 image with values in [0, 255]."""
    arr = np.random.randint(0, 65535, (100, 100), dtype=np.uint16)
    result = arcsinh_stretch(arr)
    assert result.dtype == np.uint8
    assert result.min() >= 0
    assert result.max() <= 255


def test_arcsinh_stretch_dark_image_not_clipped():
    """Very dark images should still produce non-zero output."""
    arr = np.ones((100, 100), dtype=np.float32) * 10
    result = arcsinh_stretch(arr)
    assert result.max() > 0


def test_preprocess_image_returns_pil():
    """preprocess_image should return a PIL RGB image."""
    img = Image.new("RGB", (640, 640), color=(20, 20, 30))
    result = preprocess_image(img)
    assert isinstance(result, Image.Image)
    assert result.mode == "RGB"


def test_preprocess_image_preserves_content():
    """Non-blank image should not become blank after preprocessing."""
    arr = np.random.randint(10, 200, (640, 640, 3), dtype=np.uint8)
    img = Image.fromarray(arr, mode="RGB")
    result = preprocess_image(img)
    result_arr = np.array(result)
    assert result_arr.mean() > 0
