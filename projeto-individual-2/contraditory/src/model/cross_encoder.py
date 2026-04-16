from transformers import AutoTokenizer, AutoModelForSequenceClassification


def load_tokenizer_and_model(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model


def tokenize_nli_batch(batch, tokenizer, max_length: int = 128):
    return tokenizer(
        batch["premise"],
        batch["hypothesis"],
        truncation=True,
        padding="max_length",
        max_length=max_length
    )