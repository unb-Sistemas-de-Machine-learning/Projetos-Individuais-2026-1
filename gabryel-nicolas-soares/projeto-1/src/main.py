import requests
import json
from typing import Optional

# BASE DE CONHECIMENTO (RAG SIMPLES)
BASE_CONHECIMENTO = [
    {
        "id": "bolsa_familia_criterio",
        "titulo": "Bolsa Família — Critério de renda",
        "conteudo": (
            "O Bolsa Família é destinado a famílias com renda per capita mensal de até R$ 218,00. "
            "A inscrição é feita pelo CadÚnico. Documentos necessários: CPF, RG, comprovante de renda "
            "e comprovante de residência. O cadastro deve ser atualizado a cada 2 anos."
        ),
        "fonte": "Decreto nº 11.150/2022 e Lei nº 14.284/2021"
    },
    {
        "id": "bpc_criterio",
        "titulo": "BPC — Critérios de elegibilidade",
        "conteudo": (
            "O Benefício de Prestação Continuada (BPC) garante 1 salário mínimo mensal a idosos com "
            "65 anos ou mais e a pessoas com deficiência de qualquer idade, desde que a renda familiar "
            "per capita seja de até 1/4 do salário mínimo (R$ 353,00 em 2024). "
            "Não é necessário ter contribuído para o INSS. O requerimento é feito no INSS ou CRAS."
        ),
        "fonte": "LOAS — Lei nº 8.742/1993, Art. 20"
    },
    {
        "id": "cadúnico_info",
        "titulo": "CadÚnico — O que é e como funciona",
        "conteudo": (
            "O Cadastro Único (CadÚnico) é o registro do governo federal que identifica famílias "
            "de baixa renda para acesso a programas sociais. Famílias com renda mensal de até meio "
            "salário mínimo por pessoa, ou renda total de até 3 salários mínimos, podem se cadastrar. "
            "O cadastro é feito no CRAS do município."
        ),
        "fonte": "Decreto nº 6.135/2007"
    },
    {
        "id": "cras_servicos",
        "titulo": "CRAS — Serviços disponíveis",
        "conteudo": (
            "O Centro de Referência de Assistência Social (CRAS) oferece: cadastramento no CadÚnico, "
            "orientação sobre benefícios, encaminhamentos para serviços especializados, "
            "Serviço de Proteção e Atendimento Integral à Família (PAIF) e grupos socioeducativos. "
            "O atendimento é gratuito e presencial."
        ),
        "fonte": "Política Nacional de Assistência Social (PNAS/2004)"
    },
    {
        "id": "bpc_deficiencia",
        "titulo": "BPC para Pessoa com Deficiência",
        "conteudo": (
            "Pessoa com deficiência tem direito ao BPC independente da idade, desde que a deficiência "
            "seja de longo prazo (mínimo 2 anos) e cause impedimento à participação plena na sociedade. "
            "A avaliação é feita pelo INSS com laudo médico e avaliação social. "
            "Renda per capita familiar deve ser de até 1/4 do salário mínimo."
        ),
        "fonte": "LOAS — Lei nº 8.742/1993, Art. 20, § 2º"
    }
]

# MÓDULO RAG
def buscar_rag(pergunta: str, top_k: int = 2) -> list[dict]:
    pergunta_lower = pergunta.lower()
    pontuacoes = []

    for doc in BASE_CONHECIMENTO:
        texto = (doc["titulo"] + " " + doc["conteudo"]).lower()
        palavras = set(pergunta_lower.split())
        score = sum(1 for p in palavras if p in texto and len(p) > 3)
        pontuacoes.append((score, doc))

    pontuacoes.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in pontuacoes[:top_k] if score > 0]

# CHAMADA LLM (OLLAMA LOCAL)
def chamar_llm(prompt: str, modelo: str = "llama3") -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": modelo, "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "Sem resposta do modelo.")
    except requests.exceptions.ConnectionError:
        return "[ERRO] Não foi possível conectar ao Ollama. Verifique se está rodando com: `ollama serve`"
    except requests.exceptions.Timeout:
        return "[ERRO] O modelo demorou demais para responder. Tente novamente."
    except requests.exceptions.HTTPError as e:
        return f"[ERRO HTTP] {e}"
    except (KeyError, json.JSONDecodeError) as e:
        return f"[ERRO] Resposta inesperada do modelo: {e}"
    except Exception as e:
        return f"[ERRO inesperado] {e}"

# CLASSIFICADOR DE INTENÇÃO
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

# COLETA DE DADOS (COM VALIDAÇÃO)
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

    renda_per_capita = renda / int(pessoas)

    return {
        "renda": renda,
        "pessoas": int(pessoas),
        "idade": int(idade),
        "renda_per_capita": round(renda_per_capita, 2)
    }

