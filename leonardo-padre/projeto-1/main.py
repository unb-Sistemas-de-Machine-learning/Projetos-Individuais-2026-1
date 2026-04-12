"""
Ponto de entrada único do Tutor Agent.
- Roda o ingest apenas se o índice FAISS ainda não existir.
- Inicializa o agente e abre o CLI.
"""

import os
import sys

# garante que src/ está no path para imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ingestion.ingest import build_faiss_index, extract_text_from_pdf, chunk_pages
from agent.interface import run_cli

# ── Configurações centrais ─────────────────────────────────
PDF_PATH      = os.path.join("data", "PSPD_Tannenbaum.pdf")
STORE_DIR     = "vector_store"
EMBED_MODEL   = "paraphrase-multilingual-MiniLM-L12-v2"
# ──────────────────────────────────────────────────────────


def index_exists(store_dir: str) -> bool:
    """Verifica se o índice FAISS já foi gerado."""
    return (
        os.path.exists(os.path.join(store_dir, "index.faiss")) and
        os.path.exists(os.path.join(store_dir, "chunks.pkl"))  and
        os.path.exists(os.path.join(store_dir, "config.pkl"))
    )


def run_ingestion():
    """Executa o pipeline completo de ingestão do PDF."""
    print("━" * 50)
    print("  Índice não encontrado — iniciando ingestão")
    print("━" * 50)

    if not os.path.exists(PDF_PATH):
        print(f"\n❌ PDF não encontrado em: {PDF_PATH}")
        print("   Coloque o arquivo em data/ e tente novamente.")
        sys.exit(1)

    pages  = extract_text_from_pdf(PDF_PATH)
    chunks = chunk_pages(pages)
    build_faiss_index(chunks, EMBED_MODEL, STORE_DIR)

    print("\n✅ Ingestão concluída!\n")


def main():
    # 1. Ingest só se necessário
    if not index_exists(STORE_DIR):
        run_ingestion()
    else:
        print("✅ Índice FAISS encontrado — pulando ingestão.\n")

    # 2. Inicia o CLI
    run_cli(store_dir=STORE_DIR)


if __name__ == "__main__":
    main()