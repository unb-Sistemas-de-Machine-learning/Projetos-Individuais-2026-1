import argparse
from typing import List

from auditor.clients import build_client, extract_pdf_text, fetch_company_data, fetch_pncp_contracts, require_api_key
from auditor.models import AuditResult
from auditor.reporting import generate_llm_analysis, render_markdown_report, save_markdown_report
from auditor.rules import evaluate_red_flags
from auditor.utils import licitacao_sort_value


DEFAULT_MAX_PAGINAS = 3
DEFAULT_HTTP_TIMEOUT = 20.0
DEFAULT_HTTP_RETRIES = 2


def _resolve_positive_int(value: int | None, default: int) -> int:
    return value if value is not None and value > 0 else default


def _resolve_positive_float(value: float | None, default: float) -> float:
    return value if value is not None and value > 0 else default


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auditor de compras publicas com regras deterministicamente auditaveis."
    )
    parser.add_argument("--data-inicial", required=True, help="Data inicial no formato AAAAMMDD.")
    parser.add_argument("--data-final", required=True, help="Data final no formato AAAAMMDD.")
    parser.add_argument("--modalidade", type=int, default=5, help="Codigo da modalidade no PNCP.")
    parser.add_argument(
        "--max-paginas",
        type=int,
        default=None,
        help=f"Maximo de paginas a consultar. Opcional; padrao: {DEFAULT_MAX_PAGINAS}.",
    )
    parser.add_argument("--top-n", type=int, default=5, help="Quantidade de licitacoes auditadas.")
    parser.add_argument(
        "--http-timeout",
        type=float,
        default=None,
        help=f"Timeout base das chamadas HTTP, em segundos. Opcional; padrao: {int(DEFAULT_HTTP_TIMEOUT)}.",
    )
    parser.add_argument(
        "--http-retries",
        type=int,
        default=None,
        help=f"Numero de tentativas por chamada HTTP. Opcional; padrao: {DEFAULT_HTTP_RETRIES}.",
    )
    parser.add_argument(
        "--http-backoff",
        type=float,
        default=2.0,
        help="Backoff base entre tentativas HTTP, em segundos.",
    )
    parser.add_argument(
        "--incluir-pdf",
        action="store_true",
        help="Baixa e extrai as primeiras paginas do edital quando houver URL disponivel.",
    )
    parser.add_argument(
        "--saida-md",
        default="relatorio_auditoria.md",
        help="Arquivo Markdown de saida.",
    )
    return parser.parse_args()


def audit_contracts(args: argparse.Namespace) -> List[AuditResult]:
    max_paginas = _resolve_positive_int(args.max_paginas, DEFAULT_MAX_PAGINAS)
    http_timeout = _resolve_positive_float(args.http_timeout, DEFAULT_HTTP_TIMEOUT)
    http_retries = _resolve_positive_int(args.http_retries, DEFAULT_HTTP_RETRIES)

    contracts = fetch_pncp_contracts(
        data_inicial=args.data_inicial,
        data_final=args.data_final,
        modalidade=args.modalidade,
        max_paginas=max_paginas,
        timeout=http_timeout,
        retries=http_retries,
        backoff_seconds=args.http_backoff,
    )

    ranked = sorted(contracts, key=licitacao_sort_value, reverse=True)[: args.top_n]
    if not ranked:
        print("[!] Nenhuma licitacao encontrada para os parametros informados.")
        return []

    client = build_client(require_api_key())
    results: List[AuditResult] = []

    for index, licitacao in enumerate(ranked, start=1):
        metadata = licitacao["_metadata"]
        print(f"[*] Auditando item {index}/{len(ranked)}: {metadata['titulo']}")
        company = fetch_company_data(
            metadata["fornecedor_cnpj"],
            timeout=http_timeout,
            retries=max(1, min(http_retries, 2)),
            backoff_seconds=args.http_backoff,
        )
        pdf_excerpt = (
            extract_pdf_text(
                metadata["pdf_url"],
                timeout=max(http_timeout, 25),
                retries=max(1, min(http_retries, 2)),
                backoff_seconds=args.http_backoff,
            )
            if args.incluir_pdf
            else None
        )
        result = evaluate_red_flags(licitacao, company, contracts, pdf_excerpt=pdf_excerpt)

        try:
            result.llm_analysis = generate_llm_analysis(client, result)
        except Exception as exc:  # pragma: no cover - depends on network/SDK
            raise RuntimeError(
                "Falha ao gerar a consolidacao com LLM. "
                f"Execucao interrompida no item {index}: {metadata['titulo']}. "
                f"Erro reportado: {exc}"
            ) from exc

        results.append(result)

    return results


def main() -> None:
    args = parse_args()
    max_paginas = _resolve_positive_int(args.max_paginas, DEFAULT_MAX_PAGINAS)
    results = audit_contracts(args)
    if not results:
        return

    report = render_markdown_report(
        results,
        metadata={
            "data_inicial": args.data_inicial,
            "data_final": args.data_final,
            "modalidade": args.modalidade,
            "max_paginas": max_paginas,
        },
    )
    save_markdown_report(report, args.saida_md)
