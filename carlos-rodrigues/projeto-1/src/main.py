import json
import os
from pathlib import Path

from agent import ProcurementAnomalyAgent


def load_data(data_path):
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _select_recent_distinct_dates(registros, limite):
    ordenados = sorted(registros, key=lambda item: item.get("Data", ""), reverse=True)

    selecionados = []
    datas_vistas = set()
    for item in ordenados:
        data = item.get("Data", "")
        if not data or data in datas_vistas:
            continue

        selecionados.append(item)
        datas_vistas.add(data)

        if len(selecionados) >= limite:
            break

    return selecionados


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "data.json"

    registros = load_data(data_path)
    limite_registros = int(os.getenv("MAX_REGISTROS", "3"))
    registros = _select_recent_distinct_dates(registros, limite_registros)

    agent = ProcurementAnomalyAgent()

    for idx, item in enumerate(registros, start=1):
        texto = item.get("Texto_encontrado", "")
        data = item.get("Data", "Data nao informada")
        municipio = item.get("Municipio", "Municipio nao informado")

        resultado = agent.run_pipeline(texto, data)

        print(f"\n=== Registro {idx} ===")
        print(f"Municipio: {municipio}")
        print(f"Data: {data}")
        print("Saida estruturada:")
        print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
