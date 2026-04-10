import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple


def normalize_cnpj(value: Any) -> Optional[str]:
    digits = re.sub(r"\D", "", str(value or ""))
    return digits if len(digits) == 14 else None


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("R$", "").replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def parse_date(value: Any) -> Optional[datetime]:
    if not value:
        return None

    raw = str(value).strip()
    candidates = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%d/%m/%Y",
        "%Y%m%d",
    ]

    for fmt in candidates:
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    if raw.endswith("Z"):
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None

    try:
        parsed = datetime.fromisoformat(raw)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def extract_items(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ("data", "items", "content", "resultado", "resultados"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

    return []


def iter_nested_values(obj: Any) -> Iterable[Any]:
    if isinstance(obj, dict):
        for value in obj.values():
            yield value
            yield from iter_nested_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield item
            yield from iter_nested_values(item)


def find_first_value(obj: Any, candidate_keys: Tuple[str, ...]) -> Any:
    lowered = set(candidate_keys)
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in lowered and value not in (None, ""):
                return value
        for value in obj.values():
            found = find_first_value(value, candidate_keys)
            if found not in (None, ""):
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first_value(item, candidate_keys)
            if found not in (None, ""):
                return found
    return None


def collect_url_candidates(obj: Any) -> List[str]:
    found: List[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = key.lower()
            if isinstance(value, str) and value.startswith("http"):
                if "pdf" in key_lower or value.lower().endswith(".pdf"):
                    found.append(value)
            else:
                found.extend(collect_url_candidates(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(collect_url_candidates(item))
    return found


def extract_supplier_cnpj(item: Dict[str, Any]) -> Optional[str]:
    key_hints = ("cnpj", "cnpjfornecedor", "niFornecedor", "numerodocumento", "identificador")
    direct = find_first_value(item, key_hints)
    direct_cnpj = normalize_cnpj(direct)
    if direct_cnpj:
        return direct_cnpj

    for value in iter_nested_values(item):
        candidate = normalize_cnpj(value)
        if candidate:
            return candidate

    return None


def licitacao_sort_value(item: Dict[str, Any]) -> float:
    candidates = (
        "valorTotalEstimado",
        "valorEstimado",
        "valorGlobal",
        "valorTotalHomologado",
        "valorTotal",
    )
    for key in candidates:
        value = parse_float(find_first_value(item, (key.lower(), key)))
        if value is not None:
            return value
    return 0.0


def extract_licitacao_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
    orgao = find_first_value(
        item,
        (
            "nomeorgaoentidade",
            "orgaoentidade",
            "nomeunidadeorgao",
            "orgao",
            "unidadeorgao",
        ),
    )
    objeto = find_first_value(
        item,
        ("objetocompra", "objeto", "descricaocompleta", "descricao", "informacaocomplementar"),
    )
    data_publicacao = find_first_value(
        item,
        ("datapublicacao", "dataabertura", "datainclusao", "datadivulgacaopncp"),
    )
    numero_controle = find_first_value(
        item,
        ("numerocontrolepncp", "sequencialcompra", "id", "numeroprocesso"),
    )
    titulo = normalize_text(find_first_value(item, ("titulo", "objeto", "objetocompra")) or "Licitacao")
    fornecedor_cnpj = extract_supplier_cnpj(item)
    fornecedor_nome = find_first_value(
        item,
        (
            "razaosocial",
            "nomefornecedor",
            "nomefantasia",
            "fornecedor",
            "nome",
        ),
    )
    pdf_urls = collect_url_candidates(item)

    return {
        "titulo": titulo,
        "orgao": normalize_text(orgao or "Orgao nao identificado"),
        "objeto": normalize_text(objeto or "Objeto nao informado"),
        "data_publicacao": str(data_publicacao) if data_publicacao else None,
        "numero_controle": normalize_text(numero_controle or ""),
        "fornecedor_cnpj": fornecedor_cnpj,
        "fornecedor_nome": normalize_text(fornecedor_nome or "") or None,
        "pdf_url": pdf_urls[0] if pdf_urls else None,
    }


def stable_item_id(item: Dict[str, Any]) -> str:
    metadata = extract_licitacao_metadata(item)
    return metadata["numero_controle"] or json.dumps(item, sort_keys=True, ensure_ascii=False)
