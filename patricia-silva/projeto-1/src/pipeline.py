"""Orquestração: entrada estruturada → RAG → LLM → saída validada."""

from __future__ import annotations

from dataclasses import dataclass

from . import config
from .agent import gerar_plano
from .retrieval import TfIdfRetriever, load_kb_chunks
from .schemas import AgenteSaida


@dataclass
class EntradaUsuario:
    objetivo: str
    nivel: str
    horas_semana: str
    restricoes: str = ""

    def as_query(self) -> str:
        parts = [self.objetivo, self.nivel, self.horas_semana]
        if self.restricoes.strip():
            parts.append(self.restricoes.strip())
        return " ".join(parts)


def montar_prompt_usuario(entrada: EntradaUsuario, contexto_rag: str) -> str:
    bloco_ctx = (
        "Contexto recuperado da base de conhecimento (use quando fizer sentido):\n"
        + contexto_rag
        if contexto_rag.strip()
        else "Nenhum trecho relevante recuperado; baseie-se no perfil abaixo e em boas práticas."
    )
    return f"""Perfil do aluno:
- Objetivo de aprendizagem: {entrada.objetivo}
- Nível (iniciante/intermediário/avançado): {entrada.nivel}
- Tempo disponível por semana: {entrada.horas_semana}
- Restrições ou preferências: {entrada.restricoes or "(nenhuma informada)"}

{bloco_ctx}
"""


def executar(entrada: EntradaUsuario, top_k: int = 4) -> AgenteSaida:
    chunks = load_kb_chunks(config.KB_DIR)
    retriever = TfIdfRetriever(chunks)
    q = entrada.as_query()
    trechos = retriever.top_k(q, k=top_k)
    contexto = "\n\n---\n\n".join(trechos) if trechos else ""
    prompt = montar_prompt_usuario(entrada, contexto)
    return gerar_plano(prompt)
