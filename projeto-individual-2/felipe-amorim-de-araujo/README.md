# Space Object Detection — ML Pipeline

End-to-end ML pipeline for detecting astronomical objects (stars, galaxies, quasars) in sky survey images using YOLOS-small (Vision Transformer) and MLflow for experiment tracking, model registry, and deployment.

## Setup

```bash
uv sync
```

## Run the inference pipeline

Downloads SDSS images and runs detection with the fine-tuned model:

```bash
uv run python -m src.pipeline \
  --n-regions 20 \
  --radius-deg 0.05 \
  --scale 0.2 \
  --confidence-threshold 0.6 \
  --nms-iou-threshold 0.5 \
  --data-dir data \
  --model-path data/finetune/checkpoints/best
```

## Run the fine-tuning pipeline

Downloads a larger annotated dataset and fine-tunes YOLOS-small on SDSS objects:

```bash
uv run python -m src.finetune_pipeline \
  --n-regions 150 \
  --epochs 50 \
  --freeze-epochs 10 \
  --batch-size 4 \
  --data-dir data/finetune
```

To skip the download if images are already present:

```bash
uv run python -m src.finetune_pipeline --skip-download --data-dir data/finetune
```

## View experiments

```bash
uv run mlflow ui --port 5000
```

## Serve the model

Check the latest registered version first:

```bash
uv run python -c "import mlflow; client = mlflow.tracking.MlflowClient(); versions = client.get_latest_versions('space-detector'); print(versions[-1].version)"
```

Then serve it (replace `N` with the version number):

```bash
uv run mlflow models serve -m "models:/space-detector/N" --port 5001 --no-conda
```

## Run inference against the endpoint

```bash
uv run python -m src.inference --image data/raw/field_0000.jpg
```

The endpoint accepts a `dataframe_records` payload with a `b64_image` column (base64-encoded JPEG). Guardrails, preprocessing, and post-processing all run inside the served model.

## Run tests

```bash
uv run pytest tests/ -v
```

## Pipeline parameters

### Inference pipeline (`src.pipeline`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--n-regions` | 20 | Number of sky regions to download from SDSS |
| `--radius-deg` | 0.05 | Search radius per region (degrees) |
| `--scale` | 0.2 | Image scale in arcsec/pixel |
| `--confidence-threshold` | 0.6 | Minimum detection confidence |
| `--nms-iou-threshold` | 0.5 | IoU threshold for non-maximum suppression |
| `--data-dir` | `data` | Directory for raw images and outputs |
| `--model-path` | `hustvl/yolos-small` | HuggingFace model name or local checkpoint path |

### Fine-tuning pipeline (`src.finetune_pipeline`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--n-regions` | 150 | Number of annotated regions to download |
| `--epochs` | 50 | Total training epochs |
| `--freeze-epochs` | 10 | Epochs with frozen backbone (head warm-up) |
| `--lr-head` | 1e-4 | Learning rate for detection head |
| `--lr-backbone` | 1e-5 | Learning rate for ViT backbone |
| `--weight-decay` | 1e-4 | AdamW weight decay |
| `--batch-size` | 4 | Training batch size |
| `--val-fraction` | 0.2 | Fraction of images held out for validation |
| `--base-model` | `hustvl/yolos-small` | Base HuggingFace model to fine-tune from |
| `--skip-download` | false | Skip SDSS download if annotations.json exists |

## Project structure

```
src/
├── pipeline.py              # Inference pipeline (ingest → detect → log → register)
├── finetune_pipeline.py     # Fine-tuning pipeline (annotate → train → register)
├── inference.py             # Client for the MLflow serving endpoint
├── data/
│   ├── ingest.py            # SDSS DR17 image download
│   ├── preprocess.py        # Arcsinh stretch preprocessing
│   ├── annotate.py          # Auto-labeling from SDSS catalog
│   └── dataset.py           # PyTorch Dataset + train/val split
└── model/
    ├── detector.py          # YOLOS-small wrapper
    ├── guardrails.py        # Input/output validation
    ├── pyfunc_model.py      # MLflow pyfunc serving wrapper
    └── train.py             # Two-phase fine-tuning loop
```
