import json
import os
from dataclasses import dataclass
from typing import Dict, List

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


RISK_KEYWORDS = {
    "desistir": 12,
    "desmotivado": 10,
    "trancar": 10,
    "cansado": 6,
    "perdido": 8,
    "divida": 7,
    "trabalho": 4,
}

PROTECTION_KEYWORDS = {
    "motivado": 6,
    "mentoria": 5,
    "acompanhando": 4,
    "organizado": 4,
    "focado": 5,
    "ajudando": 4,
}


@dataclass
class AgentOutput:
    nivel_risco: str
    score_risco: int
    fatores_risco: List[str]
    fatores_protecao: List[str]
    explicacao: str
    acoes_recomendadas: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "nivel_risco": self.nivel_risco,
            "score_risco": self.score_risco,
            "fatores_risco": self.fatores_risco,
            "fatores_protecao": self.fatores_protecao,
            "explicacao": self.explicacao,
            "acoes_recomendadas": self.acoes_recomendadas,
        }


class StudentRiskAgent:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if (self.api_key and OpenAI) else None

    def predict(self, payload: Dict[str, object]) -> AgentOutput:
        self._validate(payload)

        score, risk_factors, protection_factors = self._calculate_score(payload)
        risk_level = self._classify(score)

        explanation = self._build_explanation(
            payload=payload,
            score=score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            protection_factors=protection_factors,
        )

        actions = self._recommended_actions(risk_level)

        return AgentOutput(
            nivel_risco=risk_level,
            score_risco=score,
            fatores_risco=risk_factors,
            fatores_protecao=protection_factors,
            explicacao=explanation,
            acoes_recomendadas=actions,
        )

    def _validate(self, payload: Dict[str, object]) -> None:
        required = [
            "frequencia",
            "nota_media",
            "acessos_plataforma_semana",
            "pendencia_financeira",
            "relato_estudante",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Campos obrigatorios ausentes: {missing}")

        if not 0 <= float(payload["frequencia"]) <= 100:
            raise ValueError("frequencia deve estar entre 0 e 100")
        if not 0 <= float(payload["nota_media"]) <= 10:
            raise ValueError("nota_media deve estar entre 0 e 10")
        if int(payload["acessos_plataforma_semana"]) < 0:
            raise ValueError("acessos_plataforma_semana nao pode ser negativo")

    def _calculate_score(self, payload: Dict[str, object]) -> tuple[int, List[str], List[str]]:
        score = 0
        risk_factors: List[str] = []
        protection_factors: List[str] = []

        frequencia = float(payload["frequencia"])
        nota_media = float(payload["nota_media"])
        acessos = int(payload["acessos_plataforma_semana"])
        pendencia = bool(payload["pendencia_financeira"])
        relato = str(payload["relato_estudante"]).lower()

        if frequencia < 60:
            score += 28
            risk_factors.append("Frequencia baixa (<60%)")
        elif frequencia < 75:
            score += 24
            risk_factors.append("Frequencia moderada (60-74%)")
        else:
            protection_factors.append("Boa frequencia (>=75%)")

        if nota_media < 5:
            score += 24
            risk_factors.append("Nota media baixa (<5)")
        elif nota_media < 7:
            score += 12
            risk_factors.append("Nota media intermediaria (5-6.9)")
        else:
            protection_factors.append("Desempenho academico adequado (>=7)")

        if acessos <= 2:
            score += 18
            risk_factors.append("Baixo engajamento na plataforma (<=2 acessos/semana)")
        elif acessos <= 4:
            score += 16
            risk_factors.append("Engajamento intermediario (3-4 acessos/semana)")
        else:
            protection_factors.append("Bom engajamento na plataforma (>4 acessos/semana)")

        if pendencia:
            score += 15
            risk_factors.append("Pendencia financeira informada")

        for keyword, weight in RISK_KEYWORDS.items():
            if keyword in relato:
                score += weight
                risk_factors.append(f"Relato com sinal de risco: '{keyword}'")

        for keyword, weight in PROTECTION_KEYWORDS.items():
            if keyword in relato:
                score -= weight
                protection_factors.append(f"Relato com sinal de protecao: '{keyword}'")

        score = max(0, min(100, score))
        return score, risk_factors, protection_factors

    def _classify(self, score: int) -> str:
        if score >= 70:
            return "alto"
        if score >= 40:
            return "moderado"
        return "baixo"

    def _build_explanation(
        self,
        payload: Dict[str, object],
        score: int,
        risk_level: str,
        risk_factors: List[str],
        protection_factors: List[str],
    ) -> str:
        if self.client:
            llm_text = self._build_explanation_with_llm(
                payload=payload,
                score=score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                protection_factors=protection_factors,
            )
            if llm_text:
                return llm_text

        return self._build_explanation_fallback(score, risk_level, risk_factors, protection_factors)

    def _build_explanation_with_llm(
        self,
        payload: Dict[str, object],
        score: int,
        risk_level: str,
        risk_factors: List[str],
        protection_factors: List[str],
    ) -> str | None:
        if not self.client:
            return None

        prompt = {
            "dados": payload,
            "score": score,
            "nivel_risco": risk_level,
            "fatores_risco": risk_factors,
            "fatores_protecao": protection_factors,
            "instrucao": (
                "Explique em portugues simples porque o risco foi classificado nesse nivel. "
                "Inclua 1 paragrafo com justificativa e 1 paragrafo com orientacao para intervencao."
            ),
        }

        try:
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": "Voce e um assistente educacional que gera explicacoes objetivas e eticas.",
                    },
                    {
                        "role": "user",
                        "content": json.dumps(prompt, ensure_ascii=True),
                    },
                ],
                temperature=0.2,
                max_output_tokens=220,
            )
            return response.output_text.strip() if response.output_text else None
        except Exception:
            return None

    def _build_explanation_fallback(
        self,
        score: int,
        risk_level: str,
        risk_factors: List[str],
        protection_factors: List[str],
    ) -> str:
        principais_riscos = "; ".join(risk_factors[:3]) if risk_factors else "Nenhum fator critico detectado"
        principais_protecoes = (
            "; ".join(protection_factors[:2]) if protection_factors else "Sem fatores de protecao relevantes"
        )

        return (
            f"Classificacao de risco {risk_level.upper()} com score {score}/100. "
            f"A decisao foi influenciada por: {principais_riscos}. "
            f"Fatores de protecao identificados: {principais_protecoes}. "
            "A classificacao deve orientar acolhimento pedagogico e plano de acompanhamento individual."
        )

    def _recommended_actions(self, risk_level: str) -> List[str]:
        if risk_level == "alto":
            return [
                "Agendar atendimento com coordenacao em ate 48h",
                "Definir plano individual de recuperacao academica",
                "Encaminhar para apoio psicopedagogico e financeiro",
            ]
        if risk_level == "moderado":
            return [
                "Realizar mentoria semanal por 30 dias",
                "Monitorar frequencia e atividades na plataforma",
                "Acionar professor orientador se houver piora",
            ]
        return [
            "Manter acompanhamento mensal",
            "Reforcar estrategias de estudo e engajamento",
            "Reconhecer desempenho para manter motivacao",
        ]
