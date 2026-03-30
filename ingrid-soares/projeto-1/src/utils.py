import json
import os

def save_to_json(data: list, filename: str):
    """
    Salva uma lista de dicionários em um arquivo JSON.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em {filename}")
    except IOError as e:
        print(f"Erro ao salvar dados em {filename}: {e}")

def ensure_directory_exists(filepath: str):
    """
    Garante que o diretório de um determinado filepath exista.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
