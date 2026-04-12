import unittest
from pathlib import Path
import json
import sys

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from agent import StudentRiskAgent  # noqa: E402


class StudentRiskAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = StudentRiskAgent()

    def test_high_risk_case(self) -> None:
        payload = {
            "frequencia": 40,
            "nota_media": 4.0,
            "acessos_plataforma_semana": 1,
            "pendencia_financeira": True,
            "relato_estudante": "Estou desmotivado e pensando em desistir.",
        }
        result = self.agent.predict(payload)
        self.assertEqual(result.nivel_risco, "alto")
        self.assertGreaterEqual(result.score_risco, 70)
        self.assertTrue(result.explicacao)

    def test_low_risk_case(self) -> None:
        payload = {
            "frequencia": 90,
            "nota_media": 8.5,
            "acessos_plataforma_semana": 7,
            "pendencia_financeira": False,
            "relato_estudante": "Estou motivado e acompanhando bem.",
        }
        result = self.agent.predict(payload)
        self.assertEqual(result.nivel_risco, "baixo")
        self.assertLess(result.score_risco, 40)

    def test_invalid_input(self) -> None:
        payload = {
            "frequencia": -1,
            "nota_media": 8.0,
            "acessos_plataforma_semana": 2,
            "pendencia_financeira": False,
            "relato_estudante": "Texto",
        }
        with self.assertRaises(ValueError):
            self.agent.predict(payload)

    def test_batch_dataset_has_expected_keys(self) -> None:
        data_file = Path(__file__).resolve().parent.parent / "data" / "test_cases.json"
        cases = json.loads(data_file.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 5)
        for case in cases:
            self.assertIn("input", case)
            self.assertIn("esperado", case)


if __name__ == "__main__":
    unittest.main()
