from src.serving.guardrails import apply_guardrails


def test_empty_text_is_rejected():
    result = apply_guardrails("")
    assert result["status"] == "rejected"
    assert result["reason"] == "empty_text"


def test_short_text_is_rejected():
    result = apply_guardrails("hi")
    assert result["status"] == "rejected"
    assert result["reason"] == "too_short"


def test_long_text_is_rejected():
    result = apply_guardrails("a" * 5001)
    assert result["status"] == "rejected"
    assert result["reason"] == "too_long"


def test_low_confidence_becomes_abstain():
    text = "Hello team, please review the attached report before tomorrow."
    result = apply_guardrails(text, prediction={"confidence": 0.40})
    assert result["status"] == "abstain"
    assert result["reason"] == "low_confidence"


def test_normal_text_is_accepted():
    text = "Hello team, please review the attached report before tomorrow."
    result = apply_guardrails(text)
    assert result["status"] == "accepted"
    assert result["reason"] is None