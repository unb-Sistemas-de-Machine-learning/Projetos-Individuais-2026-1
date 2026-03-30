import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_API_BASE_URL = "https://api.github.com"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Opcional, para aumentar o limite de requisições
    OUTPUT_FILE = "dados_projetos_open_source.json"
    SEARCH_PARAMS = {
        "q": "language:>1 created:>=2024-01-01", # Exemplo: projetos criados a partir de 2024
        "sort": "stars",
        "order": "desc",
        "per_page": 100 # Máximo de resultados por página
    }
    # Campos a serem extraídos da API do GitHub
    FIELDS_TO_EXTRACT = [
        "full_name",
        "html_url",
        "created_at",
        "language",
        "license", # Será processado para 'spdx_id'
        "description",
        "stargazers_count",
        "forks_count"
    ]
    # Outras configurações para LGPD ou lógica do agente podem ser adicionadas aqui
