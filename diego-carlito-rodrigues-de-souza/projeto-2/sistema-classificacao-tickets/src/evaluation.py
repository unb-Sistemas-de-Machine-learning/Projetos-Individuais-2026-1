import pandas as pd
from sklearn.metrics import accuracy_score
import logging

logger = logging.getLogger(__name__)

def evaluate_performance(csv_path: str) -> dict:
    """
    Lê o log de inferência e calcula as métricas reais do sistema.
    """
    try:
        df = pd.read_csv(csv_path)
        total_tickets = len(df)
        
        if total_tickets == 0:
            return {"accuracy": 0.0, "automation_rate": 0.0}

        # 1. Separar os tickets que foram bloqueados pelo seu Guardrail
        df_automatizado = df[~df['label_predita'].str.contains("Revisão Humana")]
        tickets_automatizados = len(df_automatizado)
        
        # Cálculo da Taxa de Automação (Quantos % o sistema resolveu sozinho)
        automation_rate = tickets_automatizados / total_tickets

        # 2. Cálculo da Acurácia (O modelo acertou os que ele disse ter certeza?)
        if tickets_automatizados > 0:
            # Força o lowercase para evitar que 'Network Problem' e 'network problem' sejam dados como erro
            y_true = df_automatizado['label_original'].str.lower().str.strip()
            y_pred = df_automatizado['label_predita'].str.lower().str.strip()
            
            accuracy = accuracy_score(y_true, y_pred)
        else:
            accuracy = 0.0

        logger.info(f"Avaliação Concluída -> Automação: {automation_rate:.2%} | Acurácia: {accuracy:.2%}")
        
        return {
            "accuracy": accuracy,
            "automation_rate": automation_rate
        }
        
    except Exception as e:
        logger.error(f"Falha no módulo de avaliação: {str(e)}")
        raise