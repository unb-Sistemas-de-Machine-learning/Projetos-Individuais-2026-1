# src/common/drift_detector.py

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
import logging

def detect_drift(train_data: pd.DataFrame, current_data: pd.DataFrame, threshold=0.05):
    """
    Detecta desvio de dados (Data Drift) usando o teste de Kolmogorov-Smirnov.
    Retorna True se o drift for detectado (p-value < threshold).
    """
    logging.info("Iniciando análise de Data Drift...")
    drift_detected = False
    
    # Compara colunas numéricas comuns
    common_cols = train_data.select_dtypes(include=[np.number]).columns.intersection(
        current_data.select_dtypes(include=[np.number]).columns
    )
    
    for col in common_cols:
        stat, p_value = ks_2samp(train_data[col], current_data[col])
        if p_value < threshold:
            logging.warning(f"Data Drift detectado na feature '{col}' (p-value: {p_value:.4f})")
            drift_detected = True
            
    if not drift_detected:
        logging.info("Nenhum Data Drift significativo detectado.")
        
    return drift_detected
