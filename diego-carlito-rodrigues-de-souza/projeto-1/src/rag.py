import logging
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "chroma_db"
COLLECTION_NAME = "concursos_ti"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_collection() -> chromadb.Collection:
    DB_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    logger.info("Coleção RAG carregada: %d documentos indexados.", collection.count())
    return collection


def ingest_text(
    text: str,
    doc_id: str,
    banca: str,
    materia: str,
    tipo: str = "questao",
    dificuldade: str = "media",
) -> None:
    collection = get_collection()
    existing = collection.get(ids=[doc_id])
    if existing["ids"]:
        logger.debug("Documento '%s' já indexado, pulando.", doc_id)
        return
    collection.add(
        documents=[text],
        ids=[doc_id],
        metadatas=[{"banca": banca.upper(), "materia": materia, "tipo": tipo, "dificuldade": dificuldade}],
    )
    logger.info("Documento '%s' indexado com sucesso.", doc_id)


def ingest_pdf(pdf_path: str, banca: str, materia: str) -> int:
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Instale pdfplumber: pip install pdfplumber")
    path = Path(pdf_path)
    count = 0
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text or len(text.strip()) < 50:
                continue
            ingest_text(text=text, doc_id=f"{path.stem}_p{i+1}", banca=banca, materia=materia, tipo="edital")
            count += 1
    logger.info("PDF '%s' indexado: %d páginas.", path.name, count)
    return count


def search(
    query: str,
    banca: str | None = None,
    materia: str | None = None,
    tipo: str | None = None,
    dificuldade: str | None = None,
    n_results: int = 5,
) -> list[dict]:
    collection = get_collection()
    if collection.count() == 0:
        logger.warning("Base RAG vazia. Execute a ingestão primeiro.")
        return []
    where: dict = {}
    filters = {
        "banca": banca.upper() if banca else None,
        "materia": materia,
        "tipo": tipo,
        "dificuldade": dificuldade,
    }
    active = {k: v for k, v in filters.items() if v is not None}
    if len(active) == 1:
        where = active
    elif len(active) > 1:
        where = {"$and": [{k: v} for k, v in active.items()]}
    kwargs = dict(query_texts=[query], n_results=min(n_results, collection.count()))
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    output = []
    for i, doc_id in enumerate(results["ids"][0]):
        output.append({
            "id": doc_id,
            "text": results["documents"][0][i],
            "score": round(1 - results["distances"][0][i], 4),
            **results["metadatas"][0][i],
        })
    logger.info("Busca RAG: %d resultados para '%s'.", len(output), query[:60])
    return output


def search_questions_by_difficulty(
    materia: str,
    banca: str,
    dificuldades: list[str] = ["facil", "media", "dificil"],
) -> list[dict]:
    questoes = []
    for dif in dificuldades:
        results = search(query=materia, banca=banca, materia=materia, tipo="questao", dificuldade=dif, n_results=1)
        if results:
            questoes.append(results[0])
    return questoes


BANCAS = ["CESPE", "FCC", "FGV", "VUNESP", "IDECAN", "IBFC", "QUADRIX"]

MATERIAS = [
    "Redes de Computadores",
    "Banco de Dados",
    "Sistemas Operacionais",
    "Segurança da Informação",
    "Engenharia de Software",
    "Arquitetura de Computadores",
    "Programação e Algoritmos",
    "Governança de TI",
    "Legislação de TI",
    "Inteligência Artificial",
]

