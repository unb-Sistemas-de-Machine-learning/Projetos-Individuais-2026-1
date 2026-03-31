import json
import logging
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from rag import search, search_questions_by_difficulty

logger = logging.getLogger(__name__)

@dataclass
class SessionContext:
    concurso: str
    materia: str
    banca: str
    nivel: str = "desconhecido"
    trilha: list[dict] = field(default_factory=list)
    historico_respostas: list[dict] = field(default_factory=list)
    sessao_encerrada: bool = False

def _call_llm(prompt: str, system: str = "") -> str:
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=system or "Você é um assistente especializado em concursos públicos de TI.",
        ),
        contents=prompt,
    )
    
    texto = response.text.strip()
    if texto.startswith("```json"):
        texto = texto[7:]
    elif texto.startswith("```"):
        texto = texto[3:]
    
    if texto.endswith("```"):
        texto = texto[:-3]
        
    return texto.strip()

class DiagnosticoAgent:

    SYSTEM = (
        "Você é um avaliador pedagógico especializado em concursos de TI. "
        "Sua tarefa é classificar o nível do candidato com base nas respostas "
        "fornecidas, usando critérios claros e justificando a classificação."
    )

    def run(self, ctx: SessionContext) -> tuple[list[dict], str]:
        questoes = search_questions_by_difficulty(
            materia=ctx.materia,
            banca=ctx.banca,
        )

        if not questoes:
            logger.warning("Base RAG sem questões para '%s'. Gerando via LLM.", ctx.materia)
            questoes = self._gerar_questoes_fallback(ctx)

        instrucao = (
            f"📋 **Diagnóstico de nível — {ctx.materia} ({ctx.banca})**\n\n"
            "Responda as questões abaixo para calibrar sua trilha de estudos.\n"
            "Responda com **Certo/Errado** ou a **letra** da alternativa.\n\n"
        )
        for i, q in enumerate(questoes, 1):
            instrucao += f"**Questão {i} ({q.get('dificuldade', '?')}):**\n{q['text']}\n\n"

        return questoes, instrucao

    def classificar(self, ctx: SessionContext, respostas: list[str], questoes: list[dict]) -> str:
        prompt = (
            f"Matéria: {ctx.materia}\nBanca: {ctx.banca}\n\n"
            "Questões e respostas do candidato:\n"
        )
        for i, (q, r) in enumerate(zip(questoes, respostas), 1):
            prompt += f"\nQ{i} ({q.get('dificuldade')}): {q['text']}\nResposta: {r}\n"

        prompt += (
            "\n\nClassifique o nível do candidato como exatamente uma das opções: "
            "Iniciante, Intermediário ou Avançado.\n"
            "Responda APENAS em JSON com o formato:\n"
            '{"nivel": "...", "justificativa": "..."}'
        )

        resposta_llm = _call_llm(prompt, self.SYSTEM)
        try:
            data = json.loads(resposta_llm)
            ctx.nivel = data.get("nivel", "Iniciante")
            return (
                f"🎯 **Nível identificado: {ctx.nivel}**\n\n"
                f"💡 *Justificativa:* {data.get('justificativa', '')}"
            )
        except json.JSONDecodeError:
            ctx.nivel = "Iniciante"
            return f"🎯 **Nível identificado: Iniciante** (classificação padrão)"

    def _gerar_questoes_fallback(self, ctx: SessionContext) -> list[dict]:
        prompt = (
            f"Gere 3 questões de {ctx.materia} no estilo {ctx.banca}, "
            "uma fácil, uma média e uma difícil. "
            "Responda APENAS em JSON:\n"
            '[{"text": "...", "dificuldade": "facil"}, ...]'
        )
        resposta = _call_llm(prompt)
        try:
            return json.loads(resposta)
        except Exception:
            return [{"text": f"Questão sobre {ctx.materia}", "dificuldade": "media"}]

class RecomendadorAgent:

    SYSTEM = (
        "Você é um especialista em preparação para concursos públicos de TI. "
        "Seu papel é recomendar trilhas de estudos personalizadas, sempre "
        "explicando o motivo de cada recomendação de forma clara e didática."
    )

    def run(self, ctx: SessionContext) -> str:
        docs_rag = search(
            query=f"tópicos essenciais {ctx.materia} {ctx.concurso}",
            materia=ctx.materia,
            tipo="resumo",
            n_results=3,
        )
        contexto_rag = "\n".join(d["text"] for d in docs_rag) if docs_rag else ""

        prompt = (
            f"Candidato: nível {ctx.nivel}, concurso {ctx.concurso}, "
            f"matéria {ctx.materia}, banca {ctx.banca}.\n\n"
        )
        if contexto_rag:
            prompt += f"Conteúdo de referência da base de conhecimento:\n{contexto_rag}\n\n"

        prompt += (
            "Gere uma trilha de estudos com 5 a 7 tópicos ordenados por pré-requisito "
            "e frequência de cobrança em provas. Para cada tópico, inclua uma "
            "justificativa explícita de por que ele deve ser estudado nessa posição.\n\n"
            "Responda APENAS em JSON:\n"
            '[{"topico": "...", "justificativa": "...", "concluido": false}, ...]'
        )

        resposta = _call_llm(prompt, self.SYSTEM)
        try:
            ctx.trilha = json.loads(resposta)
        except json.JSONDecodeError:
            ctx.trilha = [{"topico": ctx.materia, "justificativa": "Tópico central da matéria.", "concluido": False}]

        return self._formatar_trilha(ctx)

    def _formatar_trilha(self, ctx: SessionContext) -> str:
        output = (
            f"📚 **Trilha de estudos — {ctx.materia} ({ctx.banca})**\n"
            f"*Nível: {ctx.nivel} | Concurso: {ctx.concurso}*\n\n"
        )
        for i, item in enumerate(ctx.trilha, 1):
            status = "✅" if item.get("concluido") else "📌"
            output += f"{status} **{i}. {item['topico']}**\n"
            output += f"   💡 *{item['justificativa']}*\n\n"
        return output

