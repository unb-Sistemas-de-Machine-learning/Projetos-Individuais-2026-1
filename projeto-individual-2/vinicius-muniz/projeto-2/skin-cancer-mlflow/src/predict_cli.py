"""CLI de inferência: recebe caminho de imagem e retorna predição."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from PIL import Image
from .config import load_config, project_root
from .guardrails import validate_file, check_input, apply_confidence_guard, DISCLAIMER
from .model import load_local_model, _aggregate_binary
import torch


def predict(image_path: Path) -> dict:
    cfg = load_config()
    err = validate_file(image_path, cfg["guardrails"]["max_image_mb"], cfg["guardrails"]["allowed_formats"])
    if err:
        return {"decision": "rejected", "reason": err, "disclaimer": DISCLAIMER}
    img = Image.open(image_path).convert("RGB")
    guard = check_input(img, cfg["guardrails"])
    if not guard.allowed:
        return {
            "decision": "rejected",
            "reason": guard.reason,
            "skin_tone_ita": guard.skin_tone_ita,
            "disclaimer": DISCLAIMER,
        }
    processor, model = load_local_model(cfg)
    with torch.no_grad():
        inputs = processor(images=img, return_tensors="pt")
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
    fine = {model.config.id2label[i]: float(p) for i, p in enumerate(probs)}
    binary = _aggregate_binary(fine, cfg["model"]["label_map"])
    result = apply_confidence_guard(binary, cfg["guardrails"]["min_confidence"])
    result["skin_tone_ita"] = guard.skin_tone_ita
    result["fine_probabilities"] = fine
    result["disclaimer"] = DISCLAIMER
    return result


def _format_human(r: dict) -> str:
    d = r["decision"]
    if d == "rejected":
        return f"REJEITADO: {r.get('reason')}\n\n{r['disclaimer']}"
    if d == "uncertain":
        conf = r.get("confidence") or 0
        return (
            f"SEM CONFIANÇA SUFICIENTE (maior probabilidade: {conf:.1%}).\n"
            "Recomenda-se avaliação médica presencial.\n\n"
            f"{r['disclaimer']}"
        )
    label = r["label"].upper()
    conf = r["confidence"]
    word = "MALIGNA (possível câncer)" if label == "MALIGNANT" else "BENIGNA"
    return f"Lesão classificada como {word}.\nConfiança: {conf:.1%}.\n\n{r['disclaimer']}"


def main():
    ap = argparse.ArgumentParser(description="Classifica lesão de pele (benign/malignant).")
    ap.add_argument("image", type=Path)
    ap.add_argument("--json", action="store_true", help="Saída JSON detalhada.")
    args = ap.parse_args()
    if not args.image.exists():
        print(f"Arquivo não encontrado: {args.image}", file=sys.stderr)
        sys.exit(1)
    result = predict(args.image)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_format_human(result))


if __name__ == "__main__":
    main()
