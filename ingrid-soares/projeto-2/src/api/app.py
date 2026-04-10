from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
import numpy as np
import time
import logging
from src.ids.inference import load_ids_model, predict_traffic
from src.phishing.inference import load_model_and_tokenizer, predict_url
from src.common.drift_detector import detect_drift

# Configurar logging para monitoramento
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ML-Security-API")

app = FastAPI(title="ML Security API")

# --- Carregamento dos modelos e baseline para detecção de drift ---
print("Carregando modelos e baseline para API...")
ids_model = load_ids_model()
phishing_tokenizer, phishing_model = load_model_and_tokenizer()

# Carrega baseline de treino (IDS) para comparação de drift
TRAIN_IDS_DATA = pd.read_parquet("data/ids/cleaned_ids_data.parquet")

class PhishingRequest(BaseModel):
    url: str

@app.middleware("http")
async def log_latency(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Endpoint: {request.url.path} | Latência: {process_time:.4f}s")
    return response

@app.get("/")
def read_root():
    return {"message": "Security ML API is online"}

@app.post("/predict/phishing")
async def predict_phishing(request: PhishingRequest):
    result = predict_url(request.url, phishing_tokenizer, phishing_model)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/predict/ids")
async def predict_ids(data: dict):
    # Recebe dados JSON, converte para DataFrame e faz inferência
    try:
        df = pd.DataFrame([data])
        
        # Verifica Drift antes da inferência
        if detect_drift(TRAIN_IDS_DATA, df):
            logger.critical("ALERTA: Data Drift detectado nos dados de inferência!")
            # Opcional: Adicionar lógica para notificação aqui
            
        results = predict_traffic(df, ids_model)
        return results.to_dict(orient="records")[0]
    except Exception as e:
        logger.error(f"Erro na inferência IDS: {e}")
        raise HTTPException(status_code=400, detail=str(e))
