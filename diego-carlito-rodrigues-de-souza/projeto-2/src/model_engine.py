from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class TicketClassifier:
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        logger.info(f"Carregando modelo: {model_name}")
        # O pipeline de zero-shot-classification abstrai toda a complexidade do BART
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.labels = [
            "Account access", "Battery life", "Cancellation request", "Data loss",
            "Delivery problem", "Display issue", "Hardware issue", "Installation support",
            "Network problem", "Payment issue", "Peripheral compatibility", 
            "Product compatibility", "Product recommendation", "Product setup", 
            "Refund request", "Software bug"
        ]

    def classify(self, text: str) -> dict:
        """
        Classifica um texto dentro das categorias pré-definidas.
        """
        result = self.classifier(text, candidate_labels=self.labels)
        # Retornamos apenas a categoria com maior score e o valor da confiança
        return {
            "label": result['labels'][0],
            "score": result['scores'][0]
        }