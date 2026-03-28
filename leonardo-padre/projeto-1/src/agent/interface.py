import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.agent.agent import TutorAgent, perfil_resumido

BANNER = """
╔══════════════════════════════════════════════╗
║          📚 TUTOR AGENT — CLI                ║
║  Livro: Modern Operating Systems (Tanenbaum) ║
║  Comandos: /perfil  /ajuda  /sair            ║
╚══════════════════════════════════════════════╝
"""

AJUDA = """
Exemplos de uso:
  → Pergunta : "O que é um deadlock?"
  → Resumo   : "Resuma escalonamento de processos"
  → Teste    : "Me teste sobre memória virtual"
  → Resposta : "1-A 2-C 3-B"  (após receber um teste)

Comandos:
  /perfil  — exibe seu progresso
  /ajuda   — exibe esta mensagem
  /sair    — encerra o tutor
"""


def run_cli(store_dir: str):
    print(BANNER)

    try:
        agente = TutorAgent(store_dir=store_dir)
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
        sys.exit(1)

    print(f"Bem-vindo! Seu nível atual: {agente.profile['nivel'].upper()}\n")

    while True:
        try:
            entrada = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Até logo!")
            break

        if not entrada:
            continue

        if entrada.lower() == "/sair":
            print("👋 Até logo! Bons estudos!")
            break

        elif entrada.lower() == "/perfil":
            p = agente.profile
            total = p["acertos_totais"] + p["erros_totais"]
            taxa  = f"{p['acertos_totais']/total*100:.0f}%" if total else "sem dados"
            print(f"""
── Seu Perfil ──────────────────────
  Nível          : {p['nivel']}
  Pontos         : {p['pontos']}
  Testes feitos  : {p['testes_realizados']}
  Taxa de acerto : {taxa}
  Tópicos fracos : {', '.join(p['topicos_fracos'][-3:]) or '—'}
  Tópicos fortes : {', '.join(p['topicos_fortes'][-3:]) or '—'}
────────────────────────────────────
""")

        elif entrada.lower() == "/ajuda":
            print(AJUDA)

        else:
            print("\n🤔 Pensando...\n")
            try:
                resposta = agente.processar(entrada)
                print(f"Tutor: {resposta}\n")
            except Exception as e:
                print(f"❌ Erro: {e}\n")