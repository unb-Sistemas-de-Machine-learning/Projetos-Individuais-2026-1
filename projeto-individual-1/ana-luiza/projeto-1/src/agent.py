import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from tools import get_deputado_id, get_gastos_deputado

load_dotenv()

class AuditorAgente:
    def __init__(self):
        # 1. Carrega o RAG (Banco de Leis) que você acabou de criar
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma(persist_directory="./chromadb", embedding_function=self.embeddings)
        
        # 2. Configura o Gemini como o "Cérebro"
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0)
        
        # 3. Cria a corrente de consulta às leis usando a abordagem moderna
        template = """Com base nas leis brasileiras (Código Penal, Lei de Improbidade e Regimento da Câmara), 
analise os seguintes gastos:

Contexto das leis:
{context}

Pergunta:
{question}

Existe algum indício de irregularidade ou gasto suspeito? Cite os artigos das leis se encontrar."""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        
        self.qa_chain = (
            {"context": self.vectorstore.as_retriever(), "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def auditar_deputado(self, nome_deputado, mes, ano):
        print(f"🔍 Auditando {nome_deputado}...")
        
        # Busca dados na API
        dep_id = get_deputado_id(nome_deputado)
        if not dep_id: return "Deputado não encontrado."
        
        gastos = get_gastos_deputado(dep_id, ano, mes)
        
        # Monta o relatório para a IA analisar
        relatorio_gastos = "\n".join([f"- {g['tipoDespesa']}: R$ {g['valorDocumento']} ({g['nomeFornecedor']})" for g in gastos])
        
        # Pergunta para o Gemini cruzando com o RAG (leis)
        pergunta = f"Analise os seguintes gastos do deputado {nome_deputado}:\n{relatorio_gastos}"
        
        return self.qa_chain.invoke(pergunta)

if __name__ == "__main__":
    agente = AuditorAgente()
    
    print("\n🏛️ --- SISTEMA DE AUDITORIA FEDERAL ---")
    
    # Recebe os dados do usuário via terminal
    nome_deputado = input("👤 Digite o nome do deputado: ")
    mes = int(input("📅 Digite o mês (1-12): "))
    ano = int(input("📅 Digite o ano (ex: 2024): "))
    
    resultado = agente.auditar_deputado(nome_deputado, mes, ano)
    
    # Exibe o relatório
    if isinstance(resultado, dict):
        print("\n" + "="*30)
        print(f"📋 RELATÓRIO DE AUDITORIA: {nome_deputado}")
        print("="*30)
        print(resultado.get('result', 'Sem resposta detalhada.'))
    else:
        print(f"\n⚠️ {resultado}")