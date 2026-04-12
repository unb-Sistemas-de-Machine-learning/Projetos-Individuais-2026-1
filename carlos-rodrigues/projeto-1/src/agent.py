import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import get_gemini_model

DISPENSA_LIMITES_ART75_II_FALLBACK = {
    2026: 65492.11,
}
DEFAULT_LIMITES_URL = (
    "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/decreto/d12807.htm"
)
NEAR_LIMIT_RATIO = 0.9

RISK_ORDER = {"baixo": 0, "medio": 1, "alto": 2}
VALID_CATEGORIES = {"legal", "financeiro", "documental", "descritivo"}

GENERIC_OBJECT_PATTERNS = [
    r"MAO\s+DE\s+OBRA",
    r"APOIO\s+A\s+S\s+ATIVIDADES",
    r"SERVICOS\s+DIVERSOS",
    r"EXECUCAO\s+E\s+APOIO\s+AS\s+ATIVIDADES",
    r"OBJETO\s+GENERICO",
]

FRAGMENTATION_PATTERNS = [
    r"FRACIONAMENTO",
    r"PARCELAMENTO",
    r"MESMO\s+FORNECEDOR",
    r"MESMA\s+EMPRESA",
    r"REPETID",
]


class ProcurementAnomalyAgent:
    def __init__(self):
        self.model = get_gemini_model()
        self.dispensa_limites_art75_ii = self._load_dispensa_limits()

    def preprocess_text(self, texto):
        if not texto:
            return ""

        texto_limpo = re.sub(r"\s+", " ", texto)
        return texto_limpo.strip()

    def extract_features(self, texto, data_referencia=None):
        texto_upper = texto.upper()
        valor = self._extract_currency_value(texto)
        ano = self._extract_year(data_referencia)
        limite_dispensa, ano_referencia = self._resolve_dispensa_limit(ano)

        is_dispensa = "DISPENSA" in texto_upper
        is_adesao_ata = bool(
            re.search(r"ADES[ÃA]O", texto_upper)
            and re.search(r"ATA\s+DE\s+REGISTRO\s+DE\s+PRECOS", texto_upper)
        )
        objeto_generico = any(
            re.search(pattern, texto_upper) for pattern in GENERIC_OBJECT_PATTERNS
        )

        dentro_limite = None
        if is_dispensa and valor is not None and limite_dispensa is not None:
            dentro_limite = valor <= limite_dispensa

        valor_alto = valor is not None and valor > 1_000_000

        near_limit = False
        if is_dispensa and valor is not None and limite_dispensa:
            near_limit = limite_dispensa * NEAR_LIMIT_RATIO <= valor <= limite_dispensa

        cnpjs = re.findall(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
        possible_fragmentation_signal = bool(
            any(re.search(pattern, texto_upper) for pattern in FRAGMENTATION_PATTERNS)
            or len(set(cnpjs)) > 1
        )

        rule_data_missing = bool(
            is_adesao_ata
            and not re.search(
                r"\b(QUANTIDADE|PERCENTUAL|%|ITEM|ITENS|LIMITE)\b",
                texto_upper,
            )
        )

        return {
            "is_dispensa": is_dispensa,
            "is_adesao_ata": is_adesao_ata,
            "valor": valor,
            "limite_dispensa": limite_dispensa,
            "ano_limite": ano_referencia,
            "dentro_limite": dentro_limite,
            "objeto_generico": objeto_generico,
            "valor_alto": valor_alto,
            "near_limit": near_limit,
            "possible_fragmentation_signal": possible_fragmentation_signal,
            "rule_data_missing": rule_data_missing,
        }

    def evaluate_hard_rules(self, features):
        if (
            features.get("is_dispensa")
            and features.get("valor") is not None
            and features.get("limite_dispensa") is not None
            and features.get("valor") > features.get("limite_dispensa")
        ):
            score = self.compute_risk_score(features)
            nivel = self._risk_from_score(score)
            valor_fmt = self._format_brl(features["valor"])
            limite_fmt = self._format_brl(features["limite_dispensa"])
            ano_ref = features.get("ano_limite")
            return {
                "tem_anomalia": True,
                "nivel_risco": self.max_risk("medio", nivel),
                "categoria": "legal",
                "tipo": "Possivel extrapolacao do limite de dispensa",
                "justificativa": (
                    f"Valor identificado (R$ {valor_fmt}) acima da referencia do Art. 75, II "
                    f"({ano_ref}: R$ {limite_fmt}). Requer verificacao documental."
                ),
                "confianca": 0.9,
            }

        return None

    def call_llm(self, texto, features):
        contexto_legal = self._build_legal_context_line(features)
        tipo_contratacao = "dispensa" if features.get("is_dispensa") else "outro"
        valor = features.get("valor")
        limite = features.get("limite_dispensa")
        dentro_limite = features.get("dentro_limite")
        objeto_generico = features.get("objeto_generico")

        valor_txt = f"R$ {self._format_brl(valor)}" if valor is not None else "nao identificado"
        limite_txt = (
            f"R$ {self._format_brl(limite)}" if limite is not None else "nao disponivel"
        )
        if dentro_limite is None:
            dentro_limite_txt = "nao aplicavel"
        else:
            dentro_limite_txt = "sim" if dentro_limite else "nao"

        prompt = f"""
Voce e um analista de risco em contratacoes publicas brasileiras.
Seu objetivo e apontar apenas sinais de atencao com cautela.

Regras de resposta:
- Nao afirmar ilegalidade sem evidencia clara.
- Evitar linguagem acusatoria; usar termos como "possivel inconsistencia" e "requer verificacao".
- Ausencia de justificativa no extrato, por si so, nao e anomalia.
- Valores altos/baixos isoladamente nao provam irregularidade.
- Se houver referencia legal no contexto abaixo, use essa referencia antes de qualquer outra.
- Se faltar dado legal atualizado, nao invente numero; sinalize incerteza e reduza confianca.

Features extraidas automaticamente:
- Tipo de contratacao: {tipo_contratacao}
- Valor identificado: {valor_txt}
- Limite legal: {limite_txt}
- Dentro do limite: {dentro_limite_txt}
- Possui objeto generico: {"sim" if objeto_generico else "nao"}
- Valor proximo do limite legal: {"sim" if features.get("near_limit") else "nao"}
- Possivel sinal de fracionamento: {"sim" if features.get("possible_fragmentation_signal") else "nao"}

Contexto legal automatico:
{contexto_legal}

Regra juridica adicional:
- Proximidade com limite legal, sozinha, NAO e anomalia.
- Se faltarem dados legais/quantitativos essenciais, NAO inferir irregularidade.

Retorne APENAS um JSON valido com o formato:
{{
    "nivel_risco": "baixo" ou "medio" ou "alto",
    "categoria": "legal" ou "financeiro" ou "documental" ou "descritivo",
  "tipo": "string",
  "justificativa": "string",
  "confianca": numero entre 0 e 1
}}

Texto:
\"\"\"
{texto}
\"\"\"
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.1},
            )
        except Exception as exc:
            return self._fallback_from_llm_error(exc)

        raw_text = (response.text or "").strip()
        return self._parse_llm_json(raw_text)

    def _fallback_from_llm_error(self, exc):
        mensagem = str(exc)
        mensagem_upper = mensagem.upper()

        if "429" in mensagem_upper or "RESOURCE_EXHAUSTED" in mensagem_upper:
            justificativa = (
                "Cota da API Gemini excedida (erro 429). "
                "Tente novamente mais tarde."
            )
        elif "401" in mensagem_upper or "403" in mensagem_upper:
            justificativa = (
                "Falha de autenticacao/autorizacao na API Gemini. "
                "Verifique GEMINI_API_KEY e permissoes da conta."
            )
        else:
            justificativa = f"Falha ao chamar API Gemini: {mensagem}"

        return {
            "tem_anomalia": False,
            "nivel_risco": "baixo",
            "categoria": "documental",
            "tipo": "Falha de integracao",
            "justificativa": justificativa,
            "confianca": 0.0,
        }

    def _parse_llm_json(self, raw_text):
        default_result = {
            "tem_anomalia": False,
            "nivel_risco": "baixo",
            "categoria": "documental",
            "tipo": "Indefinido",
            "justificativa": "Nao foi possivel interpretar a resposta do modelo.",
            "confianca": 0.0,
        }

        if not raw_text:
            return default_result

        cleaned = raw_text.strip()
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(1)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                **default_result,
                "justificativa": (
                    "Resposta da API em formato inesperado;"
                ),
            }

        nivel_risco = self._normalize_risk_level(parsed.get("nivel_risco", "baixo"))
        tem_anomalia = parsed.get("tem_anomalia")
        if tem_anomalia is None:
            tem_anomalia = nivel_risco in {"medio", "alto"}

        return {
            "tem_anomalia": bool(tem_anomalia),
            "nivel_risco": nivel_risco,
            "categoria": self._normalize_category(parsed.get("categoria", "documental")),
            "tipo": str(parsed.get("tipo", "Indefinido")),
            "justificativa": str(parsed.get("justificativa", "Sem justificativa.")),
            "confianca": self._clamp_confidence(parsed.get("confianca", 0.0)),
        }

    def compute_risk_score(self, features):
        score = 0
        if features.get("is_dispensa") and features.get("dentro_limite") is False:
            score += 50
        if features.get("objeto_generico"):
            score += 20
        if features.get("valor_alto"):
            score += 20
        if features.get("near_limit") and features.get("possible_fragmentation_signal"):
            score += 20
        return min(score, 100)

    @staticmethod
    def max_risk(r1, r2):
        return r1 if RISK_ORDER.get(r1, 0) >= RISK_ORDER.get(r2, 0) else r2

    def apply_rules(self, texto, resultado_llm, features):
        texto_upper = texto.upper()
        resultado = dict(resultado_llm)

        risk_score = self.compute_risk_score(features)
        risk_by_features = self._risk_from_score(risk_score)
        risk_atual = self._normalize_risk_level(resultado.get("nivel_risco", "baixo"))
        risk_final = self.max_risk(risk_atual, risk_by_features)

        bonus = 0
        regras_disparadas = []

        if "INEXIGIBILIDADE" in texto_upper:
            bonus += 10
            regras_disparadas.append("termo INEXIGIBILIDADE encontrado")

        if "ADITIVO" in texto_upper:
            bonus += 8
            regras_disparadas.append("termo ADITIVO encontrado")

        risk_score = min(100, risk_score + bonus)
        risk_final = self.max_risk(risk_final, self._risk_from_score(risk_score))

        if features.get("near_limit") and not features.get("possible_fragmentation_signal"):
            risk_score = min(risk_score, 29)
            risk_final = "baixo"

        if features.get("rule_data_missing"):
            risk_score = min(risk_score, 29)
            risk_final = "baixo"

        confianca_base = self._clamp_confidence(resultado.get("confianca", 0.0))
        confianca_por_score = self._clamp_confidence(risk_score / 100)
        resultado["confianca"] = max(confianca_base, confianca_por_score)
        if features.get("rule_data_missing"):
            resultado["confianca"] = min(resultado["confianca"], 0.6)
        resultado["nivel_risco"] = risk_final

        explicit_legal_inconsistency = (
            features.get("is_dispensa") and features.get("dentro_limite") is False
        )
        resultado["tem_anomalia"] = bool(
            explicit_legal_inconsistency or risk_score >= 50
        )
        resultado["categoria"] = self._infer_category(features, resultado.get("categoria"))

        if features.get("rule_data_missing"):
            complemento = "Nao e possivel verificar com os dados disponiveis."
            justificativa_atual = str(resultado.get("justificativa", "")).strip()
            if complemento.lower() not in justificativa_atual.lower():
                resultado["justificativa"] = f"{justificativa_atual} {complemento}".strip()
            if not resultado.get("tipo") or resultado.get("tipo") == "Indefinido":
                resultado["tipo"] = "Dados insuficientes para conclusao"

        if features.get("near_limit") and not features.get("possible_fragmentation_signal"):
            complemento = "Proximidade com limite legal, isoladamente, nao configura anomalia."
            justificativa_atual = str(resultado.get("justificativa", "")).strip()
            if complemento.lower() not in justificativa_atual.lower():
                resultado["justificativa"] = f"{justificativa_atual} {complemento}".strip()

        if regras_disparadas:
            if not resultado.get("tem_anomalia", False) and resultado.get("tipo", "") == "Indefinido":
                resultado["tipo"] = "Sinal de atencao heuristico"

            detalhe_regras = "; ".join(regras_disparadas)
            justificativa_atual = str(resultado.get("justificativa", "")).strip()
            if justificativa_atual:
                resultado["justificativa"] = (
                    f"{justificativa_atual} Regras adicionais: {detalhe_regras}."
                )
            else:
                resultado["justificativa"] = f"Regras adicionais: {detalhe_regras}."

        return resultado

    def run_pipeline(self, texto, data_referencia=None):
        texto_limpo = self.preprocess_text(texto)
        features = self.extract_features(texto_limpo, data_referencia)
        hard_result = self.evaluate_hard_rules(features)
        if hard_result:
            return hard_result

        resultado_llm = self.call_llm(texto_limpo, features)
        resultado_final = self.apply_rules(texto_limpo, resultado_llm, features)
        return resultado_final

    def _build_legal_context_line(self, features):
        limite = features.get("limite_dispensa")
        ano_referencia = features.get("ano_limite")
        if limite is None:
            return "Sem limite legal carregado automaticamente para Art. 75, II."

        limite_fmt = self._format_brl(limite)
        return (
            f"Art. 75, II referencia para {ano_referencia}: R$ {limite_fmt}. "
        )

    def _resolve_dispensa_limit(self, ano):
        if not self.dispensa_limites_art75_ii:
            return None, None

        if ano in self.dispensa_limites_art75_ii:
            return self.dispensa_limites_art75_ii[ano], ano

        anos_disponiveis = sorted(self.dispensa_limites_art75_ii.keys())
        anos_ate_ano = [a for a in anos_disponiveis if ano is not None and a <= ano]
        if anos_ate_ano:
            ano_referencia = anos_ate_ano[-1]
            return self.dispensa_limites_art75_ii[ano_referencia], ano_referencia

        ano_referencia = anos_disponiveis[-1]
        return self.dispensa_limites_art75_ii[ano_referencia], ano_referencia

    @staticmethod
    def _risk_from_score(score):
        if score >= 70:
            return "alto"
        if score >= 30:
            return "medio"
        return "baixo"

    @staticmethod
    def _normalize_category(categoria):
        categoria_txt = str(categoria).strip().lower()
        if categoria_txt in VALID_CATEGORIES:
            return categoria_txt
        return "documental"

    def _infer_category(self, features, categoria_atual):
        categoria = self._normalize_category(categoria_atual)
        if features.get("rule_data_missing"):
            return "documental"
        if features.get("is_dispensa") and features.get("dentro_limite") is False:
            return "legal"
        if features.get("valor_alto"):
            return "financeiro"
        if features.get("objeto_generico"):
            return "descritivo"
        return categoria

    def _load_dispensa_limits(self):
        limites = dict(DISPENSA_LIMITES_ART75_II_FALLBACK)

        url = os.getenv("LEI_LIMITES_URL", DEFAULT_LIMITES_URL)
        html = self._fetch_text(url)
        if not html:
            return limites

        valor_art75_ii = self._extract_art75_ii_value(html)
        ano_vigencia = self._extract_vigencia_year(html)

        if valor_art75_ii is not None and ano_vigencia is not None:
            limites[ano_vigencia] = valor_art75_ii

        return limites

    @staticmethod
    def _fetch_text(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=10) as response:
                return response.read().decode("utf-8", errors="ignore")
        except (HTTPError, URLError, TimeoutError, ValueError):
            return None

    @staticmethod
    def _extract_art75_ii_value(texto):
        patterns = [
            r"Art\.\s*75,\s*caput,\s*inciso\s*II\s*\|\s*R\$\s*([\d\.]+,\d{2})",
            r"Art\.\s*75[^\n]{0,120}inciso\s*II[\s\S]{0,150}?R\$\s*([\d\.]+,\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE)
            if not match:
                continue
            numero_txt = match.group(1).replace(".", "").replace(",", ".")
            try:
                return float(numero_txt)
            except ValueError:
                continue

        return None

    @staticmethod
    def _extract_vigencia_year(texto):
        match_vigencia = re.search(
            r"entra em vigor em\s*1[ºo]?\s*de\s*janeiro\s*de\s*(\d{4})",
            texto,
            re.IGNORECASE,
        )
        if match_vigencia:
            return int(match_vigencia.group(1))

        match_decreto = re.search(r"DECRETO\s*N[ºO]?\s*[\d\.]+,\s*DE\s*\d{1,2}\s*DE\s*\w+\s*DE\s*(\d{4})", texto, re.IGNORECASE)
        if match_decreto:
            return int(match_decreto.group(1)) + 1

        return None

    @staticmethod
    def _format_brl(valor):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _extract_currency_value(texto):
        prioridade_padroes = [
            r"VALOR\s+GLOBAL[\s\S]{0,80}?R\$\s*([\d\.]+,\d{2})",
            r"VALOR\s+TOTAL[\s\S]{0,80}?R\$\s*([\d\.]+,\d{2})",
            r"VALOR\s+DO\s+CONTRATO[\s\S]{0,80}?R\$\s*([\d\.]+,\d{2})",
        ]

        for pattern in prioridade_padroes:
            matches = re.findall(pattern, texto, re.IGNORECASE)
            valor = ProcurementAnomalyAgent._parse_brl_values(matches)
            if valor is not None:
                return valor

        matches = re.findall(r"R\$\s*([\d\.]+,\d{2})", texto, re.IGNORECASE)
        return ProcurementAnomalyAgent._parse_brl_values(matches)

    @staticmethod
    def _parse_brl_values(matches):
        if not matches:
            return None

        valores = []
        for match in matches:
            numero_txt = str(match).replace(".", "").replace(",", ".")
            try:
                valores.append(float(numero_txt))
            except ValueError:
                continue

        if not valores:
            return None

        return max(valores)

    @staticmethod
    def _extract_year(data_referencia):
        if not data_referencia:
            return None
        match = re.match(r"(\d{4})-\d{2}-\d{2}", str(data_referencia))
        if not match:
            return None
        return int(match.group(1))

    @staticmethod
    def _normalize_risk_level(nivel):
        nivel_txt = str(nivel).strip().lower()
        if nivel_txt in {"baixo", "medio", "alto"}:
            return nivel_txt
        return "baixo"

    @staticmethod
    def _clamp_confidence(valor):
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(1.0, numero))
