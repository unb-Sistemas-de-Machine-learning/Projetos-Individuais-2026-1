import numpy as np
import pandas as pd
import tensorflow as tf
import mlflow.tensorflow
from tensorflow.keras import layers, models, regularizers
import mlflow
import dagshub
import os

def train_model():
    # 1. Configuração do DagsHub e MLflow
    dagshub.init(repo_owner='Ana-Luiza-SC', repo_name='contraditory', mlflow=True)
    mlflow.set_tracking_uri("https://dagshub.com/Ana-Luiza-SC/contraditory.mlflow")
    mlflow.set_experiment("contraditory")

    # carrega os embeddings
    print("carrega os embeddings")
    p_emb = np.load("data/processed/p_emb.npy")
    h_emb = np.load("data/processed/h_emb.npy")
    train_df = pd.read_csv("data/train.csv")
    y = train_df['label'].values

    # combinação de vetores
    diff = np.abs(p_emb - h_emb)
    prod = p_emb * h_emb
    X = np.concatenate([p_emb, h_emb, diff, prod], axis=1)
    
    # ativa autolog
    mlflow.tensorflow.autolog()

    with mlflow.start_run(run_name="Neural_Network_Simple_2"):
        # define uma arquitetura mais simplificada
        model = models.Sequential([
            # primeira camada com regularização
            layers.Dense(128, activation='relu', input_shape=(X.shape[1],),
                         kernel_regularizer=regularizers.l2(0.01)),
            layers.Dropout(0.5),
            
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(3, activation='softmax') # Saída para 3 classes
        ])

        # compilação com learning rate
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        # configura early stopping
        early_stop = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=4,           
            restore_best_weights=True 
        )

        # 8. Treinamento
        print("Iniciando treino com diminuição da complexidade")
        history = model.fit(
            X, y, 
            epochs=50, 
            batch_size=64, 
            validation_split=0.2, 
            callbacks=[early_stop]
        )

        final_acc = history.history['val_accuracy'][np.argmin(history.history['val_loss'])]
        print(f"Treino finalizado com acurácia de: {final_acc:.4f}")

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    train_model()