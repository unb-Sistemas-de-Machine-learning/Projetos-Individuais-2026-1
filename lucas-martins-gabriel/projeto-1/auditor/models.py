from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RedFlag:
    code: str
    level: str
    evidence: str


@dataclass
class AuditResult:
    titulo: str
    orgao: str
    objeto: str
    valor_estimado: float
    data_publicacao: Optional[str]
    fornecedor_cnpj: Optional[str] = None
    fornecedor_nome: Optional[str] = None
    capital_social: Optional[float] = None
    cnae_principal: Optional[str] = None
    company_open_date: Optional[str] = None
    score: int = 0
    risk_level: str = "Baixo"
    red_flags: List[RedFlag] = field(default_factory=list)
    pdf_url: Optional[str] = None
    pdf_excerpt: Optional[str] = None
    llm_analysis: Optional[str] = None
