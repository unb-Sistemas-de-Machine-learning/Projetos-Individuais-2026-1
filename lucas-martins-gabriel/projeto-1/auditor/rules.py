from typing import Dict, List, Optional, Tuple

from auditor.models import AuditResult, RedFlag
from auditor.utils import licitacao_sort_value, normalize_text, parse_date, parse_float


def assess_cnae_compatibility(objeto: str, cnae: Optional[str]) -> Optional[Tuple[str, int]]:
    if not objeto or not cnae:
        return None

    domain_terms = {
        "software": {"software", "sistema", "tecnologia", "informatica", "desenvolvimento"},
        "obra": {"obra", "engenharia", "pavimentacao", "reforma", "construcao"},
        "alimento": {"merenda", "alimento", "nutricao", "genero", "alimenticio"},
        "saude": {"hospital", "medicamento", "saude", "clinico", "laboratorio"},
        "limpeza": {"limpeza", "higiene", "coleta", "residuo"},
    }

    objeto_text = objeto.lower()
    cnae_text = cnae.lower()
    matched_object_domains = {
        name for name, keywords in domain_terms.items() if any(word in objeto_text for word in keywords)
    }
    matched_cnae_domains = {
        name for name, keywords in domain_terms.items() if any(word in cnae_text for word in keywords)
    }

    if matched_object_domains and matched_cnae_domains and matched_object_domains.isdisjoint(matched_cnae_domains):
        evidence = (
            "Possivel incompatibilidade entre objeto e CNAE principal: "
            f"objeto sugere {sorted(matched_object_domains)}, CNAE sugere {sorted(matched_cnae_domains)}."
        )
        return evidence, 2

    return None


def compute_concentration(
    all_contracts: List[Dict], fornecedor_cnpj: Optional[str], orgao: str
) -> Optional[Tuple[str, int]]:
    if not fornecedor_cnpj:
        return None

    wins = []
    for item in all_contracts:
        metadata = item.get("_metadata", {})
        if metadata.get("fornecedor_cnpj") == fornecedor_cnpj and metadata.get("orgao") == orgao:
            wins.append(item)

    if len(wins) >= 3:
        evidence = (
            f"Fornecedor aparece em {len(wins)} registros associados ao mesmo orgao no periodo consultado."
        )
        return evidence, 3

    if len(wins) == 2:
        evidence = "Fornecedor aparece em 2 registros do mesmo orgao no periodo consultado."
        return evidence, 1

    return None


def classify_risk(score: int) -> str:
    if score >= 7:
        return "Critico"
    if score >= 5:
        return "Alto"
    if score >= 3:
        return "Medio"
    return "Baixo"


def evaluate_red_flags(
    licitacao: Dict,
    company: Optional[Dict],
    all_contracts: List[Dict],
    pdf_excerpt: Optional[str] = None,
) -> AuditResult:
    metadata = licitacao["_metadata"]
    valor = licitacao_sort_value(licitacao)
    result = AuditResult(
        titulo=metadata["titulo"],
        orgao=metadata["orgao"],
        objeto=metadata["objeto"],
        valor_estimado=valor,
        data_publicacao=metadata["data_publicacao"],
        fornecedor_cnpj=metadata["fornecedor_cnpj"],
        fornecedor_nome=metadata["fornecedor_nome"],
        pdf_url=metadata["pdf_url"],
        pdf_excerpt=pdf_excerpt,
    )

    if company:
        result.fornecedor_nome = normalize_text(company.get("razao_social") or result.fornecedor_nome)
        result.capital_social = parse_float(company.get("capital_social"))
        result.cnae_principal = normalize_text(company.get("cnae_fiscal_descricao"))
        result.company_open_date = company.get("data_inicio_atividade")

    if result.capital_social is not None and result.valor_estimado > 0:
        threshold = result.valor_estimado * 0.10
        if result.capital_social < threshold:
            result.red_flags.append(
                RedFlag(
                    code="CAPITAL_SOCIAL_BAIXO",
                    level="alto",
                    evidence=(
                        f"Capital social de R$ {result.capital_social:,.2f} abaixo de 10% do valor estimado "
                        f"da contratacao (R$ {threshold:,.2f})."
                    ),
                )
            )
            result.score += 3

    abertura = parse_date(result.company_open_date)
    publicacao = parse_date(result.data_publicacao)
    if abertura and publicacao:
        delta_days = (publicacao - abertura).days
        if delta_days < 180:
            result.red_flags.append(
                RedFlag(
                    code="EMPRESA_RECENTE",
                    level="alto",
                    evidence=f"Empresa aberta {delta_days} dias antes da publicacao da contratacao.",
                )
            )
            result.score += 3

    cnae_result = assess_cnae_compatibility(result.objeto, result.cnae_principal)
    if cnae_result:
        evidence, points = cnae_result
        result.red_flags.append(RedFlag(code="CNAE_POSSIVEL_INCOMPATIBILIDADE", level="medio", evidence=evidence))
        result.score += points

    concentration = compute_concentration(all_contracts, result.fornecedor_cnpj, result.orgao)
    if concentration:
        evidence, points = concentration
        result.red_flags.append(RedFlag(code="CONCENTRACAO_FORNECEDOR", level="medio", evidence=evidence))
        result.score += points

    if pdf_excerpt and pdf_excerpt.startswith("Erro ao ler PDF"):
        result.red_flags.append(
            RedFlag(
                code="PDF_NAO_PROCESSADO",
                level="baixo",
                evidence=pdf_excerpt,
            )
        )

    if not result.red_flags:
        result.red_flags.append(
            RedFlag(
                code="SEM_RED_FLAGS_OBJETIVAS",
                level="baixo",
                evidence="Nenhuma red flag objetiva foi acionada pelas regras deterministicamente calculadas.",
            )
        )

    result.risk_level = classify_risk(result.score)
    return result
