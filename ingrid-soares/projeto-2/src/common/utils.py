# src/common/utils.py

import logging
import os

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configura o sistema de logging para o projeto.
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    if log_file:
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

    logging.info("Logging configurado com sucesso.")

# Exemplo de uso (se este arquivo for executado diretamente)
if __name__ == "__main__":
    log_path = os.path.join("logs", "app.log") # Exemplo de caminho de log
    setup_logging(log_file=log_path)
    logging.info("Este é um log de informação de exemplo.")
    logging.warning("Este é um log de aviso de exemplo.")
    logging.error("Este é um log de erro de exemplo.")
