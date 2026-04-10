import logging

from transformers import pipeline

from src.config import HF_MODEL_NAME

logger = logging.getLogger(__name__)


class PretrainedSpamModel:
    def __init__(self, model_name=HF_MODEL_NAME):
        self.model_name = model_name
        self.classifier = pipeline(
            task="text-classification",
            model=model_name,
            tokenizer=model_name,
        )
        logger.info(f"Modelo carregado: {model_name}")

    @staticmethod
    def _to_spam_probability(prediction):
        label = str(prediction.get("label", "")).lower()
        score = float(prediction.get("score", 0.0))

        if "spam" in label or label in {"label_1", "1"}:
            return score

        return 1.0 - score

    def predict_proba(self, texts):
        predictions = self.classifier(list(texts), truncation=True, max_length=512)
        return [self._to_spam_probability(prediction) for prediction in predictions]
