from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
FINETUNED_MODEL_DIR = ARTIFACTS_DIR / "finetuned_model"

RAW_DATA_GLOB = "Youtube*.csv"
CONTENT_COLUMN = "content"
TARGET_COLUMN = "class"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
MLFLOW_EXPERIMENT_SERVING = "youtube-spam-serving"
MLFLOW_EXPERIMENT_FINETUNING = "youtube-spam-finetuning"
REGISTERED_MODEL_NAME = "youtube_spam_classifier"
SERVING_MODEL_URI = os.getenv("SERVING_MODEL_URI", "")
SERVING_MODEL_FALLBACK_TO_HF = os.getenv("SERVING_MODEL_FALLBACK_TO_HF", "true").lower() == "true"

HF_MODEL_NAME = "mrm8488/bert-tiny-finetuned-sms-spam-detection"
SPAM_THRESHOLD = 0.50
TEST_SIZE = 0.2
FINETUNING_VALIDATION_SIZE = 0.15
RANDOM_SEED = 42

MIN_CONTENT_CHARS = 3
MAX_CONTENT_CHARS = 1000
MAX_URL_RATIO = 0.8

MAX_EMOJI_RATIO = 0.15
YOUTUBE_CTA_MAX_RATIO = 0.20

FINETUNE_NUM_EPOCHS = 3
FINETUNE_BATCH_SIZE = 16
FINETUNE_LEARNING_RATE = 2e-5
FINETUNE_MAX_LENGTH = 128
