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

        # armazenar quantos idiomas diferentes ele abrange
        with mlflow.start_run(run_name = "Data Ingestion"):

            # organizar a observabilidade
            mlflow.log_param("num_train_sample", len(df_train))
            mlflow.log_dict(df_train['language'].value_counts().to_dict(), "language_distribution.json")
            print(f"As colunas são: {df_train.columns.tolist()}")
            print("A ingestão foi registrada no mlflow")

            print("")
            # só para visualizar e armazenar a quantidade de idiomas
            total_idiomas = df_train['language'].nunique()
            mlflow.log_param("total_languages", total_idiomas)
            print(f"Os dados abrangem o total de {total_idiomas} idiomas")
    else:
        print("caminho não encontrado!")

if __name__ == "__main__":
    load_and_log_data()