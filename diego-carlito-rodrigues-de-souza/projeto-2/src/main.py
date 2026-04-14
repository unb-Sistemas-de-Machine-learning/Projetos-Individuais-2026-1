import os
import mlflow
import time
import pandas as pd
import logging
from ingest import load_and_clean_data
from model_engine import TicketClassifier
from guardrails import mask_pii, apply_confidence_guardrail
from evaluation import evaluate_performance

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline(data_path: str, sample_size: int = 10, confidence_threshold: float = 0.65) -> None:
    """
    Executa o pipeline end-to-end de classificação Zero-Shot com rastreamento MLflow.

    Esta função atua como o orquestrador principal, integrando a ingestão de dados,
    a engine do modelo e os guardrails de segurança, registrando todo o ciclo de vida
    no MLflow para garantir a reprodutibilidade.

    Args:
        data_path (str): Caminho local para o dataset CSV bruto.
        sample_size (int, opcional): Quantidade de linhas para processar (amostragem).
        confidence_threshold (float, opcional): Limite de confiança para acionar a revisão humana.
    """
    # 1. Configurar MLflow Tracking
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Zero-Shot_Ticket_Classification")

    with mlflow.start_run(run_name="BART_Inference_Pipeline"):
        logger.info("Iniciando pipeline de processamento.")
        start_time = time.time()

        try:
            # 2. Ingestão
            df = load_and_clean_data(data_path, sample_size=sample_size)
            
            # Registrar parâmetros de negócio (MLflow)
            mlflow.log_param("dataset_path", data_path)
            mlflow.log_param("sample_size", sample_size)
            mlflow.log_param("confidence_threshold", confidence_threshold)
            mlflow.log_param("model_architecture", "facebook/bart-large-mnli")

            # 3. Inicializar Modelo
            classifier = TicketClassifier()
            
            resultados = []
            guardrail_triggers = 0
            
            # 4. Inferência Linha a Linha (com Guardrails)
            for idx, row in df.iterrows():
                texto_original = row['Ticket Description']
                
                # Guardrail 1: Mascarar PII (Privacidade)
                texto_seguro = mask_pii(texto_original)
                
                # Inferência
                predicao = classifier.classify(texto_seguro)
                
                # Guardrail 2: Confiança (Segurança do Usuário)
                label_final = apply_confidence_guardrail(predicao, threshold=confidence_threshold)
                
                # Contabilizar acionamentos do Guardrail
                if "Revisão Humana" in label_final:
                    guardrail_triggers += 1

                # Salvar resultado
                resultados.append({
                    "texto_seguro": texto_seguro,
                    "label_original": row['Ticket Type'],
                    "label_predita": label_final,
                    "confianca_modelo": predicao['score']
                })
            
            # 5. Salvar resultados localmente
            os.makedirs("logs", exist_ok=True)
            df_results = pd.DataFrame(resultados)
            output_file = "logs/output_results.csv"
            df_results.to_csv(output_file, index=False)
            logger.info(f"Resultados salvos em {output_file}")

            # 5.1 Marcos: Avaliar performance real
            metricas_finais = evaluate_performance(output_file)

            # 6. Registrar Métricas, Artefatos e Assinatura no MLflow
            end_time = time.time()
            total_time = end_time - start_time
            avg_confidence = df_results['confianca_modelo'].mean()

            mlflow.log_metric("accuracy", metricas_finais["accuracy"])
            mlflow.log_metric("automation_rate", metricas_finais["automation_rate"])

            mlflow.log_metric("total_latency_seconds", total_time)
            mlflow.log_metric("avg_confidence", avg_confidence)
            mlflow.log_metric("human_review_triggers", guardrail_triggers)
            
            # Registrar as colunas usadas como um schema simples
            mlflow.set_tag("features_schema", "Ticket Description, Ticket Type")
            
            # Versão dos dados gerados (Reprodutibilidade)
            mlflow.log_artifact(output_file, artifact_path="processed_data")

            logger.info("Pipeline concluído e registrado no MLflow com sucesso.")

        except Exception as e:
            logger.error(f"Erro fatal no pipeline: {str(e)}")
            # Registrar erro como "Run Failed" no MLflow
            mlflow.set_tag("status", "failed")
            raise

if __name__ == "__main__":
    run_pipeline("data/customer_support_tickets.csv", sample_size=10, confidence_threshold=0.65)
