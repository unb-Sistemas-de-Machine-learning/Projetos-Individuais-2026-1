import pandas
import os
import mlflow
import dagshub


def load_and_log_data():

    # configuração do projeto no dagshub usando mlflow
    dagshub.init(repo_owner='Ana-Luiza-SC', repo_name='contraditory', mlflow=True)    
    mlflow.set_tracking_uri("https://dagshub.com/Ana-Luiza-SC/contraditory.mlflow")
    mlflow.set_experiment("contraditory")
    
    train_path = "data/train.csv"

    if os.path.exists(train_path):
        # lê a tabela de dados para treinar
        df_train = pandas.read_csv(train_path)
        
        # recorte para inglês
        df_en = df_train[df_train["language"] == "English"].copy()

        # armazenar quantos idiomas diferentes ele abrange
        with mlflow.start_run(run_name = "Data_Ingestion_English_2"):

            # organizar a observabilidade
            mlflow.log_param("num_train_samples_total", len(df_train))
            mlflow.log_param("total_languages", df_train["language"].nunique())
            mlflow.log_dict(
                df_train["language"].value_counts().to_dict(),
                "language_distribution.json"
            )
            
            # observabilidade para o novo escopo gerado
            mlflow.log_param("language_scope", "English only")
            mlflow.log_param("num_train_samples_english", len(df_en))
            mlflow.log_metric("english_ratio", len(df_en) / len(df_train))

            # distribuição de classes no recorte final
            mlflow.log_dict(
                df_en["label"].value_counts().to_dict(),
                "english_label_distribution.json"
            )
            
            print(f"As colunas são: {df_train.columns.tolist()}")
            print("A ingestão foi registrada no mlflow")

            print("")
            print(f"Total de amostras em inglês: {len(df_en)}")
    else:
        print("caminho não encontrado!")

if __name__ == "__main__":
    load_and_log_data()