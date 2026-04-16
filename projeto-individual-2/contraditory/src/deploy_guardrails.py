import mlflow
import dagshub
from model_wrapper import ContraditoryGuardrailWrapper

# Configuração DagsHub
dagshub.init(repo_owner='Ana-Luiza-SC', repo_name='contraditory', mlflow=True)

# URI do modelo que você já subiu (o checkpoint)
# Substitua pelo seu Run ID anterior
run_id = "57cd950a2ad84a569b61adbeb474cf1a"
logged_model_path = f"runs:/{run_id}/model_files/checkpoint-2748"

# Artefatos necessários para o Wrapper
artifacts = {
    "model_path": logged_model_path
}

with mlflow.start_run(run_name="Deploy_With_Guardrails"):
    mlflow.pyfunc.log_model(
        artifact_path="guardrail_model",
        python_model=ContraditoryGuardrailWrapper(),
        artifacts=artifacts,
        registered_model_name="contraditory-crossencoder-final",
        pip_requirements=["sentence-transformers", "langdetect", "pandas"]
    )
    print("Modelo com Guardrails registrado com sucesso!")