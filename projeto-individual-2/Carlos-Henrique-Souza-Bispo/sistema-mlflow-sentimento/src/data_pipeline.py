import re
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

import config


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def preprocess_text(text: str) -> str:
    return _normalize_whitespace(text)


def load_dataset(csv_path: Path = config.DATASET_FILE) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo de dataset nao encontrado: {csv_path}")

    df = pd.read_csv(csv_path)

    required_columns = {config.TEXT_COLUMN, config.LABEL_COLUMN}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset invalido. Colunas ausentes: {missing}")

    df = df[[config.TEXT_COLUMN, config.LABEL_COLUMN]].copy()
    df[config.TEXT_COLUMN] = df[config.TEXT_COLUMN].astype(str).map(preprocess_text)
    df[config.LABEL_COLUMN] = df[config.LABEL_COLUMN].astype(str).str.strip().str.lower()

    invalid_labels = sorted(set(df[config.LABEL_COLUMN]) - config.ALLOWED_LABELS)
    if invalid_labels:
        labels = ", ".join(invalid_labels)
        raise ValueError(f"Labels fora do escopo permitido: {labels}")

    if df.empty:
        raise ValueError("Dataset vazio apos carregamento")

    return df


def split_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df, test_df = train_test_split(
        df,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=df[config.LABEL_COLUMN],
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)
