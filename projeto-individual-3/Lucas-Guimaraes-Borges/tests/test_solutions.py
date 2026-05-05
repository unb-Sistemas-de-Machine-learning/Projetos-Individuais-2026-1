import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class TestSolutions(unittest.TestCase):
    def test_solution_a_cancelamento_tem_prioridade(self):
        module = _load_module(ROOT / "solutions" / "solution-a" / "main.py")
        result = module.classify_email("quero cancelar", "quero cancelar meu plano hoje")
        self.assertEqual(result["categoria"], "cancelamento")
        self.assertEqual(result["urgencia"], 7)

    def test_solution_b_financeiro(self):
        module = _load_module(ROOT / "solutions" / "solution-b" / "main.py")
        result = module.classify_email("fatura", "houve cobranca duplicada no pagamento")
        self.assertEqual(result["categoria"], "financeiro")
        self.assertGreaterEqual(result["urgencia"], 7)

    def test_solution_c_escalonamento(self):
        module = _load_module(ROOT / "solutions" / "solution-c" / "main.py")
        result = module.process_email("oi", "bom dia")
        self.assertEqual(result["meta"]["decision"], "escalar_humano")


if __name__ == "__main__":
    unittest.main()