SAMPLE_DATA = [
    {
        "doc_id": "redes_cespe_001",
        "text": (
            "O protocolo TCP pertence à camada de transporte do modelo OSI e garante a entrega "
            "ordenada e confiável de segmentos por meio de confirmações (ACKs), controle de fluxo "
            "e retransmissão em caso de perda de pacotes. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Redes de Computadores", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "redes_cespe_002",
        "text": (
            "No modelo OSI, a camada responsável pelo roteamento de pacotes entre redes distintas, "
            "determinando o melhor caminho com base em endereços lógicos, é a camada de rede. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Redes de Computadores", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "redes_cespe_003",
        "text": (
            "Em uma VPN IPSec operando em modo túnel com IKEv2, a fase 1 (IKE_SA_INIT) é responsável "
            "pela negociação dos algoritmos criptográficos e pela troca de material Diffie-Hellman, "
            "enquanto a fase 2 (IKE_AUTH) realiza a autenticação mútua dos peers. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Redes de Computadores", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "redes_fcc_001",
        "text": (
            "Qual protocolo da camada de aplicação é utilizado para resolução de nomes de domínio "
            "em endereços IP, operando por padrão na porta 53?\n"
            "A) DHCP\nB) FTP\nC) DNS\nD) SNMP\nE) SMTP"
        ),
        "banca": "FCC", "materia": "Redes de Computadores", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "redes_fcc_002",
        "text": (
            "Em relação ao protocolo OSPF, assinale a alternativa correta:\n"
            "A) É um protocolo de roteamento por vetor de distância.\n"
            "B) Utiliza o algoritmo de Bellman-Ford para calcular rotas.\n"
            "C) É um protocolo de estado de enlace que utiliza o algoritmo de Dijkstra.\n"
            "D) Opera apenas em redes classful.\n"
            "E) Não suporta VLSM."
        ),
        "banca": "FCC", "materia": "Redes de Computadores", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "redes_fgv_001",
        "text": (
            "Considerando o protocolo IPv6, analise as afirmações:\n"
            "I. Os endereços IPv6 possuem 128 bits.\n"
            "II. O IPv6 elimina a necessidade de NAT em redes de larga escala.\n"
            "III. O cabeçalho IPv6 é menor que o do IPv4.\n"
            "Estão corretas apenas:\n"
            "A) I\nB) I e II\nC) II e III\nD) I e III\nE) I, II e III"
        ),
        "banca": "FGV", "materia": "Redes de Computadores", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "bd_cespe_001",
        "text": (
            "A propriedade de atomicidade das transações em banco de dados garante que todas as "
            "operações de uma transação sejam executadas completamente ou que nenhuma delas seja "
            "efetivada, impedindo estados intermediários inconsistentes. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "bd_cespe_002",
        "text": (
            "A Terceira Forma Normal (3FN) exige que todos os atributos não-chave de uma relação "
            "sejam dependentes apenas da chave primária, eliminando dependências transitivas entre "
            "atributos não-chave. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "bd_cespe_003",
        "text": (
            "Em um banco de dados relacional, o uso de índices do tipo B-Tree é mais adequado para "
            "consultas de igualdade exata em colunas de alta cardinalidade, enquanto índices Bitmap "
            "são mais eficientes para colunas de baixa cardinalidade em ambientes de data warehouse. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "bd_fcc_001",
        "text": (
            "Qual das alternativas descreve corretamente a propriedade de isolamento (I) do modelo ACID?\n"
            "A) Garante que os dados gravados persistam mesmo após falhas.\n"
            "B) Garante que transações concorrentes não interfiram entre si.\n"
            "C) Garante que todas as operações da transação sejam executadas ou nenhuma.\n"
            "D) Garante que o banco passe de um estado consistente para outro.\n"
            "E) Garante a integridade referencial entre tabelas."
        ),
        "banca": "FCC", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "bd_fcc_002",
        "text": (
            "Em SQL, a cláusula que filtra grupos após a aplicação de funções de agregação é:\n"
            "A) WHERE\nB) GROUP BY\nC) HAVING\nD) ORDER BY\nE) DISTINCT"
        ),
        "banca": "FCC", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "bd_fgv_001",
        "text": (
            "Sobre bancos de dados NoSQL, analise as afirmações:\n"
            "I. Bancos do tipo chave-valor oferecem consultas complexas semelhantes ao SQL.\n"
            "II. Bancos orientados a documentos armazenam dados em formatos como JSON ou BSON.\n"
            "III. O teorema CAP afirma que sistemas distribuídos não podem garantir simultaneamente "
            "consistência, disponibilidade e tolerância a partições.\n"
            "Estão corretas:\n"
            "A) Apenas I\nB) Apenas II\nC) II e III\nD) I e III\nE) I, II e III"
        ),
        "banca": "FGV", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "so_cespe_001",
        "text": (
            "O escalonamento Round-Robin atribui fatias de tempo iguais (quantum) a cada processo "
            "na fila de prontos, garantindo que nenhum processo sofra inanição (starvation). (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Sistemas Operacionais", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "so_cespe_002",
        "text": (
            "Em sistemas operacionais, a técnica de memória virtual permite que processos utilizem "
            "mais memória do que a RAM fisicamente disponível, mapeando páginas em disco por meio "
            "do mecanismo de paginação por demanda. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Sistemas Operacionais", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "so_cespe_003",
        "text": (
            "O problema do deadlock em sistemas operacionais pode ser detectado por meio do algoritmo "
            "do banqueiro, que verifica se o estado do sistema é seguro antes de alocar recursos "
            "adicionais a um processo. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Sistemas Operacionais", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "so_fcc_001",
        "text": (
            "Qual mecanismo do sistema operacional é responsável por mapear endereços virtuais em "
            "endereços físicos de memória?\n"
            "A) Escalonador de processos\nB) Gerenciador de arquivos\n"
            "C) Unidade de Gerenciamento de Memória (MMU)\nD) Spooler\nE) Kernel de tempo real"
        ),
        "banca": "FCC", "materia": "Sistemas Operacionais", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "seg_cespe_001",
        "text": (
            "A criptografia assimétrica utiliza um par de chaves matematicamente relacionadas: "
            "a chave pública, usada para cifrar ou verificar assinaturas, e a chave privada, "
            "usada para decifrar ou assinar digitalmente. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Segurança da Informação", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "seg_cespe_002",
        "text": (
            "Um ataque do tipo SQL Injection explora falhas na validação de entradas de usuário "
            "para inserir comandos SQL maliciosos, podendo resultar em acesso não autorizado, "
            "alteração ou exclusão de dados no banco de dados. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Segurança da Informação", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "seg_cespe_003",
        "text": (
            "O protocolo TLS 1.3 eliminou suporte a algoritmos considerados inseguros, como RC4 "
            "e MD5, e reduziu a latência do handshake para 1-RTT na maioria dos casos, além de "
            "suportar 0-RTT para reconexões, embora este modo introduza riscos de ataques de replay. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Segurança da Informação", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "seg_fcc_001",
        "text": (
            "Qual das alternativas descreve corretamente o conceito de autenticação multifator (MFA)?\n"
            "A) Uso de senha longa com caracteres especiais.\n"
            "B) Combinação de dois ou mais fatores: algo que você sabe, tem ou é.\n"
            "C) Uso de biometria como único fator de autenticação.\n"
            "D) Renovação periódica de senhas a cada 30 dias.\n"
            "E) Uso de certificado digital para criptografar a senha."
        ),
        "banca": "FCC", "materia": "Segurança da Informação", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "eng_cespe_001",
        "text": (
            "No modelo Scrum, o Product Backlog é uma lista ordenada de tudo que é necessário no "
            "produto, sendo o Product Owner o responsável por sua criação, manutenção e priorização. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Engenharia de Software", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "eng_cespe_002",
        "text": (
            "O princípio da responsabilidade única (SRP) do SOLID estabelece que uma classe deve "
            "ter apenas um motivo para mudar, ou seja, deve encapsular apenas uma responsabilidade "
            "ou eixo de variação do sistema. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Engenharia de Software", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "eng_fcc_001",
        "text": (
            "Qual das alternativas descreve corretamente o padrão de projeto (design pattern) Observer?\n"
            "A) Define uma interface para criar objetos, deixando subclasses decidirem qual instanciar.\n"
            "B) Permite que um objeto notifique automaticamente seus dependentes sobre mudanças de estado.\n"
            "C) Garante que uma classe tenha apenas uma instância e fornece ponto de acesso global.\n"
            "D) Converte a interface de uma classe em outra esperada pelos clientes.\n"
            "E) Separa a construção de um objeto complexo de sua representação."
        ),
        "banca": "FCC", "materia": "Engenharia de Software", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "eng_cespe_003",
        "text": (
            "Em arquitetura de microsserviços, o padrão Saga resolve o problema de transações "
            "distribuídas por meio de uma sequência de transações locais, cada uma publicando "
            "eventos ou mensagens para acionar a próxima etapa, com compensações para desfazer "
            "operações em caso de falha. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Engenharia de Software", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "gov_cespe_001",
        "text": (
            "O COBIT 2019 é um framework de governança e gestão de TI que organiza seus objetivos "
            "em um sistema de governança baseado em princípios, sendo um de seus principais "
            "conceitos a separação entre governança (avaliar, dirigir e monitorar) e gestão "
            "(planejar, construir, executar e monitorar). (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Governança de TI", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "gov_cespe_002",
        "text": (
            "No framework ITIL 4, a cadeia de valor de serviço (Service Value Chain) é composta "
            "por seis atividades: planejar, melhorar, engajar, projetar e fazer a transição, "
            "obter/construir e entregar e suportar. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Governança de TI", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "gov_fcc_001",
        "text": (
            "Qual dos seguintes não é um domínio de processo do CMMI-DEV?\n"
            "A) Gestão de Requisitos\nB) Planejamento de Projeto\n"
            "C) Gestão de Configuração\nD) Gestão de Portfólio de Investimentos\n"
            "E) Garantia de Qualidade de Processo e Produto"
        ),
        "banca": "FCC", "materia": "Governança de TI", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "arq_cespe_001",
        "text": (
            "A arquitetura RISC caracteriza-se por um conjunto reduzido de instruções de tamanho "
            "fixo, execução em um único ciclo de clock e uso intensivo de registradores, em "
            "contraste com a arquitetura CISC, que possui instruções complexas de tamanho variável. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Arquitetura de Computadores", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "arq_fcc_001",
        "text": (
            "Em relação à hierarquia de memória em computadores, qual afirmação está correta?\n"
            "A) A memória cache é mais lenta que a RAM, porém mais barata.\n"
            "B) Registradores têm maior capacidade que a memória RAM.\n"
            "C) A cache L1 é a mais próxima do processador e a mais rápida.\n"
            "D) O disco rígido possui latência menor que a memória RAM.\n"
            "E) A memória virtual é mais rápida que a cache L2."
        ),
        "banca": "FCC", "materia": "Arquitetura de Computadores", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "prog_cespe_001",
        "text": (
            "Em Python, listas e tuplas são estruturas de dados sequenciais, porém as tuplas são "
            "imutáveis, o que as torna mais eficientes em termos de memória e adequadas para "
            "armazenar coleções de dados que não devem ser alteradas. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Programação e Algoritmos", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "prog_cespe_002",
        "text": (
            "A complexidade de tempo do algoritmo QuickSort no pior caso é O(n²), situação que "
            "ocorre quando o pivô escolhido é sempre o maior ou o menor elemento da partição, "
            "enquanto no caso médio sua complexidade é O(n log n). (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Programação e Algoritmos", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "prog_fcc_001",
        "text": (
            "Qual estrutura de dados é mais adequada para implementar uma fila de prioridade "
            "onde o elemento de maior prioridade é sempre removido primeiro?\n"
            "A) Lista encadeada simples\nB) Pilha (Stack)\nC) Heap binário\n"
            "D) Fila circular\nE) Árvore AVL"
        ),
        "banca": "FCC", "materia": "Programação e Algoritmos", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "ia_cespe_001",
        "text": (
            "Em aprendizado de máquina supervisionado, o overfitting ocorre quando o modelo se "
            "ajusta excessivamente aos dados de treinamento, perdendo capacidade de generalização "
            "para novos dados, podendo ser mitigado por técnicas como regularização e dropout. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Inteligência Artificial", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "ia_cespe_002",
        "text": (
            "Redes neurais convolucionais (CNNs) são especialmente eficazes no processamento de "
            "dados com estrutura de grade, como imagens, pois utilizam operações de convolução "
            "para extrair automaticamente hierarquias de características espaciais. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Inteligência Artificial", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "leg_cespe_001",
        "text": (
            "A Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018) estabelece que o "
            "tratamento de dados pessoais somente poderá ser realizado mediante uma das bases "
            "legais previstas no art. 7º, sendo o consentimento do titular apenas uma delas. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Legislação de TI", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "leg_cespe_002",
        "text": (
            "A Lei nº 12.965/2014 (Marco Civil da Internet) consagra a neutralidade de rede como "
            "princípio, proibindo que provedores de conexão discriminem pacotes de dados com base "
            "em seu conteúdo, origem, destino ou serviço, salvo regulamentação específica. (Certo/Errado)"
        ),
        "banca": "CESPE", "materia": "Legislação de TI", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "resumo_redes_001",
        "text": (
            "Resumo — Redes de Computadores: Tópicos de alta incidência em concursos: "
            "Modelo OSI (7 camadas) e TCP/IP (4 camadas); endereçamento IPv4 e IPv6; sub-redes "
            "e CIDR; protocolos de roteamento (RIP, OSPF, BGP); switching e VLANs; "
            "DNS, DHCP, HTTP/HTTPS, FTP, SMTP, IMAP; firewalls, IDS e IPS; VPN e túneis; "
            "Wi-Fi (802.11) e Bluetooth; QoS e SLA. Bancas CESPE e FCC cobram mais profundidade "
            "em protocolos de roteamento e segurança de redes."
        ),
        "banca": "CESPE", "materia": "Redes de Computadores", "tipo": "resumo", "dificuldade": "media",
    },
    {
        "doc_id": "resumo_bd_001",
        "text": (
            "Resumo — Banco de Dados: Tópicos de alta incidência: modelo relacional e SQL completo "
            "(DDL, DML, DCL, TCL); normalização (1FN a BCNF); transações e propriedades ACID; "
            "índices B-Tree e Bitmap; stored procedures e triggers; bancos NoSQL (documento, "
            "chave-valor, coluna, grafo); teorema CAP; data warehouse, OLAP e ETL; modelagem "
            "ER e DER. FCC cobra intensamente SQL e normalização. CESPE cobra transações e NoSQL."
        ),
        "banca": "FCC", "materia": "Banco de Dados", "tipo": "resumo", "dificuldade": "media",
    },
    {
        "doc_id": "resumo_seg_001",
        "text": (
            "Resumo — Segurança da Informação: Tópicos de alta incidência: criptografia simétrica "
            "(AES, DES) e assimétrica (RSA, ECC); funções hash (MD5, SHA-1, SHA-256); PKI e "
            "certificados digitais; protocolos SSL/TLS; autenticação e controle de acesso (RBAC, "
            "DAC, MAC); principais ataques (phishing, ransomware, DDoS, SQL Injection, XSS); "
            "OWASP Top 10; normas ISO 27001 e 27002; LGPD. CESPE e FCC cobram muito criptografia "
            "e ataques."
        ),
        "banca": "CESPE", "materia": "Segurança da Informação", "tipo": "resumo", "dificuldade": "media",
    },
    {
        "doc_id": "resumo_eng_001",
        "text": (
            "Resumo — Engenharia de Software: Tópicos de alta incidência: metodologias ágeis "
            "(Scrum, Kanban, XP); RUP e ciclo de vida clássico; UML (casos de uso, classes, "
            "sequência, atividades); padrões de projeto GoF (criacionais, estruturais, "
            "comportamentais); princípios SOLID; testes de software (unitário, integração, "
            "sistema, aceitação); DevOps e CI/CD; métricas de qualidade (complexidade ciclomática, "
            "cobertura de testes). CESPE cobra UML e SOLID com frequência."
        ),
        "banca": "CESPE", "materia": "Engenharia de Software", "tipo": "resumo", "dificuldade": "media",
    },
    {
        "doc_id": "resumo_gov_001",
        "text": (
            "Resumo — Governança de TI: Tópicos de alta incidência: ITIL 4 (cadeia de valor, "
            "práticas de gestão); COBIT 2019 (princípios, domínios, objetivos); CMMI-DEV "
            "(níveis de maturidade 1 a 5); ISO/IEC 38500; gestão de projetos com PMBOK e "
            "metodologias ágeis; gestão de riscos de TI; BPM e processos de negócio; "
            "planejamento estratégico de TI (PDTI). CESPE cobra muito ITIL e COBIT."
        ),
        "banca": "CESPE", "materia": "Governança de TI", "tipo": "resumo", "dificuldade": "media",
    },
]


def seed_sample_data() -> None:
    collection = get_collection()
    if collection.count() > 0:
        logger.info("Base RAG já populada (%d docs). Seed ignorado.", collection.count())
        return
    logger.info("Populando base RAG com dados de exemplo...")
    for item in SAMPLE_DATA:
        ingest_text(**item)
    logger.info("Seed concluído: %d documentos indexados.", len(SAMPLE_DATA))
