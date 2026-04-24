import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(RAW_DIR / "train.csv")

    # ajuste estes nomes conforme o CSV real
    df = df.rename(columns={
        "Email Text": "text",
        "Email Type": "label"
    })

    # exemplo de normalizacao de labels
    df["label"] = df["label"].map({
        "Safe Email": 0,
        "Phishing Email": 1
    })

    df = df[["text", "label"]].dropna()
    df = df.drop_duplicates()

    df.to_csv(PROCESSED_DIR / "normalized.csv", index=False)

if __name__ == "__main__":
    main()