import re
from dataclasses import dataclass

from src.config import (
    MAX_CONTENT_CHARS,
    MAX_EMOJI_RATIO,
    MAX_URL_RATIO,
    MIN_CONTENT_CHARS,
    YOUTUBE_CTA_MAX_RATIO,
)

URL_REGEX = re.compile(r"https?://|www\.", flags=re.IGNORECASE)
ALPHA_REGEX = re.compile(r"[a-zA-Z]")

YOUTUBE_CTA_KEYWORDS = {
    "subscribe",
    "suscribe",
    "suscribirse",
    "subscribe now",
    "check out",
    "check my",
    "check it",
    "like this",
    "hit like",
    "please like",
    "please subscribe",
    "visit my",
    "visit me",
    "follow me",
    "click here",
    "watch my",
    "channel",
    "my video",
    "my channel",
}

SPAM_INDICATORS = {
    "make money",
    "earn money",
    "cash now",
    "free money",
    "click here",
    "limited time",
    "act now",
    "offer",
    "deal",
    "discount",
}

EMOJI_REGEX = re.compile(r"[\U0001F300-\U0001F9FF]|[\u2600-\u27BF]|[\u2700-\u27BF]")


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str


def _count_cta_keywords(text):
    tokens = text.lower().split()
    if not tokens:
        return 0.0

    cta_count = 0
    for keyword in YOUTUBE_CTA_KEYWORDS:
        cta_count += text.lower().count(keyword)

    return cta_count / len(tokens)


def _count_emoji_ratio(text):
    total_chars = len(text)
    if total_chars == 0:
        return 0.0

    emoji_count = len(EMOJI_REGEX.findall(text))
    return emoji_count / total_chars


def _has_spam_indicators(text):
    text_lower = text.lower()
    for indicator in SPAM_INDICATORS:
        if indicator in text_lower:
            return True
    return False


def _has_excessive_repetition(text):
    tokens = text.split()

    word_counts = {}
    for token in tokens:
        word_counts[token.lower()] = word_counts.get(token.lower(), 0) + 1

    max_word_count = max(word_counts.values()) if word_counts else 0
    word_repetition_ratio = max_word_count / len(tokens) if tokens else 0
    has_word_repetition = max_word_count >= 2 and word_repetition_ratio > 0.3

    char_repetition = re.search(r"([a-zA-Z0-9])\1{3,}", text)

    return has_word_repetition or bool(char_repetition)


def _has_excessive_caps(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False

    caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return caps_ratio > 0.7


def validate_comment(text):
    if text is None:
        return GuardrailResult(False, "Conteudo ausente")

    normalized = str(text).strip()

    if len(normalized) < MIN_CONTENT_CHARS:
        return GuardrailResult(False, "Texto muito curto para inferencia")

    if len(normalized) > MAX_CONTENT_CHARS:
        return GuardrailResult(False, "Texto muito longo para inferencia")

    if not ALPHA_REGEX.search(normalized):
        return GuardrailResult(False, "Texto sem caracteres alfabeticos")

    tokens = normalized.split()
    if tokens:
        url_tokens = sum(1 for token in tokens if URL_REGEX.search(token))
        url_ratio = url_tokens / len(tokens)
        if url_ratio > MAX_URL_RATIO:
            return GuardrailResult(False, "Predominancia de links")

    if _has_spam_indicators(normalized):
        return GuardrailResult(False, "Indicadores de spam detectados")

    if _has_excessive_repetition(normalized):
        return GuardrailResult(False, "Repetição excessiva detectada")

    if _has_excessive_caps(normalized):
        return GuardrailResult(False, "Caps lock excessivo")

    emoji_ratio = _count_emoji_ratio(normalized)
    if emoji_ratio > MAX_EMOJI_RATIO:
        return GuardrailResult(False, "Emojis excessivos")

    cta_ratio = _count_cta_keywords(normalized)
    if cta_ratio > YOUTUBE_CTA_MAX_RATIO:
        return GuardrailResult(False, "Call-to-action excessivo detectado")

    return GuardrailResult(True, "ok")
