import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_profile_summary(profile):
    languages = ", ".join(
        [f"{lang} ({count} repositórios)" for lang, count in profile["languages"]]
    )
    external_repos = (
        ", ".join(profile["pull_requests"]["external_repositories"]) or "Nenhum"
    )

    return f""" 
        Username: {profile['username']}
        Nome: {profile['name']}
        Bio: {profile['bio']}
        Conta criada em: {profile['created_at']}
        Repositórios públicos: {profile['public_repos']}
        Seguidores: {profile['followers']}
        Linguagens: {languages}
        Total de PRs abertos: {profile['pull_requests']['total_opened']}
        Total de PRs mergeados: {profile['pull_requests']['total_merged']}
        Repositórios externos onde contribuiu: {external_repos}
    """


def analyze_profile(profile):
    summary = build_profile_summary(profile)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um analisador de perfis técnicos do GitHub. "
                    "Com base nos dados fornecidos, retorne APENAS um JSON válido, sem texto adicional, no seguinte formato:\n"
                    "{\n"
                    '  "nivel": "Iniciante" | "Intermediário" | "Avançado",\n'
                    '  "linguagens": ["linguagem1", "linguagem2"],\n'
                    '  "tipo": "Solo" | "Colaborador Open Source" | "Colaborador de Equipe",\n'
                    '  "resumo": "Uma frase curta descrevendo o perfil"\n'
                    "}"
                ),
            },
            {
                "role": "user",
                "content": f"Analise o seguinte perfil do GitHub:\n{summary}",
            },
        ],
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    return json.loads(content)
