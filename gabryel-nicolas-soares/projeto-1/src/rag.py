# rag simples
BASE_CONHECIMENTO = [
    {
        "id": "bolsa_familia_criterio",
        "titulo": "Bolsa Família — Critério de renda",
        "conteudo": (
            "O Bolsa Família é destinado a famílias com renda per capita mensal de até R$ 218,00. "
            "A inscrição é feita pelo CadÚnico. Documentos necessários: CPF, RG, comprovante de renda "
            "e comprovante de residência. O cadastro deve ser atualizado a cada 2 anos."
        ),
        "fonte": "Decreto nº 11.150/2022 e Lei nº 14.284/2021"
    },
    {
        "id": "bpc_criterio",
        "titulo": "BPC — Critérios de elegibilidade",
        "conteudo": (
            "O Benefício de Prestação Continuada (BPC) garante 1 salário mínimo mensal a idosos com "
            "65 anos ou mais e a pessoas com deficiência de qualquer idade, desde que a renda familiar "
            "per capita seja de até 1/4 do salário mínimo (R$ 353,00 em 2024). "
            "Não é necessário ter contribuído para o INSS. O requerimento é feito no INSS ou CRAS."
        ),
        "fonte": "LOAS — Lei nº 8.742/1993, Art. 20"
    },
    {
        "id": "cadunico_info",
        "titulo": "CadÚnico — O que é e como funciona",
        "conteudo": (
            "O Cadastro Único (CadÚnico) é o registro do governo federal que identifica famílias "
            "de baixa renda para acesso a programas sociais. Famílias com renda mensal de até meio "
            "salário mínimo por pessoa, ou renda total de até 3 salários mínimos, podem se cadastrar. "
            "O cadastro é feito no CRAS do município."
        ),
        "fonte": "Decreto nº 6.135/2007"
    },
    {
        "id": "cras_servicos",
        "titulo": "CRAS — Serviços disponíveis",
        "conteudo": (
            "O Centro de Referência de Assistência Social (CRAS) oferece: cadastramento no CadÚnico, "
            "orientação sobre benefícios, encaminhamentos para serviços especializados, "
            "Serviço de Proteção e Atendimento Integral à Família (PAIF) e grupos socioeducativos. "
            "O atendimento é gratuito e presencial."
        ),
        "fonte": "Política Nacional de Assistência Social (PNAS/2004)"
    },
    {
        "id": "bpc_deficiencia",
        "titulo": "BPC para Pessoa com Deficiência",
        "conteudo": (
            "Pessoa com deficiência tem direito ao BPC independente da idade, desde que a deficiência "
            "seja de longo prazo (mínimo 2 anos) e cause impedimento à participação plena na sociedade. "
            "A avaliação é feita pelo INSS com laudo médico e avaliação social. "
            "Renda per capita familiar deve ser de até 1/4 do salário mínimo."
        ),
        "fonte": "LOAS — Lei nº 8.742/1993, Art. 20, § 2º"
    }
]


def buscar_rag(pergunta: str, top_k: int = 2) -> list[dict]:

    pergunta_lower = pergunta.lower()
    pontuacoes = []

    for doc in BASE_CONHECIMENTO:
        texto = (doc["titulo"] + " " + doc["conteudo"]).lower()
        palavras = set(pergunta_lower.split())
        score = sum(1 for p in palavras if p in texto and len(p) > 3)
        pontuacoes.append((score, doc))

    pontuacoes.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in pontuacoes[:top_k] if score > 0]