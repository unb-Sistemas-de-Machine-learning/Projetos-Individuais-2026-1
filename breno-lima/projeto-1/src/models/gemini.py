from google import genai
import os

from models.model import Model


api_key = os.environ["API_KEY"]

if (not api_key) or api_key == "":
    raise Exception("API_KEY environment variable is not set.")


class GeminiModel(Model):
    def prompt_diff(self, diff: str) -> str | None:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            config=genai.types.GenerateContentConfig(
                system_instruction="You are a helpful assistant that summarizes git diffs into concise commit messages."
            ),
            contents=diff,
        )

        return response.text
