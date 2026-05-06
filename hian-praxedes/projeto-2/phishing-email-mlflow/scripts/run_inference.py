from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import mlflow
import mlflow.pyfunc


MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
MODEL_URI = "models:/phishing-email-detector/1"


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    model = mlflow.pyfunc.load_model(MODEL_URI)

    samples = [
        "Dear customer, your mailbox has exceeded its storage limit. Click here to keep your email active.",
        "Hello team, please find attached the updated meeting notes for tomorrow."
    ]

    for text in samples:
        prediction = model.predict(text)
        print("-" * 80)
        print("INPUT:")
        print(text)
        print("OUTPUT:")
        print(prediction)


if __name__ == "__main__":
    main()