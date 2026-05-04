from pathlib import Path
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("O arquivo informado não é um PDF.")

    reader = PdfReader(str(path))
    all_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            all_text.append(page_text)

    extracted_text = "\n".join(all_text).strip()

    if not extracted_text:
        raise ValueError(
            "Não foi possível extrair texto do PDF. "
            "Ele pode ser um PDF escaneado/imagem."
        )

    return extracted_text