class GeradorAgent:

    SYSTEM = (
        "Você é um especialista em elaboração de questões para concursos públicos de TI. "
        "Crie questões fiéis ao estilo da banca especificada, incluindo sempre "
        "o gabarito e uma explicação detalhada da resposta correta."
    )

    def run(self, ctx: SessionContext, topico: str | None = None) -> str:
        if not topico:
            proximos = [t for t in ctx.trilha if not t.get("concluido")]
            topico = proximos[0]["topico"] if proximos else ctx.materia

        exemplos = search(
            query=topico,
            banca=ctx.banca,
            materia=ctx.materia,
            tipo="questao",
            n_results=2,
        )
        ctx_exemplos = "\n".join(e["text"] for e in exemplos) if exemplos else ""

        prompt = (
            f"Gere uma questão de {topico} (matéria: {ctx.materia}) "
            f"no estilo da banca {ctx.banca}, nível {ctx.nivel}.\n"
        )
        if ctx_exemplos:
            prompt += f"\nExemplos de questões dessa banca para referência:\n{ctx_exemplos}\n"

        prompt += (
            "\nA questão deve ser inédita. Inclua gabarito e justificativa.\n"
            "MUITO IMPORTANTE: Se a banca for de múltipla escolha (ex: FCC, FGV, VUNESP), "
            "você OBRIGATORIAMENTE deve digitar as alternativas (A, B, C, D, E) "
            "dentro do texto do campo 'enunciado'.\n"
            "Responda APENAS em JSON:\n"
            '{"enunciado": "...", "gabarito": "...", "justificativa": "..."}'
        )

        resposta = _call_llm(prompt, self.SYSTEM)
        try:
            data = json.loads(resposta)
            return (
                f"❓ **Questão — {topico}** *(estilo {ctx.banca})*\n\n"
                f"{data['enunciado']}"
            )
        except json.JSONDecodeError:
            return f"❓ **Questão sobre {topico}:**\n\n{resposta}"

class AvaliadorAgent:

    SYSTEM = (
        "Você é um professor especializado em concursos de TI. "
        "Corrija a resposta do candidato de forma pedagógica, explicando "
        "o raciocínio correto e identificando exatamente onde está a lacuna "
        "de conhecimento para que o candidato possa melhorar."
    )

    def run(
        self,
        ctx: SessionContext,
        questao: str,
        resposta_candidato: str,
        gabarito: str,
        topico: str,
    ) -> str:
        prompt = (
            f"Questão: {questao}\n"
            f"Gabarito correto: {gabarito}\n"
            f"Resposta do candidato: {resposta_candidato}\n"
            f"Tópico: {topico} | Matéria: {ctx.materia} | Banca: {ctx.banca}\n\n"
            "Avalie a resposta. Explique se está correta ou não, o raciocínio "
            "correto e identifique a lacuna de conhecimento (se houver).\n"
            "Responda APENAS em JSON:\n"
            '{"acertou": true/false, "explicacao": "...", "lacuna": "...", "sugestao": "..."}'
        )

        resposta = _call_llm(prompt, self.SYSTEM)
        try:
            data = json.loads(resposta)
        except json.JSONDecodeError:
            ctx.historico_respostas.append({
                "topico": topico,
                "acertou": False,  
                "lacuna": "O agente não conseguiu formatar o laudo."
            })
            return f"📝 **Avaliação:**\n\n{resposta}"

        ctx.historico_respostas.append({
            "topico": topico,
            "acertou": data.get("acertou", False),
            "lacuna": data.get("lacuna", ""),
        })

        if data.get("acertou"):
            for item in ctx.trilha:
                if item["topico"] == topico:
                    item["concluido"] = True

        icone = "✅" if data.get("acertou") else "❌"
        output = f"{icone} **{'Correto!' if data.get('acertou') else 'Incorreto.'}**\n\n"
        output += f"📖 **Explicação:** {data.get('explicacao', '')}\n\n"

        if not data.get("acertou"):
            output += f"🔍 **Lacuna identificada:** {data.get('lacuna', '')}\n\n"
            output += f"💡 **Sugestão:** {data.get('sugestao', '')}\n"

        return output

    def resumo_sessao(self, ctx: SessionContext) -> str:
        total = len(ctx.historico_respostas)
        acertos = sum(1 for r in ctx.historico_respostas if r.get("acertou"))
        pendentes = [t for t in ctx.trilha if not t.get("concluido")]

        output = (
            "---\n"
            f"## 📊 Resumo da Sessão — {ctx.materia}\n\n"
            f"**Desempenho:** {acertos}/{total} questões corretas "
            f"({'%.0f' % (acertos/total*100 if total else 0)}%)\n\n"
        )

        lacunas = [r["lacuna"] for r in ctx.historico_respostas if r.get("lacuna")]
        if lacunas:
            output += "**Lacunas identificadas:**\n"
            for lacuna in lacunas:
                output += f"- {lacuna}\n"
            output += "\n"

        if pendentes:
            output += "**Próximos tópicos na trilha:**\n"
            for t in pendentes[:3]:
                output += f"- {t['topico']}\n"

        ctx.sessao_encerrada = True
        return output
