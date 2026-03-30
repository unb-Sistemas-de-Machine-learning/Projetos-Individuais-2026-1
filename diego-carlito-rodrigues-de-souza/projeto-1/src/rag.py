import os
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
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
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
    tipo: str = "questao",  # "questao" | "resumo" | "edital"
    dificuldade: str = "media",  # "facil" | "media" | "dificil"
) -> None:
    
    collection = get_collection()

    existing = collection.get(ids=[doc_id])
    if existing["ids"]:
        logger.debug("Documento '%s' já indexado, pulando.", doc_id)
        return

    collection.add(
        documents=[text],
        ids=[doc_id],
        metadatas=[{
            "banca": banca.upper(),
            "materia": materia,
            "tipo": tipo,
            "dificuldade": dificuldade,
        }],
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
            doc_id = f"{path.stem}_p{i+1}"
            ingest_text(
                text=text,
                doc_id=doc_id,
                banca=banca,
                materia=materia,
                tipo="edital",
            )
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
            "score": round(1 - results["distances"][0][i], 4),  # cosine → similarity
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
        results = search(
            query=materia,
            banca=banca,
            materia=materia,
            tipo="questao",
            dificuldade=dif,
            n_results=1,
        )
        if results:
            questoes.append(results[0])
    return questoes

SAMPLE_DATA = [
    {
        "doc_id": "redes_cespe_001",
        "text": (
            "Questão CESPE — Redes (fácil): O protocolo TCP garante a entrega "
            "ordenada de pacotes por meio de confirmações (ACKs) e retransmissão "
            "em caso de perda. (Certo / Errado)"
        ),
        "banca": "CESPE", "materia": "Redes", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "redes_cespe_002",
        "text": (
            "Questão CESPE — Redes (média): Em relação ao modelo OSI, assinale "
            "a opção correta quanto à camada responsável pelo roteamento de pacotes "
            "entre redes distintas."
        ),
        "banca": "CESPE", "materia": "Redes", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "redes_cespe_003",
        "text": (
            "Questão CESPE — Redes (difícil): Analise o cenário de uma VPN IPSec "
            "em modo túnel com IKEv2. Indique qual fase de negociação é responsável "
            "pela autenticação mútua e derivação do material de chaveamento."
        ),
        "banca": "CESPE", "materia": "Redes", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "bd_fcc_001",
        "text": (
            "Questão FCC — Banco de Dados (fácil): A propriedade ACID que garante "
            "que uma transação seja executada completamente ou não seja executada "
            "é denominada: (A) Consistência (B) Atomicidade (C) Isolamento (D) Durabilidade"
        ),
        "banca": "FCC", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "bd_fcc_002",
        "text": (
            "Questão FCC — Banco de Dados (média): Sobre normalização, a Terceira "
            "Forma Normal (3FN) exige que todos os atributos não-chave sejam "
            "dependentes apenas da chave primária, eliminando dependências transitivas."
        ),
        "banca": "FCC", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "media",
    },
    {
        "doc_id": "bd_fcc_003",
        "text": (
            "Questão FCC — Banco de Dados (difícil): Considerando o plano de execução "
            "de uma consulta SQL com múltiplos JOINs e subconsultas correlacionadas, "
            "descreva as estratégias de otimização baseadas em índices compostos e "
            "estatísticas do otimizador de consultas."
        ),
        "banca": "FCC", "materia": "Banco de Dados", "tipo": "questao", "dificuldade": "dificil",
    },
    {
        "doc_id": "so_cespe_001",
        "text": (
            "Questão CESPE — Sistemas Operacionais (fácil): O escalonamento Round-Robin "
            "atribui fatias de tempo iguais a cada processo, garantindo que nenhum "
            "processo sofra inanição (starvation). (Certo / Errado)"
        ),
        "banca": "CESPE", "materia": "Sistemas Operacionais", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "seg_cespe_001",
        "text": (
            "Questão CESPE — Segurança da Informação (fácil): A criptografia assimétrica "
            "utiliza um par de chaves (pública e privada), sendo a chave pública usada "
            "para cifrar e a privada para decifrar. (Certo / Errado)"
        ),
        "banca": "CESPE", "materia": "Segurança da Informação", "tipo": "questao", "dificuldade": "facil",
    },
    {
        "doc_id": "resumo_redes_001",
        "text": (
            "Resumo — Redes de Computadores: Tópicos essenciais para concursos de TI: "
            "Modelo OSI (7 camadas) e TCP/IP (4 camadas), endereçamento IP (IPv4/IPv6), "
            "sub-redes e CIDR, protocolos de roteamento (RIP, OSPF, BGP), "
            "DNS, DHCP, HTTP/HTTPS, FTP, SMTP. Frequência alta nas bancas CESPE e FCC."
        ),
        "banca": "GERAL", "materia": "Redes", "tipo": "resumo", "dificuldade": "media",
    },
    {
        "doc_id": "resumo_bd_001",
        "text": (
            "Resumo — Banco de Dados: Tópicos essenciais para concursos de TI: "
            "Modelo relacional e SQL (DDL, DML, DCL), normalização (1FN, 2FN, 3FN, BCNF), "
            "transações e propriedades ACID, índices e otimização de consultas, "
            "bancos NoSQL (conceitos e tipos). Frequência alta nas bancas FCC e FGV."
        ),
        "banca": "GERAL", "materia": "Banco de Dados", "tipo": "resumo", "dificuldade": "media",
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