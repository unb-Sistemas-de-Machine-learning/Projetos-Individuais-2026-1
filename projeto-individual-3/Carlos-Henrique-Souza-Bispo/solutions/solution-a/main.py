import json
import re
import sys
from typing import Any, Dict, List


CATEGORY_KEYWORDS = {
    "suporte_tecnico": ["acesso", "login", "senha", "portal", "moodle", "erro", "sistema"],
    "financeiro": ["boleto", "mensalidade", "pagamento", "fatura", "desconto", "parcela"],
    "secretaria_academica": [
        "historico",
        "declaracao",
        "atestado",
        "documento",
        "matricula",
        "rematricula",
        "trancamento",
    ],
    "estagio_tcc": ["estagio", "tcc", "orientador", "banca", "monografia"],
}

HIGH_URGENCY_TERMS = ["urgente", "hoje", "imediato", "prazo", "nao consigo", "bloqueado"]
MEDIUM_URGENCY_TERMS = ["amanha", "essa semana", "quando puder"]

ROUTE_BY_CATEGORY = {
    "suporte_tecnico": "fila_suporte",
    "financeiro": "fila_financeiro",
    "secretaria_academica": "fila_secretaria",
    "estagio_tcc": "fila_coordenacao",
    "indefinido": "triagem_humana",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _find_keywords(text: str) -> Dict[str, List[str]]:
    matches: Dict[str, List[str]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hit_list = [keyword for keyword in keywords if keyword in text]
        if hit_list:
            matches[category] = hit_list
    return matches


def _estimate_urgency(text: str) -> str:
    if any(term in text for term in HIGH_URGENCY_TERMS):
        return "alta"
    if any(term in text for term in MEDIUM_URGENCY_TERMS):
        return "media"
    return "baixa"


def classify_request(message: str) -> Dict[str, Any]:
    normalized = _normalize(message)
    keyword_hits = _find_keywords(normalized)
    urgency = _estimate_urgency(normalized)

    if keyword_hits:
        category, matched_terms = max(keyword_hits.items(), key=lambda item: len(item[1]))
    else:
        category, matched_terms = "indefinido", []

    confidence = 0.45 + min(len(matched_terms), 4) * 0.10
    if urgency == "alta":
        confidence += 0.10
    if category == "indefinido":
        confidence = 0.40

    return {
        "solution": "A",
        "category": category,
        "urgency": urgency,
        "confidence": round(min(confidence, 0.92), 2),
        "extracted": {
            "keywords": matched_terms,
            "main_request": message.strip()[:160],
        },
        "route": ROUTE_BY_CATEGORY[category],
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python main.py \"mensagem\"")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    print(json.dumps(classify_request(message), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
