# tests/data/test_ingest.py
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
import pytest
from src.data.ingest import SAMPLE_REGIONS, build_dataset, download_cutout


def test_sample_regions_not_empty():
    assert len(SAMPLE_REGIONS) > 0
    for ra, dec in SAMPLE_REGIONS:
        assert 0 <= ra <= 360
        assert -90 <= dec <= 90


def test_download_cutout_creates_file(tmp_path):
    """Mock HTTP call — verify file is written."""
    from PIL import Image
    import io

    fake_img = Image.new("RGB", (640, 640), color=(10, 10, 10))
    buf = io.BytesIO()
    fake_img.save(buf, format="JPEG")
    buf.seek(0)

    mock_response = MagicMock()
    mock_response.content = buf.read()
    mock_response.raise_for_status = MagicMock()

    with patch("src.data.ingest.requests.get", return_value=mock_response):
        out = download_cutout(180.0, 0.0, tmp_path / "test.jpg")

    assert out.exists()
    assert out.suffix == ".jpg"


def test_build_dataset_skips_empty_regions(tmp_path):
    """If SDSS returns no objects, skip region gracefully."""
    with patch("src.data.ingest.query_region", return_value=pd.DataFrame()), \
         patch("src.data.ingest.download_cutout") as mock_dl:
        build_dataset(tmp_path, n_regions=2)
        mock_dl.assert_not_called()
