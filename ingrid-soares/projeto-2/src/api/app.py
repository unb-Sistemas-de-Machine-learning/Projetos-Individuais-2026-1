# src/api/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from src.ids.inference import load_ids_model, predict_traffic
from src.phishing.inference import load_model_and_tokenizer, predict_url

app = FastAPI(title="ML Security API")

# --- Carregamento dos modelos em memória ---
print("Carregando modelos para API...")
ids_model = load_ids_model()
phishing_tokenizer, phishing_model = load_model_and_tokenizer()

class PhishingRequest(BaseModel):
    url: str

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
        results = predict_traffic(df, ids_model)
        return results.to_dict(orient="records")[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
