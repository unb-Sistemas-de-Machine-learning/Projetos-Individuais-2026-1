import pandas as pd
from pathlib import Path
import json

RAW_DIR = Path("data/raw")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def main():
    # ajuste o split principal depois de inspecionar o que foi salvo
    df = pd.read_csv(RAW_DIR / "train.csv")

    report = {
        "n_rows": int(len(df)),
        "columns": df.columns.tolist(),
        "nulls_per_column": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }

    with open(REPORTS_DIR / "data_validation.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(report)

if __name__ == "__main__":
    main()