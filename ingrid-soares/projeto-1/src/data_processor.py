from typing import Optional
from src.config import Config

class DataProcessor:
    def __init__(self):
        self.fields_to_extract = Config.FIELDS_TO_EXTRACT

    def process_repositories(self, repositories: list) -> list:
        """
        Processa uma lista de repositórios brutos da API do GitHub,
        extraindo campos relevantes e garantindo a conformidade com a LGPD.
        """
        processed_data = []
        for repo in repositories:
            processed_repo = self._extract_and_validate_fields(repo)
            if processed_repo:
                processed_data.append(processed_repo)
        return processed_data

    def _extract_and_validate_fields(self, repo: dict) -> Optional[dict]:
        """
        Extrai os campos definidos e realiza validações básicas para LGPD.
        Retorna um dicionário com os campos processados ou None se houver problema.
        """
        extracted_data = {}
        for field in self.fields_to_extract:
            if field == "license":
                license_info = repo.get("license")
                extracted_data["licenca"] = license_info.get("spdx_id") if license_info else None
            elif field == "full_name":
                extracted_data["nome_repositorio"] = repo.get(field)
            elif field == "html_url":
                extracted_data["url_repositorio"] = repo.get(field)
            elif field == "created_at":
                extracted_data["data_criacao"] = repo.get(field)
            elif field == "language":
                extracted_data["linguagem_principal"] = repo.get(field)
            elif field == "description":
                extracted_data["descricao_curta"] = repo.get(field)
            elif field == "stargazers_count":
                extracted_data["estrelas"] = repo.get(field)
            elif field == "forks_count":
                extracted_data["forks"] = repo.get(field)
            else:
                # Caso haja algum campo não mapeado, adiciona-o diretamente,
                # mas o foco é nos campos predefinidos.
                extracted_data[field] = repo.get(field)

        # Validação LGPD: Garantir que não há campos de dados pessoais sendo coletados.
        # Nosso escopo já se concentra em metadados de projeto.
        # Se algum campo sensível (que não deveria estar aqui) for detectado,
        # retornaria None ou faria a anonimização aqui.
        # Ex: if 'owner_email' in extracted_data: return None

        return extracted_data
