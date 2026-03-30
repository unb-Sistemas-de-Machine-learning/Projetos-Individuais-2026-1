import json
import requests

def chamar_llm(prompt: str, modelo: str = "llama3") -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": modelo, "prompt": prompt, "stream": False},
            timeout=60
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

# Regras baseadas em lei + LLM para explicação
SALARIO_MINIMO = 1412

REFERENCIAS_LEGAIS = {
    "Bolsa Família": "Lei nº 14.284/2021 — renda per capita ≤ R$ 218,00",
    "BPC (Idoso)": "LOAS Art. 20 — idade ≥ 65 e renda ≤ 1/4 salário mínimo",
    "BPC (Deficiência)": "LOAS Art. 20 §2º — deficiência + renda ≤ 1/4 salário mínimo",
    "Auxílio Gás": "Lei nº 14.237/2021 — famílias do CadÚnico com baixa renda",
    "Tarifa Social de Energia": "Lei nº 12.212/2010 — renda ≤ 1/2 salário mínimo",
    "ID Jovem": "Decreto nº 8.537/2015 — idade 15 a 29 e renda ≤ 2 salários mínimos",
}


def verificar_elegibilidade(dados: dict) -> dict:
    aprovados = []
    motivos = {}
    nao_aprovados = []

    renda_pc = dados["renda_per_capita"]

    # Bolsa Família
    if renda_pc <= 218:
        aprovados.append("Bolsa Família")
        motivos["Bolsa Família"] = f"Renda per capita R$ {renda_pc:.2f} ≤ R$ 218"
    else:
        nao_aprovados.append({"nome": "Bolsa Família", "motivo": f"Renda per capita R$ {renda_pc:.2f} > R$ 218"})

    # BPC Idoso
    if renda_pc <= SALARIO_MINIMO / 4 and dados["idade"] >= 65:
        aprovados.append("BPC (Idoso)")
        motivos["BPC (Idoso)"] = "Idade ≥ 65 e baixa renda"
    else:
        nao_aprovados.append({"nome": "BPC (Idoso)", "motivo": "Não atende idade ou renda"})

    # BPC Deficiência
    if dados["tem_deficiencia"] and renda_pc <= SALARIO_MINIMO / 4:
        aprovados.append("BPC (Deficiência)")
        motivos["BPC (Deficiência)"] = "Deficiência de longo prazo + baixa renda"
    elif dados["tem_deficiencia"] and renda_pc > SALARIO_MINIMO / 4:
        nao_aprovados.append({"nome": "BPC (Deficiência)", "motivo": f"Renda per capita R$ {renda_pc:.2f} > R$ {SALARIO_MINIMO/4:.2f}"})

    # Auxílio Gás
    if renda_pc <= SALARIO_MINIMO / 2:
        aprovados.append("Auxílio Gás")
        motivos["Auxílio Gás"] = "Renda baixa — inscrição no CadÚnico necessária"
    else:
        nao_aprovados.append({"nome": "Auxílio Gás", "motivo": "Renda acima do limite"})

    # Tarifa Social de Energia
    if renda_pc <= SALARIO_MINIMO / 2:
        aprovados.append("Tarifa Social de Energia")
        motivos["Tarifa Social de Energia"] = "Desconto na conta de luz por baixa renda"
    else:
        nao_aprovados.append({"nome": "Tarifa Social", "motivo": "Renda acima do limite"})

    # ID Jovem
    if 15 <= dados["idade"] <= 29 and renda_pc <= SALARIO_MINIMO * 2:
        aprovados.append("ID Jovem")
        motivos["ID Jovem"] = "Jovem de baixa renda com acesso a benefícios culturais"

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
            f"📋 Motivos (baseados em lei):\n{motivos_str}\n\n"
            f"📍 Próximo passo:\n"
            f"  Procure o CRAS da sua cidade para uma avaliação completa e personalizada.\n"
            f"  Outros benefícios municipais ou estaduais podem estar disponíveis."
        )
        sessao["ultima_resposta"] = resposta
        return resposta

    beneficios_str = "\n".join(f"- {b}: {resultado['motivos'][b]}" for b in resultado["aprovados"])

    prompt = f"""Você é um assistente de assistência social brasileiro.
Com base nos dados abaixo, explique de forma clara e acessível quais benefícios a pessoa tem direito.

DADOS DA PESSOA:
- Renda familiar: R$ {dados['renda']:.2f}
- Pessoas na família: {dados['pessoas']}
- Renda per capita: R$ {dados['renda_per_capita']:.2f}
- Idade: {dados['idade']} anos
- Membro com deficiência: {'Sim' if dados['tem_deficiencia'] else 'Não'}

BENEFÍCIOS APROVADOS (com base em regras legais):
{beneficios_str}

INSTRUÇÕES:
- Use linguagem simples, direta e respeitosa
- Explique o motivo legal de cada benefício aprovado
- Liste os documentos necessários para cada um
- Indique onde fazer o cadastro ou requerimento
- NÃO invente benefícios além dos listados acima
- NÃO faça perguntas
- Formato: Benefícios ✓ | Por que você tem direito | Documentos | Onde ir
"""

    resposta = chamar_llm(prompt)
    sessao["ultima_resposta"] = resposta
    return resposta