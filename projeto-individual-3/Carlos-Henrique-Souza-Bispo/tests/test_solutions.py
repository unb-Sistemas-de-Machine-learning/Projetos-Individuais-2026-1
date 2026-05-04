import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Nao foi possivel carregar modulo: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSolutions(unittest.TestCase):
    def test_solution_a_classifies_support(self):
        module = _load_module(ROOT / "solutions" / "solution-a" / "main.py")
        result = module.classify_request("Nao consigo fazer login no portal, preciso urgente")

        self.assertEqual(result["category"], "suporte_tecnico")
        self.assertEqual(result["urgency"], "alta")
        self.assertGreaterEqual(result["confidence"], 0.55)

    def test_solution_b_uses_knowledge_base(self):
        module = _load_module(ROOT / "solutions" / "solution-b" / "main.py")
        result = module.classify_request("Preciso da segunda via do boleto da mensalidade")

        self.assertEqual(result["category"], "financeiro")
        self.assertEqual(result["retrieval"]["policy_id"], "FIN-002")
        self.assertGreaterEqual(result["confidence"], 0.6)

    def test_solution_c_escalates_low_confidence(self):
        module = _load_module(ROOT / "solutions" / "solution-c" / "main.py")
        result = module.process_request("Oi, tudo bem?")

        self.assertEqual(result["classification"]["category"], "indefinido")
        self.assertEqual(result["decision"]["next_step"], "escalar_humano")

    def test_solution_c_requests_ra_for_financial(self):
        module = _load_module(ROOT / "solutions" / "solution-c" / "main.py")
        result = module.process_request("Preciso renegociar minha mensalidade urgente")

        self.assertEqual(result["classification"]["category"], "financeiro")
        self.assertIn("ra", result["validation"]["missing_fields"])
        self.assertEqual(result["decision"]["next_step"], "solicitar_dados")

    def test_benchmark_script_generates_outputs(self):
        module = _load_module(ROOT / "src" / "run_benchmark.py")
        result = module.run_benchmark()

        self.assertIn("summary", result)
        self.assertTrue((ROOT / "docs" / "evidence" / "benchmark-output.json").exists())
        self.assertTrue((ROOT / "docs" / "evidence" / "comparacao-solucoes.md").exists())


if __name__ == "__main__":
    unittest.main()
