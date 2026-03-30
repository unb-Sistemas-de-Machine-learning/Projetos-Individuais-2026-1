import requests
from src.config import Config

class GitHubAPI:
    def __init__(self):
        self.base_url = Config.GITHUB_API_BASE_URL
        self.headers = self._get_headers()

    def _get_headers(self):
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if Config.GITHUB_TOKEN:
            headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"
        return headers

    def search_repositories(self, query_params: dict):
        """
        Busca repositórios na API do GitHub com base nos parâmetros fornecidos.
        Lida com paginação para obter mais resultados.
        """
        all_repositories = []
        page = 1
        per_page = query_params.get("per_page", 100)

        while True:
            params = {
                **query_params,
                "page": page,
                "per_page": per_page
            }
            response = requests.get(f"{self.base_url}/search/repositories", headers=self.headers, params=params)

            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                all_repositories.extend(items)

                # Verifica se há mais páginas
                if len(items) < per_page:
                    break # Não há mais itens, ou limite de busca atingido

                # Para evitar loops infinitos ou exceder limites da API,
                # pode-se adicionar um limite de páginas ou resultados totais.
                # Por exemplo, parar após 5 páginas para o protótipo.
                if page >= 5: # Limite arbitrário para o protótipo
                    break

                page += 1
            else:
                print(f"Erro ao buscar repositórios: {response.status_code} - {response.text}")
                break
        return all_repositories

    def get_repository_details(self, owner: str, repo: str):
        """
        Obtém detalhes de um repositório específico (pode ser usado para dados adicionais se necessário).
        Para este projeto, search_repositories já retorna a maioria dos dados que precisamos.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao obter detalhes do repositório {owner}/{repo}: {response.status_code} - {response.text}")
            return None