# MOTOR DE ELEGIBILIDADE
REFERENCIAS_LEGAIS = {
    "Bolsa Família": "Lei nº 14.284/2021 — renda per capita ≤ R$ 218,00",
    "BPC (Idoso)": "LOAS Art. 20 — idade ≥ 65 e renda ≤ 1/4 salário mínimo",
}


def verificar_elegibilidade(dados: dict) -> dict:
    aprovados = []
    motivos = {}
    nao_aprovados = []

    renda_pc = dados["renda_per_capita"]

    if renda_pc <= 218:
        aprovados.append("Bolsa Família")
        motivos["Bolsa Família"] = f"Renda per capita R$ {renda_pc:.2f} ≤ R$ 218"
    else:
        nao_aprovados.append({"nome": "Bolsa Família", "motivo": f"Renda per capita R$ {renda_pc:.2f} > R$ 218"})

    if renda_pc <= 353 and dados["idade"] >= 65:
        aprovados.append("BPC (Idoso)")
        motivos["BPC (Idoso)"] = "Idade ≥ 65 e baixa renda"
    else:
        nao_aprovados.append({"nome": "BPC (Idoso)", "motivo": "Não atende idade ou renda"})

    return {"aprovados": aprovados, "motivos": motivos, "nao_aprovados": nao_aprovados}


def motor_elegibilidade(dados: dict, sessao: dict) -> str:
    resultado = verificar_elegibilidade(dados)
    sessao["elegibilidade"] = resultado

    if not resultado["aprovados"]:
        motivos_str = "\n".join(
            f"  - {item['nome']}: {item['motivo']}" for item in resultado["nao_aprovados"]
        )
        resposta = (
            f"\n❌ Com base nos dados informados, você não se enquadra nos critérios analisados.\n\n"
            f"📋 Motivos:\n{motivos_str}\n\n"
            f"📍 Próximo passo:\n"
            f"  Procure o CRAS da sua cidade para uma avaliação completa."
        )
        sessao["ultima_resposta"] = resposta
        return resposta

    beneficios_str = "\n".join(f"- {b}: {resultado['motivos'][b]}" for b in resultado["aprovados"])

    prompt = f"""Você é um assistente de assistência social brasileiro.
Com base nos dados abaixo, explique quais benefícios a pessoa tem direito.

DADOS DA PESSOA:
- Renda familiar: R$ {dados['renda']:.2f}
- Pessoas na família: {dados['pessoas']}
- Renda per capita: R$ {dados['renda_per_capita']:.2f}
- Idade: {dados['idade']} anos

BENEFÍCIOS APROVADOS:
{beneficios_str}

INSTRUÇÕES:
- Use linguagem simples e respeitosa
- Explique o motivo legal de cada benefício
- Liste os documentos necessários
- Indique onde fazer o cadastro
- NÃO invente benefícios além dos listados
- NÃO faça perguntas
"""

    resposta = chamar_llm(prompt)
    sessao["ultima_resposta"] = resposta
    return resposta


# MÓDULO DE PERGUNTAS (RAG + LLM)
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
            f"\nDados do usuário:\n"
            f"- Renda per capita: R$ {dados_usuario.get('renda_per_capita', 'N/A')}\n"
            f"- Idade: {dados_usuario.get('idade', 'N/A')} anos\n"
        )

    prompt = f"""Você é um assistente de assistência social brasileiro.

{f'CONTEXTO:{dados_str}' if dados_str else ''}
{f'DOCUMENTOS:{chr(10)}{contexto_rag}' if contexto_rag else ''}

PERGUNTA: {pergunta}

INSTRUÇÕES:
- Responda em português simples
- Cite a fonte legal quando possível
- Se não souber, oriente buscar o CRAS
- NÃO invente informações
"""

    resposta = chamar_llm(prompt)

    if fontes:
        resposta += "\n\n📚 Fontes:\n" + "\n".join(f"  - {f}" for f in fontes)

    return resposta

# AGENTE PRINCIPAL
def agente():
    sessao: dict = {
        "dados_usuario": {},
        "ultima_resposta": "",
        "elegibilidade": {},
        "historico": []
    }

    print("\n" + "═" * 55)
    print("  🤖 Agente de Assistência Social")
    print("═" * 55)
    print("  • Verificar benefícios (Bolsa Família, BPC)")
    print("  • Responder dúvidas sobre programas sociais")
    print("  Digite 'sair' para encerrar.")
    print("═" * 55)

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
            print("📋 Resultado:\n")
            print(resposta)
            sessao["historico"].append({"papel": "agente", "mensagem": resposta})

        elif intencao == "pergunta":
            print("\n⏳ Buscando informação...\n")
            resposta = responder_pergunta(msg, sessao)
            print("💬", resposta)
            sessao["historico"].append({"papel": "agente", "mensagem": resposta})

        else:
            print("\n🤖 Posso verificar benefícios ou responder dúvidas.")

if __name__ == "__main__":
    agente()