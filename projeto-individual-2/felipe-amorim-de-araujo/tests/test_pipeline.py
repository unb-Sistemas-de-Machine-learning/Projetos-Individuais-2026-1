# tests/test_pipeline.py
from unittest.mock import patch, MagicMock
from pathlib import Path
import pytest
from src.pipeline import run_pipeline


@pytest.fixture
def pipeline_mocks(tmp_path):
    """Mock all external calls: SDSS, model download, MLflow."""
    from PIL import Image
    import numpy as np

    fake_img = Image.fromarray(np.random.randint(10, 200, (640, 640, 3), dtype=np.uint8))

    with patch("src.pipeline.build_dataset", return_value={"downloaded": 3, "skipped": 1}) as mock_ingest, \
         patch("src.pipeline.SpaceDetector") as mock_det_cls, \
         patch("src.pipeline.mlflow") as mock_mlflow, \
         patch("src.pipeline.Image.open", return_value=fake_img):

        mock_det = MagicMock()
        mock_det.detect.return_value = [{"box": [10, 10, 50, 50], "score": 0.75}]
        mock_det_cls.return_value = mock_det

        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        yield {
            "tmp_path": tmp_path,
            "mock_ingest": mock_ingest,
            "mock_mlflow": mock_mlflow,
        }


def test_pipeline_runs_without_error(pipeline_mocks):
    run_pipeline(
        data_dir=pipeline_mocks["tmp_path"],
        n_regions=3,
        confidence_threshold=0.4,
    )


def test_pipeline_calls_mlflow_log_params(pipeline_mocks):
    run_pipeline(
        data_dir=pipeline_mocks["tmp_path"],
        n_regions=3,
        confidence_threshold=0.4,
    )
    pipeline_mocks["mock_mlflow"].log_params.assert_called_once()


def test_pipeline_calls_mlflow_log_metrics(pipeline_mocks):
    run_pipeline(
        data_dir=pipeline_mocks["tmp_path"],
        n_regions=3,
        confidence_threshold=0.4,
    )
    assert pipeline_mocks["mock_mlflow"].log_metrics.call_count >= 2
