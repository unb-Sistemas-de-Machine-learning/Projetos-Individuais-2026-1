# src/main.py
import os
import mlflow
import pandas as pd
from transformers import pipeline

def carregar_metadados(caminho_csv=None):
    """Carrega os arquivos metadata.csv encontrados dentro da pasta `data/` e concatena.
    Se `caminho_csv` for fornecido, tenta abrir esse arquivo diretamente.
    Retorna um DataFrame ou None em caso de falha.
    """
    try:
        if caminho_csv:
            return pd.read_csv(caminho_csv)

        # Procura por metadata.csv nas subpastas de `data/`
        arquivos = []
        for root, _, files in os.walk("data"):
            for f in files:
                if f.lower() == "metadata.csv":
                    arquivos.append(os.path.join(root, f))

        if not arquivos:
            print("Nenhum arquivo metadata.csv encontrado em data/.")
            return None

        dfs = [pd.read_csv(p) for p in arquivos]
        df_concat = pd.concat(dfs, ignore_index=True)
        return df_concat
    except Exception as e:
        print(f"Erro ao carregar metadados: {e}")
        return None

def validar_guardrail(nome_arquivo, df_metadados):
    """
    Motor de Regras de Negócio (Guardrails)
    Aplica validações de escopo, qualidade e ética antes da inferência.
    """
    # 1. Extrai o ID
    image_id = os.path.splitext(nome_arquivo)[0]
    
    # Busca a imagem no CSV
    linha_dados = df_metadados[df_metadados['isic_id'] == image_id]
    
    # Regra 1: Validação de Escopo
    if linha_dados.empty:
        return False, "BLOQUEADO [Escopo]: Imagem não consta nos registros oficiais."
    
    # Extrai a linha como um dicionário para facilitar a leitura
    dados_paciente = linha_dados.iloc[0]
    
    # Regra 2: Validação de Equipamento/Qualidade
    # Verifica se a imagem é do tipo dermoscópico
    tipo_imagem = str(dados_paciente.get('image_type', '')).lower()
    if 'dermoscopic' not in tipo_imagem:
        return False, f"BLOQUEADO [Qualidade]: Equipamento não suportado ({tipo_imagem}). Requer imagem dermoscópica."
    
    # Regra 3: Validação Ética e Legal (Idade)
    # Tenta converter a idade para número
    try:
        idade = float(dados_paciente.get('age_approx', 0))
        if pd.notna(idade) and idade < 18:
            return False, f"BLOQUEADO [Ética]: Inferência não permitida para menores de idade ({idade} anos)."
    except ValueError:
        pass # Ignora se a idade for 'Unknown' ou texto inválido
        
    return True, f"Validado (Paciente {dados_paciente.get('sex', 'N/A')}, {dados_paciente.get('anatom_site_general', 'local não informado')})"

