from pathlib import Path

import pandas as pd

from src.config import CONTENT_COLUMN, DATA_DIR, RAW_DATA_GLOB, TARGET_COLUMN, TEST_SIZE


EXPECTED_COLUMNS = {"comment_id", "author", "date", "content", "class"}


def load_raw_comments(data_dir=DATA_DIR):
    frames = []
    for csv_file in sorted(data_dir.glob(RAW_DATA_GLOB)):
        frame = pd.read_csv(csv_file)
        frame.columns = [column.lower() for column in frame.columns]
        missing_columns = EXPECTED_COLUMNS.difference(frame.columns)
        if missing_columns:
            raise ValueError(f"Arquivo {csv_file.name} sem colunas obrigatorias: {missing_columns}")

        frame["source_file"] = csv_file.name
        frame["row_order"] = range(len(frame))
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce", utc=True)
        frames.append(frame)

    if not frames:
        raise ValueError("Nenhum arquivo CSV encontrado na pasta data")

    dataset = pd.concat(frames, ignore_index=True)
    dataset[CONTENT_COLUMN] = dataset[CONTENT_COLUMN].fillna("").astype(str).str.strip()
    dataset[TARGET_COLUMN] = pd.to_numeric(dataset[TARGET_COLUMN], errors="coerce")

    dataset = dataset[dataset[TARGET_COLUMN].isin([0, 1])]
    dataset = dataset[dataset[CONTENT_COLUMN] != ""]

    dataset = dataset.drop_duplicates(subset=["comment_id", CONTENT_COLUMN])
    dataset[TARGET_COLUMN] = dataset[TARGET_COLUMN].astype(int)

    dataset = dataset.sort_values(["date", "source_file", "row_order"], na_position="last").reset_index(drop=True)
    return dataset


def temporal_split(dataset, test_size=TEST_SIZE):
    split_index = int(len(dataset) * (1 - test_size))
    train_df = dataset.iloc[:split_index].copy()
    test_df = dataset.iloc[split_index:].copy()
    return train_df, test_df


def data_quality_report(dataset):
    total_rows = int(len(dataset))
    missing_date = int(dataset["date"].isna().sum())
    duplicates = int(dataset.duplicated(subset=["comment_id", CONTENT_COLUMN]).sum())

    class_distribution = (
        dataset[TARGET_COLUMN]
        .value_counts(normalize=True)
        .sort_index()
        .to_dict()
    )

    return {
        "total_rows": total_rows,
        "missing_date_rows": missing_date,
        "duplicate_rows": duplicates,
        "class_ratio_ham_0": float(class_distribution.get(0, 0.0)),
        "class_ratio_spam_1": float(class_distribution.get(1, 0.0)),
    }

