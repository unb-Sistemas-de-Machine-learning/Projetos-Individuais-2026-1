import json
from pathlib import Path

from agent import StudentRiskAgent


def run_single_example() -> None:
    agent = StudentRiskAgent()
    sample = {
        "frequencia": 58,
        "nota_media": 5.1,
        "acessos_plataforma_semana": 2,
        "pendencia_financeira": True,
        "relato_estudante": "Estou desmotivado e com dificuldade para acompanhar as aulas.",
    }

    result = agent.predict(sample)
    print("=== Resultado de exemplo ===")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


def run_batch_examples() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    data_file = base_dir / "data" / "test_cases.json"
    if not data_file.exists():
        return

    cases = json.loads(data_file.read_text(encoding="utf-8"))
    agent = StudentRiskAgent()

    print("\n=== Execucao em lote (data/test_cases.json) ===")
    for case in cases:
        output = agent.predict(case["input"]).to_dict()
        print(f"- {case['nome']}: esperado={case['esperado']} obtido={output['nivel_risco']} score={output['score_risco']}")


if __name__ == "__main__":
    run_single_example()
    run_batch_examples()
