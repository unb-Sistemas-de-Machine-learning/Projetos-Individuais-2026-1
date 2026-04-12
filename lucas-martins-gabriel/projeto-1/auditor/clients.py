import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import find_dotenv, load_dotenv
from google import genai

from auditor.utils import extract_items, extract_licitacao_metadata, normalize_text, stable_item_id

try:
    import fitz
except ImportError:  # pragma: no cover - optional dependency
    fitz = None


PNCP_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
DEFAULT_HEADERS = {"User-Agent": "auditor/1.0", "Accept": "application/json"}
MAX_PDF_PAGES = 5
MAX_PDF_CHARS = 4000


def load_local_env() -> None:
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path, override=False)


def _normalize_timeout(timeout: float) -> Tuple[float, float]:
    connect_timeout = min(10.0, timeout)
    read_timeout = max(timeout, 10.0)
    return connect_timeout, read_timeout


def request_json(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 20,
    retries: int = 3,
    backoff_seconds: float = 2.0,
) -> Any:
    last_error: Optional[Exception] = None
    timeout_tuple = _normalize_timeout(timeout)

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout_tuple)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries:
                break
            wait_time = backoff_seconds * attempt
            print(
                f"[!] Tentativa {attempt}/{retries} falhou para {url}: {exc}. "
                f"Tentando novamente em {wait_time:.1f}s."
            )
            time.sleep(wait_time)

    raise last_error if last_error else RuntimeError(f"Falha desconhecida ao consultar {url}")


def request_bytes(
    url: str,
    timeout: float = 20,
    retries: int = 2,
    backoff_seconds: float = 2.0,
) -> bytes:
    last_error: Optional[Exception] = None
    timeout_tuple = _normalize_timeout(timeout)

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout_tuple)
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries:
                break
            wait_time = backoff_seconds * attempt
            print(
                f"[!] Tentativa {attempt}/{retries} falhou ao baixar {url}: {exc}. "
                f"Nova tentativa em {wait_time:.1f}s."
            )
            time.sleep(wait_time)

    raise last_error if last_error else RuntimeError(f"Falha desconhecida ao baixar {url}")


def require_api_key() -> str:
    load_local_env()
    api_key = os.getenv("KEY")
    if not api_key:
        raise RuntimeError(
            "Variavel KEY nao encontrada. "
            "Defina KEY no ambiente ou em um arquivo .env antes de executar o agente."
        )
    return api_key


def build_client(api_key: str) -> genai.Client:
    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:  # pragma: no cover - depends on SDK/runtime
        raise RuntimeError(f"Nao foi possivel inicializar o cliente Gemini: {exc}") from exc


def fetch_pncp_page(
    data_inicial: str,
    data_final: str,
    pagina: int,
    modalidade: int,
    timeout: float,
    retries: int,
    backoff_seconds: float,
) -> List[Dict[str, Any]]:
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": modalidade,
        "pagina": pagina,
    }
    print(f"[*] Consultando PNCP, pagina {pagina}, parametros={params}")
    payload = request_json(
        PNCP_URL,
        params=params,
        timeout=timeout,
        retries=retries,
        backoff_seconds=backoff_seconds,
    )
    return extract_items(payload)


def fetch_pncp_contracts(
    data_inicial: str,
    data_final: str,
    modalidade: int,
    max_paginas: int,
    timeout: float = 40,
    retries: int = 3,
    backoff_seconds: float = 2.0,
) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    seen_ids = set()

    for pagina in range(1, max_paginas + 1):
        try:
            items = fetch_pncp_page(
                data_inicial,
                data_final,
                pagina,
                modalidade,
                timeout,
                retries,
                backoff_seconds,
            )
        except requests.RequestException as exc:
            print(f"[!] Falha ao consultar PNCP na pagina {pagina}: {exc}")
            break

        if not items:
            break

        for item in items:
            unique_id = stable_item_id(item)
            if unique_id in seen_ids:
                continue
            seen_ids.add(unique_id)
            enriched = dict(item)
            enriched["_metadata"] = extract_licitacao_metadata(item)
            collected.append(enriched)

    print(f"[*] {len(collected)} licitacoes coletadas apos paginacao.")
    return collected


def fetch_company_data(
    cnpj: Optional[str],
    timeout: float = 20,
    retries: int = 2,
    backoff_seconds: float = 1.5,
) -> Optional[Dict[str, Any]]:
    if not cnpj:
        return None

    url = BRASIL_API_URL.format(cnpj=cnpj)
    print(f"[*] Consultando Brasil API para CNPJ {cnpj}")
    try:
        return request_json(url, timeout=timeout, retries=retries, backoff_seconds=backoff_seconds)
    except requests.RequestException as exc:
        print(f"[!] Falha ao consultar Brasil API para {cnpj}: {exc}")
        return None


def extract_pdf_text(
    url_pdf: Optional[str],
    timeout: float = 25,
    retries: int = 2,
    backoff_seconds: float = 1.5,
) -> Optional[str]:
    if not url_pdf:
        return None
    if fitz is None:
        return "Leitura de PDF indisponivel: PyMuPDF nao instalado."

    print(f"[*] Baixando edital PDF: {url_pdf}")
    try:
        content = request_bytes(
            url_pdf,
            timeout=timeout,
            retries=retries,
            backoff_seconds=backoff_seconds,
        )
        with fitz.open(stream=content, filetype="pdf") as doc:
            texto = []
            for index, pagina in enumerate(doc):
                if index >= MAX_PDF_PAGES:
                    break
                texto.append(pagina.get_text())
        combined = normalize_text(" ".join(texto))
        return combined[:MAX_PDF_CHARS] if combined else None
    except Exception as exc:  # pragma: no cover - depends on network and remote file
        return f"Erro ao ler PDF: {exc}"
