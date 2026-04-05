import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Chave da API ausente.")

client = genai.Client(api_key=API_KEY)
MODELO = 'gemini-3-flash-preview'

def agente_analista_risco(texto_cidadao):
    """Agente 1: Focado apenas em descobrir riscos subjacentes."""
    instrucao_auditor = """
    Você é um auditor de riscos urbanos.
    Analise o relato e identifique se há algum risco oculto à saúde pública (ex: focos de doenças, contaminação) ou segurança física iminente.
    Seja breve. Responda apenas com o risco identificado ou 'Nenhum risco sistêmico detectado'.
    """
    
    response = client.models.generate_content(
        model=MODELO,
        contents=texto_cidadao,
        config=types.GenerateContentConfig(
            temperature=0.3,
            system_instruction=instrucao_auditor
        )
    )
    return response.text.strip()

def agente_despachante(texto_original, parecer_risco):
    """Agente 2: Consolida a informação e formata o JSON."""
    instrucao_despachante = """
    Você é um despachante de zeladoria urbana.
    Você receberá o relato original do cidadão e um parecer de risco elaborado por um auditor.
    Classifique a demanda ESTRITAMENTE em JSON:
    {
        "categoria": "[Infraestrutura, Iluminação, Saneamento, Trânsito, Saúde, Vigilância Epidemiológica, Outros]",
        "urgencia": "[Alta, Média, Baixa]",
        "resumo_problema": "máx 5 palavras",
        "explicacao": "justificativa baseada no parecer de risco"
    }
    Regras: Se o parecer de risco indicar perigo à saúde pública ou segurança, a urgência é obrigatoriamente ALTA, independentemente 
    de ser um problema estético como mato alto.
    """
    
    prompt_combinado = f"Relato do cidadão: '{texto_original}'\nParecer do Auditor: '{parecer_risco}'"
    
    response = client.models.generate_content(
        model=MODELO,
        contents=prompt_combinado,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            system_instruction=instrucao_despachante
        )
    )
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"erro": "Falha no parsing", "raw_output": response.text}

def executar_pipeline(texto):
    print(f"Processando: '{texto}'")
    parecer = agente_analista_risco(texto)
    print(f" -> Parecer do Agente 1: {parecer}")

    # pausa entre a chamada do agente 1 e agente 2 para evitar rate limit
    time.sleep(4)
    resultado_final = agente_despachante(texto, parecer)
    return resultado_final

if __name__ == "__main__":
    casos_de_teste = [
    "Poste de iluminação queimado há semanas na quadra 5, a rua fica completamente escura à noite.",
    "Bueiro aberto na calçada perto da escola, uma criança quase caiu hoje cedo.",
    "Muito lixo acumulado atrás do mercado, cheiro forte e aparecendo ratos.",
    "Semáforo da avenida central não está funcionando desde ontem, trânsito virou um caos.",
    "Árvore grande com galhos quebrados ameaçando cair sobre os carros estacionados.",
    "Fiação elétrica solta no poste depois da chuva, parece perigoso.",
    "Ponto de ônibus sem cobertura, idosos ficam expostos ao sol forte e chuva.",
    "Vazamento constante de água limpa na rua há dias, desperdiçando muita água.",
    "Motoqueiros passando em alta velocidade dentro da área residencial.",
    "Calçada totalmente destruída dificultando passagem de cadeirantes.",
    "Esgoto correndo a céu aberto próximo às casas, cheiro insuportável.",
    "Terreno abandonado virou ponto de descarte irregular de entulho.",
    "Barulho excessivo todas as madrugadas vindo de um bar irregular na esquina.",
    "Sinalização de faixa de pedestre apagada em frente à escola municipal.",
    "Cachorros agressivos soltos na rua atacando pedestres.",
    "Acúmulo de água parada em obra abandonada, possível foco de mosquito.",
    "Buraco enorme na ciclovia causando risco para quem passa de bicicleta.",
    "Iluminação pública piscando constantemente, causando sensação de insegurança.",
    "Carros estacionados em cima da calçada obrigando pessoas a andar na rua.",
    "Cheiro forte de gás vindo de uma residência, moradores preocupados.",
    "Parquinho infantil com brinquedos quebrados e ferrugem exposta.",
    "Queimada frequente em lote vazio causando muita fumaça.",
    "Fila enorme no posto de saúde por falta de médicos, atendimento muito lento.",
    "Escadaria pública sem corrimão, idosos têm dificuldade para subir.",
    "Enxurrada sempre alaga essa rua quando chove, moradores ficam ilhados."
    "acho q tem um fio caido ali perto da praça mas n tenho certeza, alguém devia olhar",
    "não sei se é perigoso mas aquele prédio abandonado tá estranho à noite",
    "a rua não tá ruim não, tá praticamente uma pista de rally de tanto buraco",
    "toda vez que chove vira um rio aqui, normal né prefeitura?",
    "tem gente usando o campinho pra soltar rojão de madrugada",
    "cheiro muito forte vindo do bueiro, parece coisa podre",
    "o poste funciona às vezes sim às vezes não, fica piscando igual filme de terror",
    "um carro ficou abandonado faz meses ocupando vaga e juntando sujeira",
    "crianças brincando perto da avenida porque não tem área segura",
    "escutei estalos no transformador antes de acabar a energia ontem",
    "o ônibus para no meio da rua porque não existe ponto sinalizado",
    "não é reclamação mas acho que aquele muro pode cair qualquer hora",
    "tem um vazamento pequeno mas já está formando lama na calçada",
    "pessoal atravessa correndo porque os carros nunca param ali",
    "a praça virou estacionamento improvisado durante a noite",
    "não vi acidente ainda mas alguém vai se machucar naquela curva sem placa",
    "a água da torneira está saindo com cor estranha hoje",
    "muita fumaça preta saindo de uma oficina durante o dia inteiro",
    "tem um buraco escondido pela água da chuva, impossível ver",
    "parece brincadeira mas a tampa do bueiro simplesmente sumiu",
    "um cachorro ficou preso dentro do canal e ninguém consegue tirar",
    "luzes da quadra pública apagadas e pessoas evitando passar por lá",
    "barreira de obra caiu e ficou espalhada na pista",
    "a sirene disparou várias vezes sem motivo aparente",
    "o chão da passarela treme quando passa muita gente"
]

    casos_de_teste_reduzidos = casos_de_teste[:3]

    for i, relato in enumerate(casos_de_teste_reduzidos, 1):
        resultado = executar_pipeline(relato)
        print(f"--- RESULTADO FINAL {i} ---")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        print("-" * 40 + "\n")

        print("Aguardando 4 seg para a proxima requisição... \n")
        time.sleep(4)