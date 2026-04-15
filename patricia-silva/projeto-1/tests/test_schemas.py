"""Validação de schema de saída."""

from src.schemas import AgenteSaida, Recomendacao


def test_schema_aceita_saida_minima():
    out = AgenteSaida(
        resumo_perfil="Aluno com objetivo claro e tempo limitado.",
        recomendacoes=[
            Recomendacao(
                titulo="Revisão espaçada",
                tipo="rotina",
                descricao="Usar flashcards com intervalos crescentes.",
                justificativa="Combina com o objetivo de retenção e o tempo semanal informado.",
                passos=["Escolher 20 cartões", "Revisar conforme calendário"],
            ),
            Recomendacao(
                titulo="Documentação oficial",
                tipo="recurso",
                descricao="Ler a doc da ferramenta alvo.",
                justificativa="Alinhado ao nível intermediário e ao foco em aplicação prática.",
                passos=[],
            ),
        ],
        avisos_ou_limitacoes=["Recomendações são sugestões; adapte ao seu contexto."],
    )
    assert len(out.recomendacoes) == 2
