from datasets import load_dataset
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def main():
    ds = load_dataset("zefang-liu/phishing-email-dataset")

    # Não assuma os nomes dos splits/colunas sem inspecionar
    for split_name in ds.keys():
        df = ds[split_name].to_pandas()
        df.to_csv(RAW_DIR / f"{split_name}.csv", index=False)

    manifest = {
        "dataset_name": "zefang-liu/phishing-email-dataset",
        "downloaded_at": datetime.utcnow().isoformat(),
        "source": "Hugging Face",
        "notes": "Local raw copy created from datasets.load_dataset()"
    }

    with open(RAW_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()