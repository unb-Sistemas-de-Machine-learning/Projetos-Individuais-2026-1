import json
import logging
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agents import DiagnosticoAgent, RecomendadorAgent, GeradorAgent, AvaliadorAgent, SessionContext
from rag import seed_sample_data, BANCAS, MATERIAS

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("Variável GOOGLE_API_KEY não encontrada. Configure o arquivo .env")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

seed_sample_data()

diagnostico_agent = DiagnosticoAgent()
recomendador_agent = RecomendadorAgent()
gerador_agent = GeradorAgent()
avaliador_agent = AvaliadorAgent()

def salvar_log_sessao(ctx: SessionContext) -> None:
    log_path = LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = {
        "timestamp": datetime.now().isoformat(),
        "concurso": ctx.concurso,
        "materia": ctx.materia,
        "banca": ctx.banca,
        "nivel": ctx.nivel,
        "trilha": ctx.trilha,
        "historico_respostas": ctx.historico_respostas,
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Sessão salva em %s", log_path)

def init_session_state() -> None:
    defaults = {
        "etapa": "configuracao",
        "ctx": None,
        "questoes_diagnostico": [],
        "questao_atual": None,
        "gabarito_atual": None,
        "topico_atual": None,
        "messages": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def main() -> None:
    st.set_page_config(
        page_title="Tutor de Concursos de TI",
        page_icon="🎓",
        layout="centered",
    )

    st.title("🎓 Tutor de Concursos de TI")
    st.caption("Agente de recomendação com explicabilidade obrigatória")

    init_session_state()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.etapa == "configuracao":
        with st.form("config_form"):
            st.subheader("Configure sua sessão de estudos")
            concurso = st.text_input("Concurso alvo", placeholder="Ex: SEFAZ-SP 2025, TRF 5ª Região")
            materia = st.selectbox("Matéria", MATERIAS)
            banca = st.selectbox("Banca examinadora", BANCAS)
            submitted = st.form_submit_button("Iniciar diagnóstico 🚀")

        if submitted and concurso:
            ctx = SessionContext(concurso=concurso, materia=materia, banca=banca)
            st.session_state.ctx = ctx

            questoes, instrucao = diagnostico_agent.run(ctx)
            st.session_state.questoes_diagnostico = questoes
            st.session_state.etapa = "diagnostico"

            add_message("assistant", instrucao)
            logger.info("Sessão iniciada: %s | %s | %s", concurso, materia, banca)
            st.rerun()

    elif st.session_state.etapa == "diagnostico":
        n = len(st.session_state.questoes_diagnostico)
        hint = f"Responda as {n} questões separadas por vírgula (ex: Certo, B, Errado)"

        if resposta_raw := st.chat_input(hint):
            respostas = [r.strip() for r in resposta_raw.split(",")]
            add_message("user", resposta_raw)

            ctx = st.session_state.ctx
            resultado = diagnostico_agent.classificar(
                ctx, respostas, st.session_state.questoes_diagnostico
            )
            add_message("assistant", resultado)

            trilha_msg = recomendador_agent.run(ctx)
            add_message("assistant", trilha_msg)

            st.session_state.etapa = "recomendacao"
            logger.info("Diagnóstico concluído. Nível: %s", ctx.nivel)
            st.rerun()

    elif st.session_state.etapa in ("recomendacao", "pratica"):
        ctx = st.session_state.ctx

        with st.sidebar:
            st.subheader("📚 Sua trilha de estudos")
            for i, item in enumerate(ctx.trilha, 1):
                status = "✅" if item.get("concluido") else "📌"
                st.markdown(f"{status} **{i}.** {item['topico']}")

            st.divider()
            if st.button("📊 Encerrar sessão"):
                resumo = avaliador_agent.resumo_sessao(ctx)
                add_message("assistant", resumo)
                salvar_log_sessao(ctx)
                st.session_state.etapa = "encerrado"
                st.rerun()

        placeholder = (
            "Digite 'praticar' para uma questão, 'trilha' para ver seus estudos, "
            "ou pergunte 'por que [tópico]?' para ver a justificativa"
        )
        if user_input := st.chat_input(placeholder):
            add_message("user", user_input)
            cmd = user_input.lower().strip()

            if "praticar" in cmd or "questão" in cmd or "questao" in cmd:
                resposta = gerador_agent.run(ctx)
                st.session_state.questao_atual = resposta
                st.session_state.etapa = "pratica"
                add_message("assistant", resposta)
                add_message("assistant", "✍️ Digite sua resposta abaixo:")

            elif "trilha" in cmd:
                trilha_msg = recomendador_agent._formatar_trilha(ctx)
                add_message("assistant", trilha_msg)

            elif "por que" in cmd or "porque" in cmd:
                topico_query = cmd.replace("por que", "").replace("porque", "").strip()
                topico_encontrado = next(
                    (t for t in ctx.trilha if topico_query.lower() in t["topico"].lower()),
                    None,
                )
                if topico_encontrado:
                    msg = (
                        f"💡 **Por que estudar {topico_encontrado['topico']}?**\n\n"
                        f"{topico_encontrado['justificativa']}"
                    )
                else:
                    msg = f"Tópico '{topico_query}' não encontrado na trilha. Tente o nome exato."
                add_message("assistant", msg)

            elif st.session_state.questao_atual:
                proximos = [t for t in ctx.trilha if not t.get("concluido")]
                topico = proximos[0]["topico"] if proximos else ctx.materia

                feedback = avaliador_agent.run(
                    ctx=ctx,
                    questao=st.session_state.questao_atual,
                    resposta_candidato=user_input,
                    gabarito="[verificado pelo LLM]",
                    topico=topico,
                )
                st.session_state.questao_atual = None
                add_message("assistant", feedback)

            else:
                add_message("assistant", "💬 Digite **'praticar'** para uma questão ou **'trilha'** para ver seus estudos.")

            logger.info("Interação registrada: '%s'", user_input[:80])
            st.rerun()

    elif st.session_state.etapa == "encerrado":
        st.success("Sessão encerrada! Seus dados foram salvos em `logs/`.")
        if st.button("🔄 Nova sessão"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
