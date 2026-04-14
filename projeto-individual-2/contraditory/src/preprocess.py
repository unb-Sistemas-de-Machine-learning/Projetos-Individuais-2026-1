import tensorflow_hub as hub
import tensorflow_text
import pandas as pd
import mlflow
import os
import numpy as np

def preprocess_in_batches():
    
    mlflow.set_tracking_uri(f"sqlite:///{os.path.abspath(os.getcwd())}/mlflow.db")
    mlflow.set_experiment("contraditory")

    df = pd.read_csv("data/train.csv")
    model_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
    
    # configura o batch para processar 512 palavras por vez
    batch_size = 512 
    
    with mlflow.start_run(run_name="Preprocessing_Batched"):
        print("✓ Carregando modelo do TF Hub...")
        model = hub.load(model_url)
        
        all_p_embeddings = []
        all_h_embeddings = []

        print(f"✓ Processando {len(df)} linhas em lotes de {batch_size}...")
        
        # processa em pedaços
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            
            # Gera embeddings para o lote atual
            p_batch = model(batch_df['premise'].tolist())
            h_batch = model(batch_df['hypothesis'].tolist())
            
            all_p_embeddings.append(p_batch.numpy())
            all_h_embeddings.append(h_batch.numpy())
            
            print(f"Progresso: {i}/{len(df)} frases processadas")

        # junta tudo no final
        p_emb_final = np.vstack(all_p_embeddings)
        h_emb_final = np.vstack(all_h_embeddings)
        
        # salva os arquivos
        os.makedirs("data/processed", exist_ok=True)
        np.save("data/processed/p_emb.npy", p_emb_final)
        np.save("data/processed/h_emb.npy", h_emb_final)
        
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("num_rows", len(df))

        print("O pre processamento deu certo!")

if __name__ == "__main__":
    preprocess_in_batches()