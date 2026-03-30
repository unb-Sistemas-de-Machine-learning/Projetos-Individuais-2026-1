from agent import summarize_text

def validate_input(text: str) -> tuple[bool, str]:
    if text is None:
        return False, "Entrada nula."
    if not text.strip():
        return False, "Entrada vazia."
    if len(text.strip()) < 30:
        return False, "O texto é muito curto para gerar um resumo útil."
    return True, "Entrada válida."

def preprocess_text(text: str) -> str:
    return " ".join(text.strip().split())

def postprocess_output(output: str) -> str:
    return output.strip()

def run_pipeline(user_text: str) -> str:
    is_valid, message = validate_input(user_text)
    if not is_valid:
        return f"Erro: {message}"

    clean_text = preprocess_text(user_text)
    raw_output = summarize_text(clean_text)
    final_output = postprocess_output(raw_output)

    return final_output