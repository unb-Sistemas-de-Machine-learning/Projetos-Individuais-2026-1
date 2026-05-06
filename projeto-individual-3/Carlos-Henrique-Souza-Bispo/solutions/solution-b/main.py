import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


KB_PATH = Path(__file__).with_name("knowledge_base.json")
HIGH_URGENCY_TERMS = {"urgente", "hoje", "imediato", "prazo", "bloqueado"}


def _load_knowledge_base() -> List[Dict[str, Any]]:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


def _tokenize(text: str) -> Set[str]:
    return set(re.findall(r"[a-z0-9]{2,}", text.lower()))


def _score_policy(tokens: Set[str], policy: Dict[str, Any]) -> Tuple[float, List[str]]:
    keywords = set(policy["keywords"])
    matched = sorted(tokens.intersection(keywords))
    score = len(matched) / max(len(keywords), 1)
    return score, matched


def classify_request(message: str) -> Dict[str, Any]:
    tokens = _tokenize(message)
    knowledge_base = _load_knowledge_base()

    scored = []
    for policy in knowledge_base:
        score, matched = _score_policy(tokens, policy)
        scored.append((score, matched, policy))

    top_score, top_matched, top_policy = max(scored, key=lambda item: item[0])

    urgency = "alta" if HIGH_URGENCY_TERMS.intersection(tokens) else "media"

    if top_score == 0:
        confidence = 0.48
        category = "indefinido"
        route = "revisao_humana"
        retrieval = {
            "policy_id": None,
            "title": None,
            "score": 0.0,
            "matched_keywords": [],
            "source": "knowledge_base.json",
        }
        response_template = "Nao foi possivel identificar politica aderente. Encaminhar para triagem humana."
        sla_hours = 2
    else:
        confidence = min(0.58 + top_score * 0.35 + (0.05 if "ra" in tokens else 0), 0.95)
        category = top_policy["category"]
        route = "resposta_automatica_com_base" if confidence >= 0.72 else "revisao_humana"
        retrieval = {
            "policy_id": top_policy["id"],
            "title": top_policy["title"],
            "score": round(top_score, 2),
            "matched_keywords": top_matched,
            "source": "knowledge_base.json",
        }
        response_template = top_policy["action_template"]
        sla_hours = top_policy["sla_hours"]

    return {
        "solution": "B",
        "category": category,
        "urgency": urgency,
        "confidence": round(confidence, 2),
        "retrieval": retrieval,
        "decision": {
            "route": route,
            "sla_hours": sla_hours,
        },
        "response_template": response_template,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python main.py \"mensagem\"")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    print(json.dumps(classify_request(message), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
