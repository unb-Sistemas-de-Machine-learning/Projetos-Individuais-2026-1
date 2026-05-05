import json
import time
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def run_benchmark():
    samples = [
        ("erro no webhook", "nao consigo integrar webhook, retorna erro 500"),
        ("cobranca indevida", "foi cobrado duas vezes e preciso de reembolso"),
        ("cancelar plano", "quero cancelar minha conta por favor"),
    ]

    a = _load(ROOT / "solutions" / "solution-a" / "main.py")
    b = _load(ROOT / "solutions" / "solution-b" / "main.py")
    c = _load(ROOT / "solutions" / "solution-c" / "main.py")

    rows = []
    for subject, content in samples:
        for name, fn in [
            ("solution-a", lambda: a.classify_email(subject, content)),
            ("solution-b", lambda: b.classify_email(subject, content)),
            ("solution-c", lambda: c.process_email(subject, content)),
        ]:
            t0 = time.perf_counter()
            out = fn()
            dt = (time.perf_counter() - t0) * 1000
            rows.append({"solution": name, "time_ms": round(dt, 3), "output": out})

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    result = {"runs": rows}
    (EVIDENCE / "benchmark-output.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run_benchmark(), ensure_ascii=False, indent=2))
