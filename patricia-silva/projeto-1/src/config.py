import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "data" / "kb"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
# IDs válidos mudam com a API; veja ListModels no AI Studio. Padrão: 2.5-flash.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def llm_backend() -> str:
    return "gemini" if GEMINI_API_KEY else "ollama"
