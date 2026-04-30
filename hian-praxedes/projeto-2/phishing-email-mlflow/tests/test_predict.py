from src.model.load_model import load_model_and_tokenizer
from src.model.predict import predict_text


def test_predict_returns_expected_keys():
    model, tokenizer = load_model_and_tokenizer()
    text = "Hello team, please find attached the updated meeting notes for tomorrow."

    result = predict_text(text, model, tokenizer)

    assert "label" in result
    assert "confidence" in result
    assert "raw_class_id" in result
    assert result["label"] in ["phishing", "legitimate"]
    assert 0 <= result["confidence"] <= 1