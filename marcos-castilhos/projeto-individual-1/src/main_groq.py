import os
import json
import time
import csv
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("Chave da API ausente.")

client = Groq(api_key=API_KEY)
model = 'llama-3.1-8b-instant'

def agente_analista_risco(texto_cidadao):
    """Agente 1: Focado apenas em descobrir riscos subjacentes graves."""
    
    instrucao_auditor = """
    Você é um auditor de riscos urbanos. Analise o relato.
    Sua única função é separar problemas de CONFORTO/ESTÉTICA de perigos de MORTE/DOENÇA.
    - Se houver risco IMINENTE de acidente grave, morte ou surto de doença: descreva o risco em 1 frase curta.
    - Se for apenas incômodo, falta de conforto, estética ou problema de longo prazo: responda EXATAMENTE e APENAS: 'Sem risco iminente'.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": instrucao_auditor},
                {"role": "user", "content": texto_cidadao}
            ],
            model=model,
            temperature=0.0
        )
        conteudo = chat_completion.choices[0].message.content
        
        # Validação rígida contra saídas fantasmas
        if not conteudo:
            return "ALERTA: API retornou sucesso (200 OK), mas o conteúdo da mensagem veio vazio."
            
        return conteudo.strip()
    except Exception as e:
        return f"Erro Crítico no Agente 1: {e}"

def agente_despachante(texto_original, parecer_risco):
    """Agente 2: Consolida a informação e formata o JSON aplicando as réguas de negócio."""
    
    instrucao_despachante = """
    Você é um despachante de zeladoria urbana. Classifique a demanda ESTRITAMENTE em formato JSON e ESTRITAMENTE em português do Brasil.
    
    Regras de Urgência (Siga de forma absoluta):
    - ALTA: Risco à vida, saúde pública iminente ou acidentes graves (ex: esgoto aberto, fios caídos, semáforo quebrado, risco de dengue). Obrigatório se o Parecer do Auditor apontar risco.
    - MÉDIA: Transtornos à rotina ou perda de infraestrutura sem risco imediato à vida (ex: lâmpada queimada isolada, barulho noturno, vazamento pequeno, buraco em via lenta).
    - BAIXA: Estética urbana, falta de conforto, pequenos incômodos ou abandono (ex: ponto de ônibus sem cobertura, carro abandonado, mato alto em lote fechado, praça usada como estacionamento).
    
    Retorne apenas este JSON:
    {
        "categoria": "[Infraestrutura, Iluminação, Saneamento, Trânsito, Saúde, Perturbação, Outros]",
        "urgencia": "[Alta, Média, Baixa]",
        "resumo_problema": "máx 5 palavras",
        "explicacao": "justificativa curta do porquê desta urgência específica"
    }
    """
    
    prompt_combinado = f"Relato: '{texto_original}'\nParecer do Auditor: '{parecer_risco}'"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": instrucao_despachante},
                {"role": "user", "content": prompt_combinado}
            ],
            model=model,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        resposta_texto = chat_completion.choices[0].message.content
        return json.loads(resposta_texto)
    except json.JSONDecodeError:
        return {"erro": "Falha no parsing JSON do modelo leve", "raw_output": resposta_texto}
    except Exception as e:
         return {"erro": f"Erro na API: {e}"}

def executar_pipeline(texto):
    print(f"Processando: '{texto}'")
    parecer = agente_analista_risco(texto)
    print(f" -> Parecer do Agente 1: {parecer}\n")

    # pausa entre a chamada do agente 1 e agente 2 para evitar rate limit
    time.sleep(2)
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
        "Enxurrada sempre alaga essa rua quando chove, moradores ficam ilhados.",
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

    resultados_finais = []

    casos_de_teste_reduzidos = casos_de_teste[40:42]
    
    print(f"--- INICIANDO PROCESSAMENTO DE {len(casos_de_teste_reduzidos)} CASOS ---\n")

    for i, relato in enumerate(casos_de_teste_reduzidos, 1):
        resultado = executar_pipeline(relato)
        
        print(f"--- RESULTADO FINAL {i} ---")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        print("-" * 40 + "\n")
        
        # Estruturando os dados de forma holística para o CSV
        linha = {
            "id_teste": i,
            "relato": relato,
            "categoria_predita": resultado.get("categoria", "ERRO"),
            "urgencia_predita": resultado.get("urgencia", "ERRO"),
            "explicacao_agente": resultado.get("explicacao", "ERRO")
        }
        resultados_finais.append(linha)
        
        print("Aguardando 2 segundos para respeitar o rate limit do Groq...\n")
        time.sleep(2)

    # Nível mais baixo de persistência: escrevendo direto no disco
    nome_arquivo = "avaliacoes.csv"
    colunas = ["id_teste", "relato", "categoria_predita", "urgencia_predita", "explicacao_agente"]
    
    try:
        with open(nome_arquivo, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=colunas)
            writer.writeheader()
            writer.writerows(resultados_finais)
        print(f"--- SUCESSO! Dados exportados holisticamente para {nome_arquivo} ---")
    except Exception as e:
        print(f"Erro ao salvar o CSV: {e}")