import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


KB_PATH = Path(__file__).with_name("knowledge_base.json")


def _tokenize(text: str) -> Set[str]:
    return set(re.findall(r"[a-z0-9]{2,}", text.lower()))


def _load_kb() -> List[Dict[str, Any]]:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


def classify_email(subject: str, content: str) -> Dict[str, Any]:
    tokens = _tokenize(f"{subject} {content}")
    best_entry = None
    best_score: Tuple[int, int] = (-1, 0)

    for entry in _load_kb():
        keys = set(entry["keywords"])
        hits = len(tokens.intersection(keys))
        score = (hits, len(keys))
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry is None or best_score[0] == 0:
        categoria = "outros"
        urgencia = 4
        resumo = "Email sem sinais suficientes para classificacao automatica."
        confidence = 0.45
    else:
        categoria = best_entry["categoria"]
        confidence = min(0.60 + best_score[0] * 0.08, 0.95)
        if categoria == "cancelamento":
            urgencia = 7
        elif categoria == "financeiro":
            urgencia = 7
        else:
            urgencia = 8 if "urgente" in tokens else 6
        resumo = best_entry["resposta_padrao"]

    return {
        "categoria": categoria,
        "urgencia": urgencia,
        "resumo": resumo,
        "confidence": round(confidence, 2),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python main.py '<assunto>' '<conteudo>'")
        sys.exit(1)
    print(json.dumps(classify_email(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=2))
