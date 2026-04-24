import pandas as pd
import mlflow.pyfunc

from src.config import CONTENT_COLUMN, HF_MODEL_NAME, SPAM_THRESHOLD
from src.model.classifier import PretrainedSpamModel
from src.preprocessing.guardrails import validate_comment


class SpamClassifierPyfuncModel(mlflow.pyfunc.PythonModel):
    def __init__(self, model_name=HF_MODEL_NAME, threshold=SPAM_THRESHOLD):
        super().__init__()
        self.model_name = model_name
        self.threshold = threshold

    def load_context(self, context):
        self.model = PretrainedSpamModel(model_name=self.model_name)

    def predict(self, context, model_input):
        if isinstance(model_input, pd.DataFrame):
            texts = model_input[CONTENT_COLUMN].fillna("").astype(str).tolist()
        else:
            texts = [str(item) for item in model_input]

        guardrail_results = [validate_comment(text) for text in texts]
        valid_indices = [idx for idx, result in enumerate(guardrail_results) if result.allowed]

        spam_proba = [0.0] * len(texts)
        if valid_indices:
            valid_texts = [texts[idx] for idx in valid_indices]
            valid_scores = self.model.predict_proba(valid_texts)
            for idx, score in zip(valid_indices, valid_scores):
                spam_proba[idx] = score

        output = []
        for idx, text in enumerate(texts):
            guardrail = guardrail_results[idx]
            probability = spam_proba[idx]
            label = "spam" if probability >= self.threshold else "ham"
            if not guardrail.allowed:
                label = "rejected"

            output.append(
                {
                    "content": text,
                    "allowed": guardrail.allowed,
                    "guardrail_reason": guardrail.reason,
                    "spam_probability": probability,
                    "prediction": label,
                }
            )

        return pd.DataFrame(output)

