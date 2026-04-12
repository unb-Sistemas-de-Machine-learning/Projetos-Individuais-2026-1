import os
import json
import pickle
import faiss
import re
from datetime import datetime
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

MEMORY_DIR   = "student_memory"
MEMORY_FILE  = os.path.join(MEMORY_DIR, "student_profile.json")
GROQ_MODEL   = "llama-3.3-70b-versatile"
TOP_K_CHUNKS = 5
MAX_TOKENS   = 1024


# ══════════════════════════════════════════════════════════
#  MEMÓRIA DO ALUNO
# ══════════════════════════════════════════════════════════

def load_student_profile() -> dict:
    os.makedirs(MEMORY_DIR, exist_ok=True)

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "nivel":            "iniciante",
        "pontos":           0,
        "testes_realizados": 0,
        "acertos_totais":   0,
        "erros_totais":     0,
        "topicos_fracos":   [],
        "topicos_fortes":   [],
        "historico_testes": [],
        "criado_em":        datetime.now().isoformat(),
        "atualizado_em":    datetime.now().isoformat(),
    }


def save_student_profile(profile: dict):
    profile["atualizado_em"] = datetime.now().isoformat()
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def update_level(profile: dict) -> str:
    if profile["testes_realizados"] < 2:
        return profile["nivel"]

    total = profile["acertos_totais"] + profile["erros_totais"]
    if total == 0:
        return profile["nivel"]

    taxa = profile["acertos_totais"] / total

    if taxa >= 0.80:
        profile["nivel"] = "avançado"
    elif taxa >= 0.55:
        profile["nivel"] = "intermediário"
    else:
        profile["nivel"] = "iniciante"

    return profile["nivel"]


def perfil_resumido(profile: dict) -> str:
    fracos  = ", ".join(profile["topicos_fracos"][-3:])  or "nenhum identificado ainda"
    fortes  = ", ".join(profile["topicos_fortes"][-3:])  or "nenhum identificado ainda"
    total   = profile["acertos_totais"] + profile["erros_totais"]
    taxa    = f"{profile['acertos_totais']/total*100:.0f}%" if total else "sem dados"

    return (
        f"Nível: {profile['nivel']}. "
        f"Taxa de acerto: {taxa}. "
        f"Dificuldades: {fracos}. "
        f"Pontos fortes: {fortes}."
    )


# ══════════════════════════════════════════════════════════
#  RAG RETRIEVER
# ══════════════════════════════════════════════════════════

