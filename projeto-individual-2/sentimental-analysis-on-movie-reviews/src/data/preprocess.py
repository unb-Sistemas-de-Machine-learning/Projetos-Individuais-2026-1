"""Text preprocessing for IMDb reviews.

Contract:
    Input:  pandas.DataFrame with columns ['text', 'label'].
    Output: pandas.DataFrame with the same shape, where the 'text' column has
            HTML <br /> tags stripped and internal whitespace normalized.
            The input DataFrame is not mutated.
"""

import re

import pandas as pd

# Semantic version of the preprocessing logic. Bump this whenever `clean_text`
# changes in a way that could affect model inputs (new rules, different regex,
# etc.). Logged as an MLflow param so runs using different preprocessing are
# never silently compared as if they were equivalent.
PREPROCESS_VERSION = "v1"

_BR_TAG_RE = re.compile(r"<br\s*/?>", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Strip HTML <br /> tags and collapse whitespace runs into single spaces."""
    text = _BR_TAG_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with the text column cleaned. Does not mutate input."""
    out = df.copy()
    out["text"] = out["text"].map(clean_text)
    return out
