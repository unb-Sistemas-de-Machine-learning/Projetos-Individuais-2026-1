"""CLI do agente educacional (recomendação com explicabilidade obrigatória)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Permite executar: python src/main.py a partir de projeto-1/
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import KB_DIR, llm_backend
from src.pipeline import EntradaUsuario, executar


def main() -> None:
    p = argparse.ArgumentParser(
        description="Agente de recomendação de estudo com justificativas explícitas (RAG + LLM).",
    )
    p.add_argument("--objetivo", required=True, help="O que o aluno quer aprender")
    p.add_argument("--nivel", default="intermediário", help="iniciante | intermediário | avançado")
    p.add_argument("--horas", default="6h", help="Tempo semanal disponível (ex: 6h, 10h)")
    p.add_argument("--restricoes", default="", help="Preferências ou limitações")
    p.add_argument("--json", action="store_true", help="Imprime só JSON na saída")
    args = p.parse_args()

    if not args.json:
        print(f"Backend LLM: {llm_backend()} | KB: {KB_DIR}", file=sys.stderr)

    entrada = EntradaUsuario(
        objetivo=args.objetivo,
        nivel=args.nivel,
        horas_semana=args.horas,
        restricoes=args.restricoes,
    )
    saida = executar(entrada)
    payload = saida.model_dump()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(saida.resumo_perfil)
        print()
        for i, rec in enumerate(saida.recomendacoes, 1):
            print(f"{i}. [{rec.tipo}] {rec.titulo}")
            print(f"   {rec.descricao}")
            print(f"   Por quê: {rec.justificativa}")
            if rec.passos:
                for j, passo in enumerate(rec.passos, 1):
                    print(f"   {j}) {passo}")
            print()
        if saida.avisos_ou_limitacoes:
            print("Avisos:")
            for av in saida.avisos_ou_limitacoes:
                print(f"  - {av}")


if __name__ == "__main__":
    main()
