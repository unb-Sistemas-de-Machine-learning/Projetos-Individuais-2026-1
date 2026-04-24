def apply_guardrails(text, prediction=None):
    if text is None or not str(text).strip():
        return {"status": "rejected", "reason": "empty_text"}

    clean = str(text).strip()

    if len(clean) < 20:
        return {"status": "rejected", "reason": "too_short"}

    if len(clean) > 4000:
        return {"status": "rejected", "reason": "too_long"}

    if prediction is not None and prediction["confidence"] < 0.70:
        return {"status": "abstain", "reason": "low_confidence"}

    return {"status": "accepted", "reason": None}