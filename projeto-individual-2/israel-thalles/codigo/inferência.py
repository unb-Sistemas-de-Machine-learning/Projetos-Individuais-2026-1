import sys
import os
import mlflow
from transformers import pipeline
from PIL import Image

def prever_com_guardrails(caminho_imagem):
    # Guardrail 1: Validação de escopo e formato
    if not caminho_imagem.lower().endswith(('.png', '.jpg', '.jpeg')):
        return "❌ ERRO DE ENTRADA: Formato não suportado. O sistema aceita apenas imagens PNG ou JPG."

    try:
        imagem = Image.open(caminho_imagem)
    except Exception:
        return "❌ ERRO: Arquivo corrompido ou ilegível."

    print("Carregando modelo do pipeline...")

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    
    modelo_uri = "models:/SkinCancer_ViT_Model/4"
    
    try:
        # O MLflow já carrega o objeto pronto para uso
        classificador = mlflow.transformers.load_model(modelo_uri, device="cpu")
    except Exception as e:
        return f"❌ ERRO ao carregar modelo do MLflow: {e}. Certifique-se de que o 'mlflow ui' está rodando."
    
    resultados = classificador(imagem)
    melhor_resultado = resultados[0]
    score = melhor_resultado['score']
    
    # Guardrail 2: Recusar respostas com falsa confiança
    # Se o modelo tiver menos de 45% de certeza, barramos a saída
    if score < 0.45:
        return (
            f"⚠️ RESULTADO INCONCLUSIVO (Confiança: {score:.2f})\n"
            f"A imagem não apresenta padrões claros o suficiente para o modelo ou está fora do escopo de treinamento."
        )

    # Guardrail 3: Explicitar Limitações (Disclaimer Médico)
    resposta = (
        f"🔍 Previsão do Modelo: {melhor_resultado['label']}\n"
        f"📊 Confiança: {score:.2f}\n"
        f"-----------------------------------------\n"
        f"🛑 AVISO MÉDICO LEGAL: Este é um sistema experimental de Machine Learning.\n"
        f"A saída não é um diagnóstico e não substitui a avaliação de um dermatologista profissional."
    )
    return resposta

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 codigo/inferência.py <caminho_para_imagem>")
    else:
        caminho = sys.argv[1]
        if os.path.exists(caminho):
            print("\nIniciando análise com Guardrails ativados...\n")
            print(prever_com_guardrails(caminho))
        else:
            print("Erro: Arquivo não encontrado.")