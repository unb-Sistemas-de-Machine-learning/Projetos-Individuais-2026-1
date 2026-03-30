import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def setup_rag():
    print("🚀 Iniciando Setup do RAG (Modo Local - Sem Limites de API)")
    
    DATA_PATH = "./data"
    CHROMA_PATH = "./chromadb"

    # 1. Limpeza de Segurança
    if os.path.exists(CHROMA_PATH):
        print("🧹 Removendo banco de dados antigo para evitar conflitos...")
        shutil.rmtree(CHROMA_PATH)

    if not os.path.exists(DATA_PATH) or not os.listdir(DATA_PATH):
        print(f"❌ ERRO: A pasta '{DATA_PATH}' está vazia. Coloque os PDFs lá!")
        return

    # 2. Carregamento dos PDFs
    print("📄 Lendo todos os documentos da pasta data/...")
    loader = DirectoryLoader(DATA_PATH, glob="./*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    print(f"✅ {len(docs)} páginas carregadas.")

    # 3. Fragmentação (Chunking)
    # Como o processamento é local, podemos usar chunks menores e mais precisos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(docs)
    print(f"✂️ Texto dividido em {len(splits)} pedaços.")

    # 4. Criação dos Embeddings Locais
    print("🧠 Gerando vetores localmente (Isso não gasta sua cota do Gemini)...")
    # O modelo 'all-MiniLM-L6-v2' é rápido, leve e excelente para português/inglês
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Salvando no ChromaDB
    print("💾 Criando banco de dados em './chromadb'...")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=CHROMA_PATH
    )

    print(f"✨ TUDO PRONTO! {len(splits)} fragmentos salvos com sucesso.")
    print("Agora seu Agente pode consultar as leis offline.")

if __name__ == "__main__":
    setup_rag()