import torch

def predict_text(text, model, tokenizer):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        pred = torch.argmax(probs).item()

    confidence = float(probs[pred].item())

    label = "phishing" if pred == 1 else "legitimate"

    return {
        "label": label,
        "confidence": confidence,
        "raw_class_id": pred
    }