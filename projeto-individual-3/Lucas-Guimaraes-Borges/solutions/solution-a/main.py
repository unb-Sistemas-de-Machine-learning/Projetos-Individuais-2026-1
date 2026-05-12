import json
import re
import sys
from typing import Any, Dict


CATEGORIES = {
    "suporte tecnico": ["erro", "api", "integracao", "webhook", "login", "acesso", "falha", "500"],
    "suporte geral": ["como usar", "duvida", "onboarding", "ajuda", "configurar"],
    "financeiro": ["cobranca", "pagamento", "fatura", "reembolso", "plano", "mensalidade"],
    "bug no sistema": ["bug", "quebrado", "nao funciona", "comportamento inesperado"],
    "feedback de melhorias": ["sugestao", "melhoria", "funcionalidade", "ideia"],
    "pedir cupom de afiliado": ["cupom", "desconto", "afiliado", "parceria"],
    "cancelamento": ["cancelar", "cancelamento", "encerrar conta"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def classify_email(subject: str, content: str) -> Dict[str, Any]:
    text = _normalize(f"{subject} {content}")

    if any(k in text for k in CATEGORIES["cancelamento"]):
        category = "cancelamento"
    else:
        category = "outros"
        best = 0
        for name, keywords in CATEGORIES.items():
            if name == "cancelamento":
                continue
            score = sum(1 for k in keywords if k in text)
            if score > best:
                best = score
                category = name

    urgency = 4
    if "fora do ar" in text:
        urgency = 10
    elif any(k in text for k in ["urgente", "bloqueado", "nao consigo"]):
        urgency = 8
    elif any(k in text for k in ["reembolso", "cobranca indevida", "pagamento"]):
        urgency = max(urgency, 7)

    if category == "pedir cupom de afiliado":
        urgency = 5
    if category == "cancelamento":
        urgency = 7

    summary = (content.strip() or subject.strip())[:140]
    if len(summary) < 20:
        summary = f"Cliente solicita atendimento sobre {category}."

    return {"categoria": category, "urgencia": int(max(0, min(10, urgency))), "resumo": summary}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python main.py '<assunto>' '<conteudo>'")
        sys.exit(1)
    print(json.dumps(classify_email(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=2))
