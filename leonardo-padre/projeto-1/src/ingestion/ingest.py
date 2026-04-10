import fitz
import faiss
import re
import pickle
import os
from sentence_transformers import SentenceTransformer


# ── Padrões de cabeçalho típicos de livros acadêmicos ─────
# Detecta: "1.2 Título", "CHAPTER 3", "3.4.1 Subtítulo", etc.
HEADING_PATTERNS = [
    re.compile(r"^\s*CHAPTER\s+\d+", re.IGNORECASE),
    re.compile(r"^\s*\d+(\.\d+){0,3}\s+[A-Z][^\n]{3,}$"),   # 1.2 Título
    re.compile(r"^\s*[A-Z][A-Z\s]{4,}$"),                    # TÍTULO EM CAIXA ALTA
]

MAX_CHUNK_CHARS  = 1200   # teto: um chunk nunca passa disso
MIN_CHUNK_CHARS  = 150    # piso: descarta fragmentos muito pequenos
MERGE_THRESHOLD  = 600    # seções menores que isso são fundidas com a próxima


def is_heading(line: str) -> bool:
    """Retorna True se a linha parece ser um título de seção."""
    line = line.strip()
    if not line or len(line) > 120:
        return False
    return any(p.match(line) for p in HEADING_PATTERNS)


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extrai texto página a página preservando metadados de fonte
    para detecção de cabeçalhos por tamanho tipográfico.
    """
    doc   = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        # extrai blocos com informação de fonte (tamanho, flags)
        blocks = page.get_text("dict")["blocks"]
        page_text = _blocks_to_text(blocks)
        page_text = clean_text(page_text)

        if page_text.strip():
            pages.append({"page": page_num, "text": page_text})

    doc.close()
    print(f"✓ {len(pages)} páginas extraídas")
    return pages


def _blocks_to_text(blocks: list) -> str:
    """
    Reconstrói o texto da página marcando cabeçalhos tipográficos
    com um prefixo especial '##HEADING##' para facilitar a detecção.
    """
    lines = []

    # calcula o tamanho de fonte mais comum na página (corpo do texto)
    all_sizes = []
    for b in blocks:
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                all_sizes.append(round(span.get("size", 0)))

    body_size = max(set(all_sizes), key=all_sizes.count) if all_sizes else 11

    for b in blocks:
        if b.get("type") != 0:   # ignora blocos de imagem
            continue

        for line in b.get("lines", []):
            spans     = line.get("spans", [])
            line_text = " ".join(s["text"] for s in spans).strip()

            if not line_text:
                continue

            # detecta cabeçalho por tamanho de fonte OU por padrão textual
            is_larger = any(
                round(s.get("size", 0)) > body_size + 1
                for s in spans
            )
            is_bold = any(
                s.get("flags", 0) & 2**4   # bit 4 = bold em PyMuPDF
                for s in spans
            )

            if (is_larger or is_bold) and len(line_text) < 120:
                lines.append(f"##HEADING## {line_text}")
            else:
                lines.append(line_text)

    return "\n".join(lines)


def clean_text(text: str) -> str:
    text = re.sub(r'-\n(\w)', r'\1', text)          # hifenização
    text = re.sub(r'[ \t]{2,}', ' ', text)          # espaços múltiplos
    text = re.sub(r'\n{4,}', '\n\n\n', text)        # linhas em branco excessivas
    return text.strip()


def chunk_pages(pages: list[dict], **kwargs) -> list[dict]:
    """
    Chunking semântico em dois passos:
      1. Segmenta o texto em seções usando cabeçalhos como fronteiras.
      2. Seções grandes são subdivididas por parágrafo; pequenas são fundidas.
    """
    # junta todo o texto mantendo rastreamento de página
    full_segments = _split_into_sections(pages)
    chunks        = _sections_to_chunks(full_segments)

    print(f"✓ {len(chunks)} chunks semânticos gerados")
    return chunks


def _split_into_sections(pages: list[dict]) -> list[dict]:
    """
    Divide o conteúdo em seções delimitadas por cabeçalhos.
    Cada seção inclui seu título e o texto que o segue.
    """
    sections      = []
    current_title = "Introdução"
    current_lines = []
    current_page  = pages[0]["page"] if pages else 1

    for page_data in pages:
        for line in page_data["text"].splitlines():
            if line.startswith("##HEADING##"):
                # salva seção anterior
                if current_lines:
                    sections.append({
                        "title": current_title,
                        "text":  " ".join(current_lines).strip(),
                        "page":  current_page,
                    })
                # inicia nova seção
                current_title = line.replace("##HEADING##", "").strip()
                current_lines = []
                current_page  = page_data["page"]
            elif is_heading(line):
                if current_lines:
                    sections.append({
                        "title": current_title,
                        "text":  " ".join(current_lines).strip(),
                        "page":  current_page,
                    })
                current_title = line.strip()
                current_lines = []
                current_page  = page_data["page"]
            else:
                if line.strip():
                    current_lines.append(line.strip())

    # última seção
    if current_lines:
        sections.append({
            "title": current_title,
            "text":  " ".join(current_lines).strip(),
            "page":  current_page,
        })

    return sections


def _sections_to_chunks(sections: list[dict]) -> list[dict]:
    """
    Converte seções em chunks finais:
    - Seções curtas  → fundidas com a próxima
    - Seções médias  → um chunk por seção
    - Seções grandes → subdivididas por parágrafo
    """
    chunks   = []
    buffer   = None   # acumula seções pequenas

    for sec in sections:
        texto = sec["text"]

        # descarta seções sem conteúdo real
        if len(texto) < MIN_CHUNK_CHARS:
            continue

        # funde seções pequenas com o buffer
        if len(texto) < MERGE_THRESHOLD:
            if buffer is None:
                buffer = sec.copy()
            else:
                buffer["text"] += " " + texto
                # quando o buffer crescer o suficiente, emite
                if len(buffer["text"]) >= MERGE_THRESHOLD:
                    chunks.extend(_split_large_section(buffer, chunks))
                    buffer = None
            continue

        # emite buffer pendente antes de processar seção grande
        if buffer is not None:
            chunks.extend(_split_large_section(buffer, chunks))
            buffer = None

        chunks.extend(_split_large_section(sec, chunks))

    # emite buffer restante
    if buffer is not None and len(buffer["text"]) >= MIN_CHUNK_CHARS:
        chunks.extend(_split_large_section(buffer, chunks))

    # numera os chunks
    for i, c in enumerate(chunks):
        c["chunk_id"] = i

    return chunks


def _split_large_section(sec: dict, existing: list) -> list[dict]:
    """
    Se uma seção excede MAX_CHUNK_CHARS, subdivide por parágrafo.
    Caso contrário retorna a seção como chunk único.
    """
    texto  = sec["text"]
    title  = sec["title"]
    page   = sec["page"]

    if len(texto) <= MAX_CHUNK_CHARS:
        return [{
            "text":     f"[{title}] {texto}",
            "page":     page,
            "title":    title,
            "chunk_id": 0,   # será renumerado depois
        }]

    # subdivide por parágrafos (dupla quebra de linha ou ponto final + espaço)
    paragrafos = re.split(r'\.\s{1,2}(?=[A-Z])', texto)
    sub_chunks = []
    buffer     = ""

    for p in paragrafos:
        p = p.strip()
        if not p:
            continue

        candidato = (buffer + " " + p).strip() if buffer else p

        if len(candidato) <= MAX_CHUNK_CHARS:
            buffer = candidato
        else:
            if buffer and len(buffer) >= MIN_CHUNK_CHARS:
                sub_chunks.append({
                    "text":     f"[{title}] {buffer}",
                    "page":     page,
                    "title":    title,
                    "chunk_id": 0,
                })
            buffer = p

    if buffer and len(buffer) >= MIN_CHUNK_CHARS:
        sub_chunks.append({
            "text":     f"[{title}] {buffer}",
            "page":     page,
            "title":    title,
            "chunk_id": 0,
        })

    return sub_chunks if sub_chunks else [{
        "text":     f"[{title}] {texto[:MAX_CHUNK_CHARS]}",
        "page":     page,
        "title":    title,
        "chunk_id": 0,
    }]


def build_faiss_index(chunks: list[dict], model_name: str, store_dir: str):
    os.makedirs(store_dir, exist_ok=True)

    print(f"→ Carregando modelo: {model_name}")
    model = SentenceTransformer(model_name)

    texts = [c["text"] for c in chunks]
    print(f"→ Gerando embeddings para {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    faiss.normalize_L2(embeddings)

    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(store_dir, "index.faiss"))

    with open(os.path.join(store_dir, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    with open(os.path.join(store_dir, "config.pkl"), "wb") as f:
        pickle.dump({"embed_model": model_name, "dim": dim}, f)

    print(f"✓ Índice salvo — {index.ntotal} vetores (dim {dim})")