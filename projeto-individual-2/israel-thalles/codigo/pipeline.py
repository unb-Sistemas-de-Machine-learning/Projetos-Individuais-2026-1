import os
import mlflow
from transformers import pipeline
from PIL import Image

def executar_pipeline():
    # 1. Configura o MLflow
    mlflow.set_tracking_uri("http://127.0.0.1:5000") # Aponta para o servidor local
    mlflow.set_experiment("Deteccao_Cancer_Pele")

    nome_do_modelo = "Anwarkh1/Skin_Cancer-Image_Classification"
    
    print(f"Carregando o modelo {nome_do_modelo}...")
    # O pipeline do Hugging Face já abstrai o pré-processamento (resize, normalize)
    classificador = pipeline("image-classification", model=nome_do_modelo, device="cpu")

    # Inicia o rastreamento do experimento
    with mlflow.start_run(run_name="Avaliacao_Baseline"):
        
        # --- REGISTRO DE PARÂMETROS (Item 5.1 do Relatório) ---
        mlflow.log_param("nome_do_modelo", nome_do_modelo)
        mlflow.log_param("conjunto_de_dados", "ISIC_Subset_50")
        mlflow.log_param("tarefa", "image-classification")

        previsões_corretas = 0
        total_de_imagens = 0
        categorias = ["maligno", "benigno"]
        
        print("Iniciando inferência nas imagens...")
        
        # --- AVALIAÇÃO DO MODELO ---
        for categoria in categorias:
            pasta = f"./dados/{categoria}"
            if not os.path.exists(pasta):
                print(f"Aviso: Pasta {pasta} não encontrada.")
                continue
                
            for nome_do_arquivo in os.listdir(pasta):
                if nome_do_arquivo.endswith(".png") or nome_do_arquivo.endswith(".jpg"):
                    caminho_imagem = os.path.join(pasta, nome_do_arquivo)
                    imagem = Image.open(caminho_imagem)
                    
                    # Faz a previsão
                    resultado = classificador(imagem)
                    melhor_previsao = resultado[0]['label'].lower()

                    # O modelo Anwarkh1 foi treinado no dataset HAM10000 (7 classes)
                    # Vamos mapear essas 7 classes para os nossos 2 supergrupos (Maligno/Benigno)
                    
                    classes_malignas_do_modelo = ['melanoma', 'basal_cell_carcinoma', 'actinic_keratoses']
                    
                    # Verificamos em qual grupo a previsão do modelo se encaixa
                    previsao_e_maligna = any(doenca in melhor_previsao for doenca in classes_malignas_do_modelo)
                    
                    está_correto = False
                    
                    if categoria == "maligno" and previsao_e_maligna:
                        está_correto = True
                    elif categoria == "benigno" and not previsao_e_maligna:
                        está_correto = True
                        
                    print(f"Real: {categoria.upper()} | Modelo Disse: {melhor_previsao} -> Acertou? {está_correto}")
                    
                    if está_correto:
                        previsões_corretas += 1
                    total_de_imagens += 1

        # --- REGISTRO DE MÉTRICAS (Item 5.1 do Relatório) ---
        acurácia = previsões_corretas / total_de_imagens if total_de_imagens > 0 else 0
        mlflow.log_metric("acurácia", acurácia)
        mlflow.log_metric("total_de_imagens_testadas", total_de_imagens)

        # --- REGISTRO DO MODELO E VERSIONAMENTO (Item 5.2 do Relatório) ---
        print("Salvando e versionando o modelo no MLflow...")
        mlflow.transformers.log_model(
            transformers_model=classificador,
            artifact_path="modelo_classificador",
            registered_model_name="SkinCancer_ViT_Model"
        )

        print(f"✅ Pipeline concluído! Imagens testadas: {total_de_imagens} | Acurácia: {acurácia:.2f}")

if __name__ == "__main__":
    executar_pipeline()