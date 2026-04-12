from src.config import Config
from src.github_api import GitHubAPI
from src.data_processor import DataProcessor
from src.utils import save_to_json, ensure_directory_exists
import os

class OpenSourceLicenseAgent:
    def __init__(self):
        self.github_api = GitHubAPI()
        self.data_processor = DataProcessor()
        self.output_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), # src directory
            "..", # projeto-1 directory
            Config.OUTPUT_FILE
        )
        ensure_directory_exists(self.output_file)

    def run(self):
        print("Iniciando a extração de dados de repositórios open source...")
        
        # 1. Extração de dados da API do GitHub
        raw_repositories = self.github_api.search_repositories(Config.SEARCH_PARAMS)
        print(f"Total de repositórios brutos encontrados: {len(raw_repositories)}")

        if not raw_repositories:
            print("Nenhum repositório encontrado para os parâmetros de busca.")
            return

        # 2. Processamento e validação dos dados (com foco na LGPD)
        processed_repositories = self.data_processor.process_repositories(raw_repositories)
        print(f"Total de repositórios processados e válidos: {len(processed_repositories)}")

        if not processed_repositories:
            print("Nenhum repositório processado após a validação.")
            return

        # 3. Salvando os dados processados
        save_to_json(processed_repositories, self.output_file)
        print(f"Processo de extração concluído. Dados salvos em: {self.output_file}")

if __name__ == "__main__":
    agent = OpenSourceLicenseAgent()
    agent.run()
