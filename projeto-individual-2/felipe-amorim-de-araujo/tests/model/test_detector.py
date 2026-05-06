# tests/model/test_detector.py
from unittest.mock import patch, MagicMock
import torch
import pytest
from PIL import Image
import numpy as np
from src.model.detector import SpaceDetector


@pytest.fixture
def mock_detector():
    """Detector with mocked HuggingFace model to avoid download in tests."""
    with patch("src.model.detector.YolosForObjectDetection.from_pretrained") as mock_model, \
         patch("src.model.detector.YolosImageProcessor.from_pretrained") as mock_proc:

        # Mock processor: returns a dict with input_ids tensor
        mock_proc.return_value.return_value = {
            "pixel_values": torch.zeros(1, 3, 512, 512)
        }
        mock_proc.return_value.post_process_object_detection.return_value = [
            {
                "scores": torch.tensor([0.85, 0.3]),
                "labels": torch.tensor([0, 1]),
                "boxes": torch.tensor([[10., 10., 50., 50.], [60., 60., 80., 80.]]),
            }
        ]

        mock_model.return_value.return_value = MagicMock()
        mock_model.return_value.config.id2label = {0: "cat"}  # dummy COCO label

        detector = SpaceDetector()
        yield detector


def test_detector_initializes(mock_detector):
    assert mock_detector is not None


def test_detect_returns_list(mock_detector):
    img = Image.fromarray(np.random.randint(10, 200, (640, 640, 3), dtype=np.uint8))
    result = mock_detector.detect(img)
    assert isinstance(result, list)


def test_detect_result_has_expected_keys(mock_detector):
    img = Image.fromarray(np.random.randint(10, 200, (640, 640, 3), dtype=np.uint8))
    result = mock_detector.detect(img)
    for det in result:
        assert "box" in det
        assert "score" in det
        assert "label" not in det  # we strip class labels in base version
