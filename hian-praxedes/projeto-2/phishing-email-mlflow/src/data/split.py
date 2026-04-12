import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

PROCESSED_DIR = Path("data/processed")

def main():
    df = pd.read_csv(PROCESSED_DIR / "normalized.csv")

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["label"]
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["label"]
    )

    train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
    val_df.to_csv(PROCESSED_DIR / "val.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test.csv", index=False)

if __name__ == "__main__":
    main()