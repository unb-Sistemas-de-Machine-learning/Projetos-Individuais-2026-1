from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
MLRUNS_DIR = BASE_DIR / "mlruns"

TRACKING_URI = f"file:{MLRUNS_DIR.as_posix()}"
EXPERIMENT_NAME = "sentiment_distilbert_baseline"
REGISTERED_MODEL_NAME = "sentiment_distilbert_model"

DATASET_FILE = DATA_DIR / "imdb_sample.csv"
TEXT_COLUMN = "text"
LABEL_COLUMN = "label"

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
TASK_NAME = "text-classification"

TEST_SIZE = 0.20
RANDOM_STATE = 42
BATCH_SIZE = 16

MIN_INPUT_CHARS = 8
MAX_INPUT_CHARS = 300
CONFIDENCE_THRESHOLD = 0.65

ALLOWED_LABELS = {"positive", "negative"}
