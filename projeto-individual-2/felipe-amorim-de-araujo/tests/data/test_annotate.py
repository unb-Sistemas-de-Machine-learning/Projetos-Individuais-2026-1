# tests/data/test_annotate.py
import math
from unittest.mock import patch
import pandas as pd
import pytest
from src.data.annotate import (
    radec_to_pixel,
    estimate_half_width_px,
    generate_annotations,
    ASTRO_LABEL_MAP,
    TRAINING_REGIONS,
)


def test_training_regions_not_empty():
    assert len(TRAINING_REGIONS) >= 20


def test_radec_to_pixel_center_maps_to_image_center():
    """Object at the field center should map to the image center."""
    px, py = radec_to_pixel(180.0, 0.0, center_ra=180.0, center_dec=0.0, width=640, height=640)
    assert abs(px - 320.0) < 0.01
    assert abs(py - 320.0) < 0.01


def test_radec_to_pixel_ra_increases_left():
    """RA increases eastward = leftward in SDSS images (decreasing x)."""
    px_east, _ = radec_to_pixel(180.1, 0.0, center_ra=180.0, center_dec=0.0)
    px_center, _ = radec_to_pixel(180.0, 0.0, center_ra=180.0, center_dec=0.0)
    assert px_east < px_center


def test_radec_to_pixel_dec_increases_up():
    """Dec increases northward = upward = decreasing y."""
    _, py_north = radec_to_pixel(180.0, 0.1, center_ra=180.0, center_dec=0.0)
    _, py_center = radec_to_pixel(180.0, 0.0, center_ra=180.0, center_dec=0.0)
    assert py_north < py_center


def test_estimate_half_width_point_source():
    """Stars/quasars have petroRad_r=0 → should return min_box_px floor."""
    hw = estimate_half_width_px(0.0)
    assert hw == 8.0


def test_estimate_half_width_extended_source():
    """Galaxy with large Petrosian radius should produce a larger box."""
    hw_small = estimate_half_width_px(2.0)   # small galaxy
    hw_large = estimate_half_width_px(10.0)  # large galaxy
    assert hw_large > hw_small


def test_estimate_half_width_capped():
    """Very large galaxy should be capped at max_box_px."""
    hw = estimate_half_width_px(1000.0, max_box_px=80.0)
    assert hw == 80.0


def test_estimate_half_width_nan():
    """NaN petroRad should fall back to min_box_px."""
    hw = estimate_half_width_px(float("nan"))
    assert hw == 8.0


def test_generate_annotations_returns_list():
    """With a mocked SDSS query, should return a list of annotation dicts."""
    fake_df = pd.DataFrame({
        "ra": [180.0],
        "dec": [0.0],
        "type": [3],           # galaxy
        "petroRad_r": [5.0],
        "psfMag_r": [19.0],
        "class_name": ["galaxy"],
    })
    with patch("src.data.annotate.query_region", return_value=fake_df):
        annotations = generate_annotations(180.0, 0.0)

    assert isinstance(annotations, list)
    assert len(annotations) == 1
    ann = annotations[0]
    assert "bbox" in ann
    assert "category_id" in ann
    assert ann["category_id"] == ASTRO_LABEL_MAP["galaxy"]
    cx, cy, bw, bh = ann["bbox"]
    assert 0.0 <= cx <= 1.0
    assert 0.0 <= cy <= 1.0
    assert bw > 0
    assert bh > 0


def test_generate_annotations_discards_out_of_frame():
    """Object whose pixel center falls outside the image should be dropped."""
    fake_df = pd.DataFrame({
        "ra": [200.0],   # far from center — will project outside 640x640
        "dec": [50.0],
        "type": [6],
        "petroRad_r": [0.0],
        "psfMag_r": [19.0],
        "class_name": ["star"],
    })
    with patch("src.data.annotate.query_region", return_value=fake_df):
        annotations = generate_annotations(180.0, 0.0)
    assert annotations == []


def test_generate_annotations_empty_region():
    """Empty SDSS result should return empty list."""
    with patch("src.data.annotate.query_region", return_value=pd.DataFrame()):
        annotations = generate_annotations(180.0, 0.0)
    assert annotations == []
