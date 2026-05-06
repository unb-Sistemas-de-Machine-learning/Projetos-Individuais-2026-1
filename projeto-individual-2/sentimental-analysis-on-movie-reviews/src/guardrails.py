"""Input guardrails for user-facing sentiment inference."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from langdetect import DetectorFactory, LangDetectException, detect

from src.model.loader import DEFAULT_MAX_LENGTH

DetectorFactory.seed = 0

MIN_REVIEW_WORDS = 5
MAX_REVIEW_TOKENS = DEFAULT_MAX_LENGTH

_WORD_RE = re.compile(r"\b\w+\b")


class TokenizerLike(Protocol):
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        """Tokenizer protocol used by the max-token guardrail."""


@dataclass(frozen=True)
class GuardrailViolation(Exception):
    """Raised when input should not be sent to the model."""

    message: str
    code: str

    def __str__(self) -> str:
        return self.message


def count_words(text: str) -> int:
    """Return a simple word count for validation, not linguistic analysis."""
    return len(_WORD_RE.findall(text))


def validate_min_length(text: str, min_words: int = MIN_REVIEW_WORDS) -> None:
    """Reject empty or very short reviews."""
    if not text.strip():
        raise GuardrailViolation(
            "Review text is empty. Provide an English movie review.",
            "empty_review",
        )

    if count_words(text) < min_words:
        raise GuardrailViolation(
            f"Review is too short to classify reliably. Provide at least {min_words} words.",
            "review_too_short",
        )


def validate_language(text: str, expected_language: str = "en") -> None:
    """Reject reviews that are not detected as English."""
    try:
        detected_language = detect(text)
    except LangDetectException as exc:
        raise GuardrailViolation(
            "Could not detect review language. Provide an English movie review.",
            "language_detection_failed",
        ) from exc

    if detected_language != expected_language:
        raise GuardrailViolation(
            "Review appears to be non-English. This model only supports English movie reviews.",
            "non_english_review",
        )


def validate_max_tokens(
    text: str,
    tokenizer: TokenizerLike,
    max_tokens: int = MAX_REVIEW_TOKENS,
) -> None:
    """Reject inputs that exceed the model token limit before truncation."""
    token_count = len(tokenizer.encode(text, add_special_tokens=True))

    if token_count > max_tokens:
        raise GuardrailViolation(
            f"Review is longer than the {max_tokens}-token model limit.",
            "review_too_long",
        )


def validate_review(
    text: str,
    tokenizer: TokenizerLike,
    min_words: int = MIN_REVIEW_WORDS,
    max_tokens: int = MAX_REVIEW_TOKENS,
) -> None:
    """Run all current review guardrails in a stable order."""
    validate_min_length(text, min_words=min_words)
    validate_language(text)
    validate_max_tokens(text, tokenizer=tokenizer, max_tokens=max_tokens)
