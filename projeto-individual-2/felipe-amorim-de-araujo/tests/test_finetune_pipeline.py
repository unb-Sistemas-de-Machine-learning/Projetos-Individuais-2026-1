# tests/test_finetune_pipeline.py
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from src.finetune_pipeline import run_finetune_pipeline


@pytest.fixture
def finetune_mocks(tmp_path):
    """Mock all external calls: SDSS, model download, training, MLflow."""
    annotations = [
        {
            "image_file": f"field_{i:04d}.jpg",
            "center_ra": 180.0,
            "center_dec": 0.0,
            "objects": [{"bbox": [0.5, 0.5, 0.1, 0.1], "category_id": 1}],
        }
        for i in range(5)
    ]
    annotations_path = tmp_path / "annotations.json"
    annotations_path.write_text(json.dumps(annotations))

    fake_checkpoint = tmp_path / "checkpoints" / "best"
    fake_checkpoint.mkdir(parents=True)

    with patch("src.finetune_pipeline.build_annotated_dataset",
               return_value={
                   "downloaded": 5,
                   "total_objects": 12,
                   "skipped_no_sdss_objects": 2,
                   "skipped_guardrail": 0,
                   "annotations_path": str(annotations_path),
               }) as mock_build, \
         patch("src.finetune_pipeline.finetune", return_value=fake_checkpoint) as mock_train, \
         patch("src.finetune_pipeline.mlflow") as mock_mlflow, \
         patch("src.finetune_pipeline.YolosForObjectDetection") as mock_model_cls:

        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)
        mock_model_cls.from_pretrained.return_value = MagicMock()

        yield {
            "tmp_path": tmp_path,
            "mock_build": mock_build,
            "mock_train": mock_train,
            "mock_mlflow": mock_mlflow,
            "fake_checkpoint": fake_checkpoint,
        }


def test_finetune_pipeline_runs(finetune_mocks):
    result = run_finetune_pipeline(
        data_dir=finetune_mocks["tmp_path"],
        n_regions=5,
        epochs=2,
        freeze_epochs=1,
    )
    assert result == finetune_mocks["fake_checkpoint"]


def test_finetune_pipeline_calls_build_dataset(finetune_mocks):
    run_finetune_pipeline(data_dir=finetune_mocks["tmp_path"], n_regions=5, epochs=2)
    finetune_mocks["mock_build"].assert_called_once()


def test_finetune_pipeline_calls_finetune(finetune_mocks):
    run_finetune_pipeline(data_dir=finetune_mocks["tmp_path"], n_regions=5, epochs=2)
    finetune_mocks["mock_train"].assert_called_once()


def test_finetune_pipeline_logs_params(finetune_mocks):
    run_finetune_pipeline(data_dir=finetune_mocks["tmp_path"], n_regions=5, epochs=2)
    finetune_mocks["mock_mlflow"].log_params.assert_called_once()


def test_finetune_pipeline_skip_download(finetune_mocks):
    """With skip_download=True and existing annotations, build_dataset should not be called."""
    run_finetune_pipeline(
        data_dir=finetune_mocks["tmp_path"],
        n_regions=5,
        epochs=2,
        skip_download=True,
    )
    finetune_mocks["mock_build"].assert_not_called()
