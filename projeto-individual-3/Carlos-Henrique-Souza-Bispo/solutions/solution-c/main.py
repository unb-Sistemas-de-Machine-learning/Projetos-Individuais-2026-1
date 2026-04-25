import json
import re
import sys
from typing import Any, Dict, List, Tuple


CATEGORY_RULES = {
    "suporte_tecnico": {
        "keywords": ["acesso", "acessar", "login", "senha", "portal", "moodle", "erro", "sistema"],
        "owner": "time_suporte",
        "sla_minutes": 60,
        "requires_ra": False,
    },
    "financeiro": {
        "keywords": ["boleto", "mensalidade", "pagamento", "fatura", "desconto", "parcela"],
        "owner": "time_financeiro",
        "sla_minutes": 120,
        "requires_ra": True,
    },
    "secretaria_academica": {
        "keywords": ["historico", "declaracao", "atestado", "documento", "matricula", "trancamento"],
        "owner": "time_secretaria",
        "sla_minutes": 240,
        "requires_ra": True,
    },
    "estagio_tcc": {
        "keywords": ["estagio", "tcc", "orientador", "banca", "monografia"],
        "owner": "time_coordenacao",
        "sla_minutes": 360,
        "requires_ra": False,
    },
}

HIGH_URGENCY_TERMS = ["urgente", "hoje", "imediato", "prazo", "bloqueado"]
MEDIUM_URGENCY_TERMS = ["amanha", "semana", "rapido"]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _classify_category(normalized: str) -> Tuple[str, float, Dict[str, int], bool]:
    scores: Dict[str, int] = {}

    for category, config in CATEGORY_RULES.items():
        score = sum(1 for keyword in config["keywords"] if keyword in normalized)
        scores[category] = score

    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_category, best_score = sorted_scores[0]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
    ambiguous = best_score > 0 and best_score == second_score

    if best_score == 0:
        return "indefinido", 0.45, scores, False

    confidence = 0.60 + min(best_score, 4) * 0.09
    if ambiguous:
        confidence -= 0.15

    return best_category, round(min(confidence, 0.94), 2), scores, ambiguous


def _estimate_urgency(normalized: str) -> str:
    if any(term in normalized for term in HIGH_URGENCY_TERMS):
        return "alta"
    if any(term in normalized for term in MEDIUM_URGENCY_TERMS):
        return "media"
    return "baixa"


def _extract_entities(original_message: str, normalized: str) -> Dict[str, Any]:
    ra_match = re.search(r"\b\d{6,10}\b", original_message)
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", original_message)

    return {
        "ra": ra_match.group(0) if ra_match else None,
        "email": email_match.group(0) if email_match else None,
        "has_deadline": any(term in normalized for term in ["prazo", "hoje", "amanha"]),
    }


def _validate(category: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields: List[str] = []

    if category in CATEGORY_RULES and CATEGORY_RULES[category]["requires_ra"] and not entities["ra"]:
        missing_fields.append("ra")

    return {
        "is_valid": category != "indefinido" and not missing_fields,
        "missing_fields": missing_fields,
    }


def _decide(category: str, urgency: str, confidence: float, validation: Dict[str, Any]) -> Dict[str, Any]:
    if category != "indefinido" and validation["missing_fields"]:
        return {
            "next_step": "solicitar_dados",
            "owner": "bot_followup",
            "sla_minutes": 10,
        }

    if category == "indefinido" or confidence < 0.70:
        return {
            "next_step": "escalar_humano",
            "owner": "analista_n1",
            "sla_minutes": 30,
        }

    base_sla = CATEGORY_RULES[category]["sla_minutes"]
    owner = CATEGORY_RULES[category]["owner"]

    if urgency == "alta":
        return {
            "next_step": "notificar_plantao",
            "owner": owner,
            "sla_minutes": min(base_sla, 30),
        }

    return {
        "next_step": "executar_fluxo_padrao",
        "owner": owner,
        "sla_minutes": base_sla,
    }


def process_request(message: str) -> Dict[str, Any]:
    normalized = _normalize(message)

    category, confidence, category_scores, ambiguous = _classify_category(normalized)
    urgency = _estimate_urgency(normalized)
    entities = _extract_entities(message, normalized)
    validation = _validate(category, entities)
    decision = _decide(category, urgency, confidence, validation)

    trace = [
        "Entrada normalizada",
        f"Categoria estimada: {category}",
        f"Urgencia: {urgency}",
        f"Confianca: {confidence}",
        f"Ambiguidade: {'sim' if ambiguous else 'nao'}",
        f"Campos faltantes: {', '.join(validation['missing_fields']) if validation['missing_fields'] else 'nenhum'}",
        f"Decisao final: {decision['next_step']}",
    ]

    return {
        "solution": "C",
        "classification": {
            "category": category,
            "urgency": urgency,
            "confidence": confidence,
            "scores": category_scores,
            "ambiguous": ambiguous,
        },
        "entities": entities,
        "validation": validation,
        "decision": decision,
        "trace": trace,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python main.py \"mensagem\"")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    print(json.dumps(process_request(message), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
