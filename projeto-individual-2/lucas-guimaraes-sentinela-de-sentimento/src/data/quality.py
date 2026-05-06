"""Tratamento de qualidade dos dados: relatório antes da avaliação."""

from __future__ import annotations

from collections import Counter
from typing import Any

from datasets import Dataset


def dataset_quality_report(
    split: Dataset,
    text_column: str,
    label_column: str,
    max_examples: int = 5,
) -> dict[str, Any]:
    """
    Estatísticas simples: comprimento de texto, labels, exemplos de possíveis vazios.
    """
    lengths = [len(str(t)) for t in split[text_column]]
    labels = list(split[label_column])
    emptyish = sum(1 for t in split[text_column] if not str(t).strip())

    report: dict[str, Any] = {
        "n": len(split),
        "text_len_min": min(lengths) if lengths else 0,
        "text_len_max": max(lengths) if lengths else 0,
        "text_len_mean": sum(lengths) / len(lengths) if lengths else 0.0,
        "empty_or_blank": emptyish,
        "label_distribution": dict(Counter(labels)),
        "sample_texts": [str(split[text_column][i])[:200] for i in range(min(max_examples, len(split)))],
    }
    return report
