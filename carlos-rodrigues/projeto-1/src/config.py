import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

DEFAULT_MODEL_NAME = "gemini-2.5-flash"


class GeminiModelAdapter:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def generate_content(self, prompt, generation_config=None):
        config = None
        if generation_config:
            temperature = generation_config.get("temperature")
            if temperature is not None:
                config = types.GenerateContentConfig(temperature=temperature)

        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )


def get_gemini_model():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY nao encontrada. Defina no ambiente ou em um arquivo .env."
        )

    client = genai.Client(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL_NAME)
    if model_name in {"gemini-1.5-flash", "gemini-2.0-flash"}:
        model_name = DEFAULT_MODEL_NAME
    return GeminiModelAdapter(client, model_name)
