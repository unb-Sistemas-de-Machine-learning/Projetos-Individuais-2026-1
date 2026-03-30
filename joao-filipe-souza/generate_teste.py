import csv
import json

# a funcao desse arquivo é gerar casos de testes, tendo assim uma maior diversidade

def gerar_json_comentarios(caminho_csv, quantidade=10):
    comentarios = []

    with open(caminho_csv, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for i, linha in enumerate(leitor):
            if i >= quantidade:
                break
            
            comentario = linha["Review"].strip()
            comentarios.append(comentario)

    with open("comentarios.json", "w", encoding="utf-8") as f:
        json.dump(comentarios, f, ensure_ascii=False, indent=2)

    print(f"{len(comentarios)} comentários salvos em comentarios.json")

gerar_json_comentarios("reviews.csv", quantidade=100)