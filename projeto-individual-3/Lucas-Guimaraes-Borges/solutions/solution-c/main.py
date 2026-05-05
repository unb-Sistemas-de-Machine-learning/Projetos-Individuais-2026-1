import json
import re
import sys
from typing import Any, Dict, List, Tuple


RULES = {
    "suporte tecnico": ["erro", "api", "integracao", "webhook", "login", "acesso", "500"],
    "suporte geral": ["duvida", "como usar", "onboarding", "funcionalidade"],
    "financeiro": ["cobranca", "pagamento", "fatura", "reembolso", "plano"],
    "bug no sistema": ["bug", "quebrado", "nao funciona", "comportamento inesperado"],
    "feedback de melhorias": ["sugestao", "melhoria", "ideia", "feature"],
    "pedir cupom de afiliado": ["cupom", "afiliado", "desconto", "parceria"],
    "cancelamento": ["cancelamento", "cancelar", "encerrar conta"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _classify(text: str) -> Tuple[str, float]:
    if any(k in text for k in RULES["cancelamento"]):
        return "cancelamento", 0.9

    best_category = "outros"
    best_hits = 0
    for category, keywords in RULES.items():
        if category == "cancelamento":
            continue
        hits = sum(1 for k in keywords if k in text)
        if hits > best_hits:
            best_hits = hits
            best_category = category

    if best_hits == 0:
        return "outros", 0.48
    return best_category, min(0.58 + best_hits * 0.09, 0.94)


def _urgency(category: str, text: str) -> int:
    if category == "pedir cupom de afiliado":
        return 5
    if category == "cancelamento":
        return 7
    if "fora do ar" in text:
        return 10
    if any(k in text for k in ["urgente", "impacto", "nao consigo", "prejuizo"]):
        return 8
    if category == "financeiro":
        return 7
    return 4


def process_email(subject: str, content: str) -> Dict[str, Any]:
    text = _normalize(f"{subject} {content}")
    category, confidence = _classify(text)
    urgency = _urgency(category, text)

    summary_source = content.strip() if content.strip() else subject.strip()
    summary = summary_source[:160]
    if len(summary) < 15:
        summary = f"Solicitacao relacionada a {category}."

    decision = "rotear_automaticamente"
    if confidence < 0.65 or category == "outros":
        decision = "escalar_humano"

    return {
        "output": {"categoria": category, "urgencia": urgency, "resumo": summary},
        "meta": {"confidence": round(confidence, 2), "decision": decision},
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python main.py '<assunto>' '<conteudo>'")
        sys.exit(1)
    print(json.dumps(process_email(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=2))
