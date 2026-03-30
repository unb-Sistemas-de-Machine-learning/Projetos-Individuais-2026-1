from typing import Optional
from rag import buscar_rag
from elegibilidade import chamar_llm, motor_elegibilidade


# classifica intencao

PALAVRAS_TRIAGEM = [
    "beneficio", "benefício", "direito", "direitos", "renda", "família",
    "cadastro", "bolsa", "bpc", "cras", "auxilio", "auxílio", "programa",
    "vulnerabilidade", "pobreza", "ajuda", "amparo", "elegivel", "elegível"
]

PALAVRAS_ENCERRAMENTO = ["sair", "exit", "tchau", "encerrar", "finalizar", "fim"]


def classificar_intencao(mensagem: str) -> str:
    msg = mensagem.lower().strip()
    if msg in PALAVRAS_ENCERRAMENTO:
        return "encerramento"
    for palavra in PALAVRAS_TRIAGEM:
        if palavra in msg:
            return "triagem"
    return "pergunta"

def entrada_numerica(prompt_texto: str, tipo: type = float, minimo: float = 0) -> Optional[float]:
    while True:
        valor_str = input(prompt_texto).strip()
        if valor_str.lower() in ["sair", "cancelar"]:
            return None
        try:
            valor = tipo(valor_str.replace(",", "."))
            if valor < minimo:
                print(f"  ⚠️  Insira um valor igual ou maior que {minimo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠️  Valor inválido. Digite um número (ex: 1200 ou 1200,50).")


def coletar_dados() -> Optional[dict]:
    print("\n🔎 Vamos verificar seu direito a benefícios.\n")
    print("   (Digite 'cancelar' a qualquer momento para voltar ao menu)\n")

    renda = entrada_numerica("  Renda familiar total mensal (R$): ", float, 0)
    if renda is None:
        return None

    pessoas = entrada_numerica("  Número de pessoas na família: ", int, 1)
    if pessoas is None:
        return None

    idade = entrada_numerica("  Sua idade: ", int, 0)
    if idade is None:
        return None

    print("\n  A família possui algum membro com deficiência de longo prazo (2+ anos)?")
    deficiencia_str = input("  (sim/não): ").strip().lower()
    tem_deficiencia = deficiencia_str in ["sim", "s", "yes"]

    renda_per_capita = renda / int(pessoas)

    return {
        "renda": renda,
        "pessoas": int(pessoas),
        "idade": int(idade),
        "renda_per_capita": round(renda_per_capita, 2),
        "tem_deficiencia": tem_deficiencia
    }

# modulo de perguntas
def responder_pergunta(pergunta: str, sessao: dict) -> str:
    docs_relevantes = buscar_rag(pergunta)
    fontes = []
    contexto_rag = ""

    if docs_relevantes:
        partes = []
        for doc in docs_relevantes:
            partes.append(f"[{doc['titulo']}]\n{doc['conteudo']}")
            fontes.append(f"{doc['titulo']} — {doc['fonte']}")
        contexto_rag = "\n\n".join(partes)

    dados_usuario = sessao.get("dados_usuario", {})
    dados_str = ""
    if dados_usuario:
        dados_str = (
            f"\nDados do usuário nesta sessão:\n"
            f"- Renda per capita: R$ {dados_usuario.get('renda_per_capita', 'N/A')}\n"
            f"- Idade: {dados_usuario.get('idade', 'N/A')} anos\n"
            f"- Deficiência: {'Sim' if dados_usuario.get('tem_deficiencia') else 'Não'}\n"
        )

    prompt = f"""Você é um assistente de assistência social brasileiro.
Responda a pergunta abaixo com base nas informações fornecidas.

{f'CONTEXTO DO ATENDIMENTO ATUAL:{dados_str}' if dados_str else ''}
{f'DOCUMENTOS DA BASE DE CONHECIMENTO:{chr(10)}{contexto_rag}' if contexto_rag else ''}

PERGUNTA DO USUÁRIO:
{pergunta}

INSTRUÇÕES:
- Responda de forma clara, objetiva e em português simples
- Cite a fonte legal quando possível
- Se não souber, oriente o usuário a buscar o CRAS
- NÃO invente informações
- NÃO saia do tema de assistência social
"""

    resposta = chamar_llm(prompt)

    if fontes:
        resposta += "\n\n📚 Fontes consultadas:\n" + "\n".join(f"  - {f}" for f in fontes)

    return resposta

def agente():
    sessao: dict = {
        "dados_usuario": {},
        "ultima_resposta": "",
        "elegibilidade": {},
        "historico": []
    }

    print("\n" + "═" * 55)
    print("  🤖 Agente de Assistência Social — Governo Digital")
    print("═" * 55)
    print("  Posso ajudar você a:")
    print("  • Verificar benefícios disponíveis (Bolsa Família, BPC)")
    print("  • Responder dúvidas sobre programas sociais")
    print("  • Orientar sobre documentos e onde se cadastrar")
    print("\n  ⚠️  Esta sessão não armazena dados após encerramento.")
    print("  Digite 'sair' para encerrar.\n")
    print("─" * 55)

    while True:
        try:
            msg = input("\nVocê: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSessão encerrada.")
            break

        if not msg:
            continue

        sessao["historico"].append({"papel": "usuario", "mensagem": msg})
        intencao = classificar_intencao(msg)

        if intencao == "encerramento":
            print("\n🤖 Atendimento encerrado. Até logo! 👋\n")
            break

        elif intencao == "triagem":
            dados = coletar_dados()
            if dados is None:
                print("\n🤖 Coleta cancelada. Posso ajudar com outra coisa?")
                continue
            sessao["dados_usuario"] = dados
            print("\n⏳ Analisando elegibilidade...\n")
            resposta = motor_elegibilidade(dados, sessao)
            print("📋 Resultado da análise:\n")
            print(resposta)
            sessao["historico"].append({"papel": "agente", "mensagem": resposta})

        elif intencao == "pergunta":
            print("\n⏳ Buscando informação...\n")
            resposta = responder_pergunta(msg, sessao)
            print("💬", resposta)
            sessao["historico"].append({"papel": "agente", "mensagem": resposta})

        else:
            print("\n🤖 Posso verificar seu direito a benefícios ou responder dúvidas.")
            print("   Tente: 'quero verificar meus benefícios' ou faça uma pergunta.")


if __name__ == "__main__":
    agente()