from .gemini import GeminiModel
from .model import Model


class ModelFactory:
    def __init__(self, model_name):
        self.model_name = model_name

    def create_model(self) -> Model:
        if self.model_name == "gemini":
            return GeminiModel()
        else:
            raise ValueError(f"Model '{self.model_name}' not supported.")


__all__ = ["ModelFactory"]
