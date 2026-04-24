import os
from dotenv import load_dotenv
from google import genai
from prompts import SYSTEM_PROMPT

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY não encontrada. Verifique o arquivo .env.")

client = genai.Client()

def summarize_text(user_text: str) -> str:
    prompt = f"""
{SYSTEM_PROMPT}

Texto do usuário:
{user_text}
"""

    response = client.models.generate_content(
        model=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
        contents=prompt,
    )

    return response.text