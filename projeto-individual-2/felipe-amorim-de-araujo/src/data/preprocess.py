# src/data/preprocess.py
import numpy as np
from PIL import Image


def arcsinh_stretch(data: np.ndarray, scale_percentile: float = 99.0) -> np.uint8:
    """
    Apply arcsinh stretch to compress astronomical image dynamic range.
    Standard technique: compresses bright stars while preserving faint sources.
    """
    data = data.astype(np.float32)
    p99 = np.percentile(data, scale_percentile)
    if p99 == 0:
        p99 = 1.0  # avoid division by zero on blank images
    stretched = np.arcsinh(data / p99)
    max_val = np.arcsinh(1.0)
    normalized = np.clip(stretched / max_val, 0, 1)
    return (normalized * 255).astype(np.uint8)


def preprocess_image(img: Image.Image) -> Image.Image:
    """
    Preprocess a PIL RGB image for YOLOS input:
    - Apply arcsinh stretch per channel to handle astronomical dynamic range
    - Return PIL RGB image (YolosImageProcessor handles final resize)
    """
    arr = np.array(img)  # shape: (H, W, 3)
    stretched = np.stack([arcsinh_stretch(arr[:, :, c]) for c in range(3)], axis=2)
    return Image.fromarray(stretched, mode="RGB")
