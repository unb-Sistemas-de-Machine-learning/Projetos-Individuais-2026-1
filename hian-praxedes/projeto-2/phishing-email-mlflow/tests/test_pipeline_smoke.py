import pandas as pd
from pathlib import Path


def test_test_csv_exists_and_has_required_columns():
    path = Path("data/processed/test.csv")
    assert path.exists()

    df = pd.read_csv(path)
    assert "text" in df.columns
    assert "label" in df.columns
    assert len(df) > 0