class RAGRetriever:

    def __init__(self, store_dir: str):
        print("→ Carregando índice FAISS...")

        with open(os.path.join(store_dir, "config.pkl"), "rb") as f:
            config = pickle.load(f)

        with open(os.path.join(store_dir, "chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)

        self.model = SentenceTransformer(config["embed_model"])
        self.index = faiss.read_index(os.path.join(store_dir, "index.faiss"))
        print(f"✓ {self.index.ntotal} vetores carregados.")

    def retrieve(self, query: str, top_k: int = TOP_K_CHUNKS) -> list[dict]:
        """Busca PT + EN fundidas e re-rankeadas."""
        resultados = {}

        for chunk in self._search_raw(query, top_k):
            resultados[chunk["chunk_id"]] = chunk

        query_en = self._traduzir_query(query)
        if query_en and query_en.lower() != query.lower():
            for chunk in self._search_raw(query_en, top_k):
                cid = chunk["chunk_id"]
                if cid not in resultados:
                    resultados[cid] = chunk
                else:
                    resultados[cid]["score"] = max(
                        resultados[cid]["score"], chunk["score"]
                    )

        ordenados = sorted(resultados.values(), key=lambda x: x["score"], reverse=True)
        return ordenados[:top_k]

    def _search_raw(self, query: str, top_k: int) -> list[dict]:
        vec = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(vec)
        scores, indices = self.index.search(vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score > 0.2:
                results.append({**self.chunks[idx], "score": float(score)})
        return results

    def _traduzir_query(self, query_pt: str) -> str:
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            resp   = client.chat.completions.create(
                model=GROQ_MODEL,
                max_tokens=60,
                messages=[{
                    "role": "user",
                    "content": (
                        "Translate this search query to English. "
                        "Reply with ONLY the translated query, no explanation.\n"
                        f"Query: {query_pt}"
                    )
                }]
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return ""

    def format_context(self, chunks: list[dict]) -> str:
        if not chunks:
            return "Nenhum trecho relevante encontrado no livro."
        parts = [f"[Trecho {i} — Página {c['page']}]\n{c['text']}"
                 for i, c in enumerate(chunks, 1)]
        return "\n\n---\n\n".join(parts)


# ══════════════════════════════════════════════════════════
#  AGENTE
# ══════════════════════════════════════════════════════════

class TutorAgent:

    def __init__(self, store_dir: str):
        self.client          = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.retriever       = RAGRetriever(store_dir)
        self.profile         = load_student_profile()
        self._teste_pendente = None

    # ── LLM ───────────────────────────────────────────────

    def _chat(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return response.choices[0].message.content.strip()

    # ── Roteamento ────────────────────────────────────────

    def detectar_intencao(self, mensagem: str) -> str:
        if self._teste_pendente:
            return "resposta_teste"

        msg = mensagem.lower()

        if any(k in msg for k in ["resuma", "resumo", "resume", "síntese", "sintetize"]):
            return "resumo"
        if any(k in msg for k in ["teste", "quiz", "questão", "questões", "me avalie", "me teste"]):
            return "teste"
        return "qa"

    # ── Q&A ───────────────────────────────────────────────

    def responder_pergunta(self, pergunta: str) -> str:
        chunks   = self.retriever.retrieve(pergunta)
        contexto = self.retriever.format_context(chunks)
        perfil   = perfil_resumido(self.profile)

        system = f"""Você é um tutor especializado no conteúdo de um livro acadêmico escrito em inglês.
Os trechos fornecidos estão em inglês — use-os como fonte de conhecimento.
SEMPRE responda em português brasileiro, independentemente do idioma dos trechos.
Responda SOMENTE com base nos trechos fornecidos. Se a informação não estiver lá, diga claramente.
Adapte a linguagem ao perfil do aluno: {perfil}
Seja claro, didático e objetivo."""

        user = f"""Trechos do livro (em inglês):
{contexto}

Pergunta do aluno: {pergunta}

Responda em português brasileiro."""

        return self._chat(system, user)

    # ── Resumo ────────────────────────────────────────────

    def gerar_resumo(self, topico: str) -> str:
        chunks   = self.retriever.retrieve(topico, top_k=7)
        contexto = self.retriever.format_context(chunks)
        perfil   = perfil_resumido(self.profile)

        system = f"""Você é um tutor especializado em criar resumos didáticos.
O livro está em inglês — os trechos fornecidos estarão em inglês.
SEMPRE escreva o resumo em português brasileiro.
Use APENAS as informações dos trechos fornecidos.
Estruture com: introdução, pontos principais e conclusão.
Adapte ao perfil do aluno: {perfil}"""

        user = f"""Trechos do livro (em inglês) sobre "{topico}":
{contexto}

Gere um resumo didático em português brasileiro sobre: {topico}"""

        return self._chat(system, user)

    # ── Teste ─────────────────────────────────────────────

    def gerar_teste(self, topico: str) -> str:
        chunks   = self.retriever.retrieve(topico, top_k=6)
        contexto = self.retriever.format_context(chunks)
        nivel    = self.profile["nivel"]

        instrucao_nivel = {
            "iniciante":     "Crie questões simples (4 alternativas). Foque em definições e conceitos básicos.",
            "intermediário": "Crie questões (4 alternativas) que exijam compreensão e aplicação dos conceitos.",
            "avançado":      "Crie questões desafiadoras (4 alternativas) com análise crítica e síntese de conceitos.",
        }.get(nivel, "Crie questões de múltipla escolha (4 alternativas).")

        system = f"""Você é um professor criando um teste baseado em livro acadêmico em inglês.
Os trechos fornecidos estão em inglês — use-os como fonte de conteúdo.
TODAS as questões, alternativas e explicações devem ser em português brasileiro.
{instrucao_nivel}

FORMATO OBRIGATÓRIO:
QUESTÃO 1: [enunciado em português]
A) [alternativa]
B) [alternativa]
C) [alternativa]
D) [alternativa]
RESPOSTA_1: [letra]
EXPLICAÇÃO_1: [explicação em português]

QUESTÃO 2: [enunciado em português]
A) [alternativa]
B) [alternativa]
C) [alternativa]
D) [alternativa]
RESPOSTA_2: [letra]
EXPLICAÇÃO_2: [explicação em português]

QUESTÃO 3: [enunciado em português]
A) [alternativa]
B) [alternativa]
C) [alternativa]
D) [alternativa]
RESPOSTA_3: [letra]
EXPLICAÇÃO_3: [explicação em português]"""

        user = f"""Trechos do livro (em inglês) sobre "{topico}":
{contexto}

Crie um teste de 3 questões em português brasileiro sobre: {topico}"""

        resposta_llm         = self._chat(system, user)
        self._teste_pendente = self._parsear_gabarito(resposta_llm, topico)
        return self._formatar_questoes_para_aluno(resposta_llm)

    def _parsear_gabarito(self, raw: str, topico: str) -> dict:
        gabarito = {"topico": topico, "questoes": []}
        for i in range(1, 4):
            resp = re.search(rf"RESPOSTA_{i}:\s*([A-D])", raw, re.IGNORECASE)
            expl = re.search(rf"EXPLICAÇÃO_{i}:\s*(.+?)(?=QUESTÃO|\Z)", raw, re.IGNORECASE | re.DOTALL)
            gabarito["questoes"].append({
                "numero":           i,
                "resposta_correta": resp.group(1).upper() if resp else "?",
                "explicacao":       expl.group(1).strip() if expl else "",
            })
        return gabarito

    def _formatar_questoes_para_aluno(self, raw: str) -> str:
        """Remove apenas as linhas de gabarito, preservando todas as questões."""
        linhas_limpas = []

        for linha in raw.splitlines():
            # remove somente linhas que começam com RESPOSTA_ ou EXPLICAÇÃO_
            if re.match(r"^\s*(RESPOSTA_\d+|EXPLICAÇÃO_\d+)\s*:", linha, re.IGNORECASE):
                continue
            linhas_limpas.append(linha)

        # remove linhas em branco consecutivas no final
        resultado = "\n".join(linhas_limpas)
        resultado = re.sub(r"\n{3,}", "\n\n", resultado).strip()

        return resultado + "\n\n📝 Responda no formato: 1-A 2-B 3-C"

    # ── Avaliação ─────────────────────────────────────────

    def avaliar_respostas(self, resposta_aluno: str) -> str:
        if not self._teste_pendente:
            return "Nenhum teste ativo. Peça um novo teste primeiro."

        respostas_aluno = self._parsear_respostas_aluno(resposta_aluno)
        gabarito        = self._teste_pendente
        topico          = gabarito["topico"]
        acertos         = 0
        feedback        = [f"📊 Resultado — '{topico}':\n"]

        for q in gabarito["questoes"]:
            num     = q["numero"]
            correta = q["resposta_correta"]
            dada    = respostas_aluno.get(num, "?").upper()
            acertou = dada == correta

            if acertou:
                acertos += 1
                self.profile["acertos_totais"] += 1
                if topico not in self.profile["topicos_fortes"]:
                    self.profile["topicos_fortes"].append(topico)
                feedback.append(f"✅ Questão {num}: correto!")
            else:
                self.profile["erros_totais"] += 1
                if topico not in self.profile["topicos_fracos"]:
                    self.profile["topicos_fracos"].append(topico)
                feedback.append(
                    f"❌ Questão {num}: você respondeu {dada}, correto era {correta}.\n"
                    f"   💡 {q['explicacao']}"
                )

        self.profile["testes_realizados"] += 1
        self.profile["pontos"]            += acertos * 10
        self.profile["historico_testes"].append({
            "topico":  topico,
            "acertos": acertos,
            "total":   3,
            "data":    datetime.now().isoformat(),
        })

        nivel_anterior = self.profile["nivel"]
        novo_nivel     = update_level(self.profile)
        save_student_profile(self.profile)
        self._teste_pendente = None

        feedback.append(f"\n🏆 Acertos: {acertos}/3 | +{acertos * 10} pontos")
        feedback.append(f"📈 Nível: {novo_nivel}")
        if novo_nivel != nivel_anterior:
            feedback.append(f"🎉 Você passou de '{nivel_anterior}' para '{novo_nivel}'!")

        return "\n".join(feedback)

    def _parsear_respostas_aluno(self, texto: str) -> dict:
        respostas = {}
        pares = re.findall(r"(\d)\s*[-:)]\s*([A-Da-d])", texto)
        if pares:
            for num, letra in pares:
                respostas[int(num)] = letra.upper()
            return respostas

        letras = re.findall(r"\b([A-Da-d])\b", texto)
        for i, letra in enumerate(letras[:3], 1):
            respostas[i] = letra.upper()
        return respostas

    # ── Ponto de entrada ──────────────────────────────────

    def processar(self, mensagem: str) -> str:
        intencao = self.detectar_intencao(mensagem)

        if intencao == "resposta_teste":
            return self.avaliar_respostas(mensagem)
        elif intencao == "resumo":
            topico = self._extrair_topico(mensagem, "resumo")
            return self.gerar_resumo(topico)
        elif intencao == "teste":
            topico = self._extrair_topico(mensagem, "teste")
            return self.gerar_teste(topico)
        else:
            return self.responder_pergunta(mensagem)

    def _extrair_topico(self, mensagem: str, tipo: str) -> str:
        padroes = {
            "resumo": r"\b(resuma|resumo|resume|síntese|sintetize|sobre|o|a|do|da)\b",
            "teste":  r"\b(teste|quiz|questão|questões|me avalie|me teste|sobre|o|a|do|da)\b",
        }
        topico = re.sub(padroes.get(tipo, ""), "", mensagem, flags=re.IGNORECASE).strip()
        return topico if topico else mensagem