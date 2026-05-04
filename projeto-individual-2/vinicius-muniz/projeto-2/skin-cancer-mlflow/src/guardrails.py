"""Guardrails: restringe uso indevido e explicita incertezas.

Escopo declarado:
- Modelo treinado apenas com lesões em pele clara (dataset ISIC).
- Não deve ser usado como diagnóstico médico.
- Retorna "incerto" abaixo do threshold de confiança.
- Rejeita imagens de pele escura via ITA (Individual Typology Angle).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import math
import numpy as np
from PIL import Image


DISCLAIMER = (
    "Este sistema é uma ferramenta educacional. Não substitui avaliação médica. "
    "Treinado apenas com imagens de pele clara (ISIC); predições em pele escura "
    "não são suportadas."
)


@dataclass
class GuardrailResult:
    allowed: bool
    reason: Optional[str]
    skin_tone_ita: Optional[float]
    details: dict


def _rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    rgb = rgb.astype(np.float64) / 255.0
    mask = rgb > 0.04045
    rgb_lin = np.where(mask, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    m = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = rgb_lin @ m.T
    ref = np.array([0.95047, 1.0, 1.08883])
    xyz = xyz / ref
    mask2 = xyz > 0.008856
    f = np.where(mask2, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, b], axis=-1)


def compute_ita(image: Image.Image) -> float:
    """Proxy de tom de pele via luminosidade L* (CIE Lab).

    ITA clássico é instável em dermatoscopia (iluminação polarizada azulada
    satura o canal b*). Usa-se L* da borda (pele saudável) como proxy:
    L* ≳ 55 → pele clara (Fitzpatrick I–III).
    """
    arr = np.asarray(image.convert("RGB"))
    h, w, _ = arr.shape
    border = 0.12
    by, bx = int(h * border), int(w * border)
    mask_img = np.zeros((h, w), dtype=bool)
    mask_img[:by, :] = True
    mask_img[-by:, :] = True
    mask_img[:, :bx] = True
    mask_img[:, -bx:] = True
    patch = arr[mask_img]
    gray = patch.mean(axis=1)
    keep = (gray > 40) & (gray < 245)
    if keep.sum() < 200:
        return float("nan")
    sample = patch[keep]
    lab = _rgb_to_lab(sample)
    return float(np.median(lab[:, 0]))


def validate_file(path: Path, max_mb: int, allowed_formats: list[str]) -> Optional[str]:
    if not path.exists():
        return "Arquivo inexistente."
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        return f"Arquivo excede {max_mb}MB."
    ext = path.suffix.lower().lstrip(".")
    if ext not in allowed_formats:
        return f"Formato {ext} não suportado."
    return None


def check_input(image: Image.Image, cfg_guard: dict) -> GuardrailResult:
    if not cfg_guard.get("skin_tone_check", True):
        return GuardrailResult(True, None, None, {})
    ita = compute_ita(image)
    details = {"ita": ita, "threshold": cfg_guard["skin_tone_ita_min"]}
    if math.isnan(ita):
        return GuardrailResult(False, "Pele não detectada com confiança.", ita, details)
    if ita < cfg_guard["skin_tone_ita_min"]:
        return GuardrailResult(
            False,
            "Imagem aparenta pele escura; modelo só valida pele clara.",
            ita,
            details,
        )
    return GuardrailResult(True, None, ita, details)


def apply_confidence_guard(probs: dict, min_conf: float) -> dict:
    top_label = max(probs, key=probs.get)
    top_p = probs[top_label]
    if top_p < min_conf:
        return {
            "decision": "uncertain",
            "label": None,
            "confidence": top_p,
            "message": (
                f"Confiança {top_p:.2%} abaixo de {min_conf:.0%}. "
                "Recomenda-se avaliação médica presencial."
            ),
            "probabilities": probs,
        }
    return {
        "decision": "classified",
        "label": top_label,
        "confidence": top_p,
        "message": DISCLAIMER,
        "probabilities": probs,
    }
