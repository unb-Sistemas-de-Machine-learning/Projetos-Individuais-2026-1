import json
from dataclasses import asdict
from typing import Any, Dict, List

from google import genai
from google.genai import types

from auditor.models import AuditResult


DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
Voce e um Auditor Senior da Controladoria-Geral da Uniao (CGU).
Sua tarefa e explicar o parecer final a partir de evidencias estruturadas ja calculadas.

Regras:
1. Nao invente fatos ausentes do contexto.
2. Trate as flags deterministicamente calculadas como base principal da analise.
3. Quando houver dados insuficientes, diga explicitamente "dados insuficientes".
4. Estruture a resposta em:
   - GRAU DE RISCO
   - EVIDENCIAS ENCONTRADAS
   - RECOMENDACAO DE INVESTIGACAO
   - LIMITACOES DA ANALISE
""".strip()


def build_llm_prompt(result: AuditResult) -> str:
    payload = {
        "titulo": result.titulo,
        "orgao": result.orgao,
        "objeto": result.objeto,
        "valor_estimado": result.valor_estimado,
        "data_publicacao": result.data_publicacao,
        "fornecedor": {
            "cnpj": result.fornecedor_cnpj,
            "nome": result.fornecedor_nome,
            "capital_social": result.capital_social,
            "cnae_principal": result.cnae_principal,
            "data_abertura": result.company_open_date,
        },
        "score": result.score,
        "risk_level": result.risk_level,
        "red_flags": [asdict(flag) for flag in result.red_flags],
        "pdf_excerpt": result.pdf_excerpt,
    }
    return (
        "Com base nos dados estruturados abaixo, redija um parecer curto e objetivo.\n\n"
        + json.dumps(payload, indent=2, ensure_ascii=False)
    )


def generate_llm_analysis(client: genai.Client, result: AuditResult, model: str = DEFAULT_MODEL) -> str:
    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
        ),
        contents=build_llm_prompt(result),
    )
    return response.text


def render_audit_entry(result: AuditResult) -> str:
    lines = [
        f"## {result.titulo}",
        f"- Orgao: {result.orgao}",
        f"- Objeto: {result.objeto}",
        f"- Valor estimado: R$ {result.valor_estimado:,.2f}",
        f"- Data de publicacao: {result.data_publicacao or 'nao informada'}",
        f"- Fornecedor: {result.fornecedor_nome or 'nao identificado'}",
        f"- CNPJ: {result.fornecedor_cnpj or 'nao identificado'}",
        f"- Grau de risco: {result.risk_level}",
        f"- Score objetivo: {result.score}",
        "",
        "### Evidencias objetivas",
    ]

    for flag in result.red_flags:
        lines.append(f"- [{flag.level.upper()}] {flag.code}: {flag.evidence}")

    if result.pdf_url:
        lines.append(f"- PDF relacionado: {result.pdf_url}")

    if result.llm_analysis:
        lines.extend(["", "### Parecer consolidado", result.llm_analysis.strip()])

    return "\n".join(lines).strip()


def render_markdown_report(results: List[AuditResult], metadata: Dict[str, Any]) -> str:
    total = len(results)
    criticos = sum(1 for item in results if item.risk_level == "Critico")
    altos = sum(1 for item in results if item.risk_level == "Alto")
    medios = sum(1 for item in results if item.risk_level == "Medio")

    header = [
        "# Relatorio de Auditoria de Compras Publicas",
        "",
        f"- Periodo consultado: {metadata['data_inicial']} a {metadata['data_final']}",
        f"- Modalidade: {metadata['modalidade']}",
        f"- Paginas consultadas: {metadata['max_paginas']}",
        f"- Licitacoes auditadas: {total}",
        "",
        "## Resumo executivo",
        f"- Critico: {criticos}",
        f"- Alto: {altos}",
        f"- Medio: {medios}",
        f"- Baixo: {total - criticos - altos - medios}",
        "",
    ]

    body = "\n\n".join(render_audit_entry(result) for result in results)
    return "\n".join(header) + body + "\n"


def save_markdown_report(content: str, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"[V] Relatorio Markdown salvo em {output_path}")