def avaliar_modelo():
    print("Carregando o modelo pré-treinado...")
    # Config
    preferred_model = os.environ.get("HF_MODEL_ID", "Anwarkh1/Skin_Cancer-Image_Classification")
    fallback_model = os.environ.get("HF_FALLBACK_MODEL", "google/vit-base-patch16-224")
    local_model_path = os.environ.get("LOCAL_MODEL_PATH")
    hf_token = os.environ.get("HUGGINGFACE_HUB_TOKEN") or os.environ.get("HF_TOKEN")

    classificador = None
    modelo_usado = None

    def try_pipeline(model_identifier, use_token=None):
        if use_token:
            return pipeline("image-classification", model=model_identifier, use_auth_token=use_token)
        return pipeline("image-classification", model=model_identifier)

    # Tenta detectar e carregar modelos Keras hospedados no repo HF
    def try_load_keras_from_hf(repo_id, token=None):
        try:
            from huggingface_hub import list_repo_files, hf_hub_download
        except Exception:
            return None, None

        try:
            files = list_repo_files(repo_id, token=token)
            for f in files:
                if f.lower().endswith((".keras", ".h5")):
                    # baixa o arquivo e tenta carregar com tensorflow.keras
                    local_path = hf_hub_download(repo_id=repo_id, filename=f, token=token)
                    try:
                        import tensorflow as tf
                        import numpy as np
                        from PIL import Image

                        model_keras = tf.keras.models.load_model(local_path)

                        def keras_classifier(image_path):
                            img = Image.open(image_path).convert('RGB')
                            try:
                                _, h, w, _ = model_keras.input_shape
                            except Exception:
                                # fallback para 224x224
                                h, w = 224, 224
                            img = img.resize((w, h))
                            arr = np.array(img).astype('float32') / 255.0
                            arr = np.expand_dims(arr, axis=0)
                            preds = model_keras.predict(arr)
                            # interpreta saída binária ou softmax
                            if preds.ndim == 2 and preds.shape[1] == 1:
                                prob = float(preds[0][0])
                                label = 'malignant' if prob > 0.5 else 'benign'
                                return [{'label': label, 'score': prob}]
                            else:
                                idx = int(preds.argmax(axis=-1)[0])
                                score = float(preds[0][idx])
                                # assume ordem [benign, malignant] if 2 classes
                                labels = ['benign', 'malignant']
                                lab = labels[idx] if idx < len(labels) else str(idx)
                                return [{'label': lab, 'score': score}]

                        return keras_classifier, f
                    except ImportError:
                        print("TensorFlow não está instalado. Instale com: pip install tensorflow pillow numpy")
                        return None, None
                    except Exception as e:
                        print(f"Falha ao carregar modelo Keras do repositório: {e}")
                        return None, None
        except Exception:
            return None, None


    # Tenta carregar preferencial (com token se houver)
    try:
        classificador = try_pipeline(preferred_model, hf_token)
        modelo_usado = preferred_model
    except Exception as e:
        print(f"Falha ao carregar modelo '{preferred_model}': {e}")
        # Tenta carregar modelo Keras armazenado no repositório HF
        try:
            keras_clf, keras_file = try_load_keras_from_hf(preferred_model, hf_token)
            if keras_clf is not None:
                classificador = keras_clf
                modelo_usado = f"{preferred_model}:{keras_file}"
                print(f"Carregado modelo Keras do repo: {keras_file}")
        except Exception:
            pass
        # Tenta local
        if local_model_path:
            try:
                classificador = try_pipeline(local_model_path)
                modelo_usado = local_model_path
                print(f"Carregado modelo local: {local_model_path}")
            except Exception as e_local:
                print(f"Falha ao carregar modelo local '{local_model_path}': {e_local}")

        # Tenta fallback
        if classificador is None:
            print(f"Tentando carregar modelo de fallback '{fallback_model}'...")
            try:
                classificador = try_pipeline(fallback_model, hf_token)
                modelo_usado = fallback_model
            except Exception as e2:
                print(f"Falha ao carregar modelo de fallback: {e2}")

    if classificador is None:
        print("Aborting: nenhum modelo disponível para inferência. Verifique HF_MODEL_ID, HUGGINGFACE_HUB_TOKEN ou LOCAL_MODEL_PATH.")
        return

    # Sanity check rápido: prediz uma imagem de exemplo para checar labels
    try:
        sample_image = None
        for root, _, files in os.walk("data"):
            for f in files:
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    sample_image = os.path.join(root, f)
                    break
            if sample_image:
                break

        if sample_image:
            preview = classificador(sample_image)
            labels = [r.get('label', '') for r in preview]
            labels_lower = " ".join([l.lower() for l in labels])
            # expõe uma tag no mlflow (se houver conexão) para inspeção
            try:
                mlflow.set_tag("model_label_preview", labels_lower)
            except Exception:
                pass

            if ("benign" not in labels_lower) and ("malignant" not in labels_lower) and (os.environ.get("ALLOW_LABEL_MISMATCH") != "1"):
                print("O modelo carregado não parece conter labels 'benign'/'malignant'. Aborting para evitar inferências enganosas.")
                print("Para forçar execução, defina ALLOW_LABEL_MISMATCH=1 no ambiente.")
                return
    except Exception as e_preview:
        print(f"Aviso ao executar verificação de labels: {e_preview}")

    # 1. Carrega os metadados (ajuste o caminho se o CSV estiver em outro lugar)
    df_metadados = carregar_metadados()
    
    if df_metadados is None:
        print("Pipeline abortado: Falha na ingestão dos metadados.")
        return

    mlflow.set_experiment("classificacao_cancer_pele")
    
    # --- CORREÇÃO DO MLFLOW AQUI ---
    # Verifica se há alguma run fantasma ativa e a encerra forçadamente
    if mlflow.active_run() is not None:
        mlflow.end_run()
    # -------------------------------
    
    with mlflow.start_run():
        mlflow.log_param("modelo", modelo_usado if modelo_usado else "desconhecido")
        mlflow.log_param("possui_guardrails", True)
        
        acertos = 0
        total_imagens = 0
        imagens_bloqueadas = 0
        base_dir = "data"
        
        print("\nIniciando inferência com validação de Guardrails...")
        
        for classe_real in ["malignant", "benign"]:
            pasta_atual = os.path.join(base_dir, classe_real)
            
            if not os.path.exists(pasta_atual):
                continue
                
            for nome_arquivo in os.listdir(pasta_atual):
                if nome_arquivo.lower().endswith((".jpg", ".jpeg", ".png")):
                    # 2. Executa o Guardrail antes de gastar processamento com o modelo
                    permitido, mensagem = validar_guardrail(nome_arquivo, df_metadados)
                    
                    if not permitido:
                        print(f"[\033[91m X \033[0m] {nome_arquivo} -> {mensagem}")
                        imagens_bloqueadas += 1
                        continue # Pula para a próxima imagem
                    
                    caminho_imagem = os.path.join(pasta_atual, nome_arquivo)
                    total_imagens += 1
                    
                    resultado = classificador(caminho_imagem)
                    classe_predita = resultado[0]['label'].lower()
                    
                    # Mapeamento de semântica: O modelo retorna a doença exata
                    termos_malignos = ["melanoma", "carcinoma", "malignant"]
                    
                    if classe_real == "malignant":
                        acertou = any(termo in classe_predita for termo in termos_malignos)
                    else:
                        # Se a imagem é benigna, acertou se não previu nada maligno
                        acertou = not any(termo in classe_predita for termo in termos_malignos)
                        
                    # Feedback visual de acerto (Verde) ou erro (Vermelho)
                    if acertou:
                        acertos += 1
                        status = "\033[92m ACERTO \033[0m" 
                    else:
                        status = "\033[91m ERRO \033[0m"
                        
                    print(f"[{status}] Real: {classe_real.upper():<10} | Predição: {classe_predita.upper():<10} -> {nome_arquivo}")
        
        # 3. Salva métricas de negócio e de sistema no MLflow
        if total_imagens > 0:
            acuracia = acertos / total_imagens
            mlflow.log_metric("acuracia", acuracia)
            mlflow.log_metric("imagens_processadas", total_imagens)
            mlflow.log_metric("imagens_bloqueadas_guardrail", imagens_bloqueadas)
            
            print(f"\n=== Resumo do Experimento ===")
            print(f"Processadas: {total_imagens} | Bloqueadas: {imagens_bloqueadas} | Acurácia: {acuracia * 100:.2f}%")
        else:
            print("\nNenhuma imagem processada.")

if __name__ == "__main__":
    avaliar_modelo()