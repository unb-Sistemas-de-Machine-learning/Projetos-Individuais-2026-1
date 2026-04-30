from pathlib import Path
import pandas as pd 

LABEL_MAP = {"pos": 1, "neg": 0}

def load_imdb_split(
    dataset_dir: Path,
    split: str,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
     Load one split (train or test) of the Stanford aclImdb dataset
     into a DataFrame with columns: text, label.

     label: 1 = positive, 0 = negative
     """
    split_dir = Path(dataset_dir) / split
    if not split_dir.exists():
          raise FileNotFoundError(f"Split directory not found: {split_dir}")
     
    rows = []
    for label_name, label_value in LABEL_MAP.items():
          label_dir = split_dir / label_name 
          for txt_file in label_dir.glob("*.txt"):
               text = txt_file.read_text(encoding="utf-8")
               rows.append({"text": text, "label": label_value})
        
    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=random_seed).reset_index(drop=True)



def load_imdb(
    dataset_dir: str | Path,
    split: str = "test",
    sample_size: int | None = None,
    random_seed: int = 42,
) -> pd.DataFrame:
    df = load_imdb_split(Path(dataset_dir), split, random_seed=random_seed)
    if sample_size is not None and sample_size < len(df):
         df = df.sample(n=sample_size, random_state=random_seed).reset_index(drop=True)
    return df
