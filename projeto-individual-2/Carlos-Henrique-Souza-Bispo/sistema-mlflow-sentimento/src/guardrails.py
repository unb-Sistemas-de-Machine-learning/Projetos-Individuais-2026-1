import re
from typing import Tuple

import config


def validate_inference_text(text: str) -> Tuple[bool, str]:
    if not isinstance(text, str):
        return False, "A entrada deve ser uma string"

    candidate = text.strip()
    if not candidate:
        return False, "Texto vazio. Informe uma frase para classificacao"

    if len(candidate) < config.MIN_INPUT_CHARS:
        return False, f"Texto muito curto. Minimo: {config.MIN_INPUT_CHARS} caracteres"

    if len(candidate) > config.MAX_INPUT_CHARS:
        return False, f"Texto muito longo. Maximo: {config.MAX_INPUT_CHARS} caracteres"

    letters = re.findall(r"[A-Za-zÀ-ÿ]", candidate)
    textual_ratio = len(letters) / max(len(candidate), 1)
    if textual_ratio < 0.45:
        return False, "Entrada fora de escopo textual para este modelo"

    return True, "ok"


def validate_prediction_confidence(confidence: float) -> Tuple[bool, str]:
    if confidence < config.CONFIDENCE_THRESHOLD:
        return (
            False,
            "Confianca baixa para resposta segura. Recomendado revisao humana",
        )
    return True, "ok"
