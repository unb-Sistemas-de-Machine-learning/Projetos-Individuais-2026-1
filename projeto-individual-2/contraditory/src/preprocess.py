import pandas as pd
import mlflow
import os
import dagshub


def preprocess_data():
    dagshub.init(repo_owner='Ana-Luiza-SC', repo_name='contraditory', mlflow=True)
    mlflow.set_tracking_uri("https://dagshub.com/Ana-Luiza-SC/contraditory.mlflow")
    mlflow.set_experiment("contraditory")

    df = pd.read_csv("data/train.csv")
    df = df[df["language"] == "English"].copy()

    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/train_en.csv"
    df.to_csv(output_path, index=False)

    with mlflow.start_run(run_name="Preprocessing_English_CrossEncoder"):
        mlflow.log_param("language_scope", "English only")
        mlflow.log_param("num_rows_after_filter", len(df))
        mlflow.log_artifact(output_path)

        print(f"Base filtrada salva em: {output_path}")
        print(f"Total de linhas após filtro: {len(df)}")


if __name__ == "__main__":
    preprocess_data()