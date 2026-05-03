import importlib.util
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, List


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "docs" / "evidence"

SAMPLES = [
    "Nao consigo acessar o portal e preciso urgente para enviar atividade.",
    "Preciso da segunda via do boleto da mensalidade. Meu RA e 211061529.",
    "Quero emitir meu historico escolar para estagio.",
    "Preciso de ajuda com meu orientador de TCC e data da banca.",
    "Oi, tudo bem?",
]


def _load_function(file_path: Path, function_name: str) -> Callable[[str], Dict[str, Any]]:
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Nao foi possivel carregar modulo em {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    fn = getattr(module, function_name, None)
    if fn is None:
        raise RuntimeError(f"Funcao {function_name} nao encontrada em {file_path}")

    return fn


def _normalize_result(solution: str, result: Dict[str, Any]) -> Dict[str, Any]:
    if solution == "solution-a":
        return {
            "category": result["category"],
            "urgency": result["urgency"],
            "confidence": result["confidence"],
            "route": result["route"],
        }

    if solution == "solution-b":
        return {
            "category": result["category"],
            "urgency": result["urgency"],
            "confidence": result["confidence"],
            "route": result["decision"]["route"],
        }

    return {
        "category": result["classification"]["category"],
        "urgency": result["classification"]["urgency"],
        "confidence": result["classification"]["confidence"],
        "route": result["decision"]["next_step"],
    }


def run_benchmark() -> Dict[str, Any]:
    runners = {
        "solution-a": _load_function(ROOT / "solutions" / "solution-a" / "main.py", "classify_request"),
        "solution-b": _load_function(ROOT / "solutions" / "solution-b" / "main.py", "classify_request"),
        "solution-c": _load_function(ROOT / "solutions" / "solution-c" / "main.py", "process_request"),
    }

    records: List[Dict[str, Any]] = []

    for solution_name, fn in runners.items():
        for sample in SAMPLES:
            start = perf_counter()
            raw_result = fn(sample)
            elapsed_ms = (perf_counter() - start) * 1000

            normalized = _normalize_result(solution_name, raw_result)
            records.append(
                {
                    "solution": solution_name,
                    "input": sample,
                    "category": normalized["category"],
                    "urgency": normalized["urgency"],
                    "confidence": normalized["confidence"],
                    "route": normalized["route"],
                    "elapsed_ms": round(elapsed_ms, 3),
                }
            )

    summary: Dict[str, Any] = {}
    for solution_name in runners:
        rows = [row for row in records if row["solution"] == solution_name]
        avg_confidence = round(sum(float(row["confidence"]) for row in rows) / len(rows), 3)
        avg_time = round(sum(float(row["elapsed_ms"]) for row in rows) / len(rows), 3)
        escalations = sum(
            1
            for row in rows
            if row["route"] in {"triagem_humana", "revisao_humana", "escalar_humano", "solicitar_dados"}
        )

        summary[solution_name] = {
            "avg_confidence": avg_confidence,
            "avg_elapsed_ms": avg_time,
            "needs_human_intervention": escalations,
        }

    output = {
        "records": records,
        "summary": summary,
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "benchmark-output.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    comparison_md = [
        "# Comparacao automatica entre as solucoes",
        "",
        "| Solucao | Confianca media | Tempo medio (ms) | Intervencoes humanas |",
        "|---------|------------------|------------------|----------------------|",
    ]

    for solution_name, data in summary.items():
        comparison_md.append(
            f"| {solution_name} | {data['avg_confidence']} | {data['avg_elapsed_ms']} | {data['needs_human_intervention']} |"
        )

    comparison_md.extend(
        [
            "",
            "Observacao: menor numero de intervencoes humanas nao e necessariamente melhor.",
            "Uma boa estrategia deve equilibrar automacao com seguranca operacional.",
        ]
    )

    (EVIDENCE_DIR / "comparacao-solucoes.md").write_text("\n".join(comparison_md), encoding="utf-8")

    return output


if __name__ == "__main__":
    result = run_benchmark()
    print("Resumo do benchmark:")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
