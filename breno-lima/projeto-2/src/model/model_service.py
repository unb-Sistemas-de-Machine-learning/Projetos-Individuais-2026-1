import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import requests
from io import BytesIO


class ModelService:
    def __init__(self, model_name: str):
        self.model_name = model_name

        # Carrega processor e modelo
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)

        # Modo inferência
        self.model.eval()

        # Labels
        self.id2label = self.model.config.id2label

    # -----------------------------
    # Input handling
    # -----------------------------
    def _load_image(self, image_input):
        """
        Aceita:
        - URL
        - path local
        - PIL.Image
        """

        if isinstance(image_input, str):
            if image_input.startswith("http"):
                response = requests.get(image_input)
                image = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                image = Image.open(image_input).convert("RGB")

        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")

        else:
            raise ValueError("Formato de imagem inválido")

        return image

    # -----------------------------
    # Preprocessamento
    # -----------------------------
    def _preprocess(self, image: Image.Image):
        return self.processor(images=image, return_tensors="pt")

    # -----------------------------
    # Inferência
    # -----------------------------
    def _inference(self, inputs):
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.logits

    # -----------------------------
    # Pós-processamento
    # -----------------------------
    def _postprocess(self, logits):
        probs = torch.nn.functional.softmax(logits, dim=-1)

        confidence, predicted_class = torch.max(probs, dim=-1)

        label = self.id2label[predicted_class.item()]

        return {
            "label": label,
            "confidence": confidence.item(),
            "probs": probs.squeeze().tolist(),  # útil pra debug/MLflow
        }

    # -----------------------------
    # Guardrails
    # -----------------------------
    def _apply_guardrails(self, result):
        warnings = []

        # Baixa confiança
        if result["confidence"] < 0.6:
            warnings.append("Baixa confiança na predição")

        # Você pode expandir aqui:
        # - validação de domínio
        # - detecção de imagem inválida
        # - etc.

        result["warnings"] = warnings
        return result

    # -----------------------------
    # Método público
    # -----------------------------
    def predict(self, image_input):
        image = self._load_image(image_input)

        inputs = self._preprocess(image)

        logits = self._inference(inputs)

        result = self._postprocess(logits)

        result = self._apply_guardrails(result)

        return result
