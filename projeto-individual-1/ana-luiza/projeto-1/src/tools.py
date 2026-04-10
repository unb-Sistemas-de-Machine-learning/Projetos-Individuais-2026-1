import requests

def get_deputado_id(nome: str):
    """Busca o ID de um deputado pelo nome."""
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    params = {"nome": nome, "ordem": "ASC", "ordenarPor": "nome"}
    response = requests.get(url, params=params)
    dados = response.json().get('dados', [])
    return dados[0]['id'] if dados else None

def get_gastos_deputado(id_deputado: int, ano: int = 2024, mes: int = 1):
    """Busca despesas detalhadas de um deputado."""
    url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado}/despesas"
    params = {"ano": ano, "mes": mes, "ordem": "DESC", "ordenarPor": "valorDocumento"}
    response = requests.get(url, params=params)
    return response.json().get('dados', [])[:10] # Retorna os 10 maiores gastos