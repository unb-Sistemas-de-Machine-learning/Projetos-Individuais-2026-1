"""Modelos de saída do agente (explicabilidade por construção)."""

from pydantic import BaseModel, Field


class Recomendacao(BaseModel):
    titulo: str = Field(..., min_length=3, description="Nome curto da recomendação")
    tipo: str = Field(
        ...,
        description="Ex.: tópico, recurso, rotina, avaliação",
    )
    descricao: str = Field(..., min_length=10)
    justificativa: str = Field(
        ...,
        min_length=20,
        description="Por que esta recomendação se aplica ao perfil/objetivo informado",
    )
    passos: list[str] = Field(default_factory=list, max_length=8)


class AgenteSaida(BaseModel):
    resumo_perfil: str = Field(..., min_length=10)
    recomendacoes: list[Recomendacao] = Field(..., min_length=2, max_length=6)
    avisos_ou_limitacoes: list[str] = Field(default_factory=list)
