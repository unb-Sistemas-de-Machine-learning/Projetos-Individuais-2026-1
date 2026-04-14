import re

def mask_pii(text: str) -> str:
    """
    Identifica e mascara padrões de e-mail e dados numéricos sensíveis (CPF/Cartão).
    """
    # Regex para e-mails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    # Regex para sequências numéricas longas (comum em IDs ou documentos)
    pii_pattern = r'\b\d{11,16}\b'
    
    masked_text = re.sub(email_pattern, "[E-MAIL OCULTADO]", text)
    masked_text = re.sub(pii_pattern, "[DADO SENSÍVEL OCULTADO]", masked_text)
    
    return masked_text

def apply_confidence_guardrail(prediction: dict, threshold: float = 0.65) -> str:
    """
    Se a confiança do modelo for baixa, força a revisão humana.
    """
    if prediction['score'] < threshold:
        return "Revisão Humana (Confiança Baixa)"
    return prediction['label']