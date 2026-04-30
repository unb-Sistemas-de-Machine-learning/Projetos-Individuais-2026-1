# src/api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import pipeline
from PIL import Image
import io
import uvicorn

# Inicializa a app
app = FastAPI(
    title="API de Deteção de Cancer de Pele",
    description="Endpoint de inferência para o projeto de ML Systems"
)

print("A carregar o modelo na memória... Isto pode demorar alguns segundos.")
try:
    classifier = pipeline("image-classification", model="Anwarkh1/Skin_Cancer-Image_Classification")
    print("Modelo carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    classifier = None

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if classifier is None:
        raise HTTPException(status_code=500, detail="Modelo não disponível no servidor.")

    # Validação básica de extensão
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Formato de ficheiro inválido. Use JPG ou PNG.")

    try:
        # Lê a imagem enviada
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Executa a inferência
        predictions = classifier(image)

        # Formata a resposta para o utilizador
        results = []
        for pred in predictions:
            results.append({
                "label": pred['label'],
                "confidence": round(pred['score'] * 100, 2)
            })

        return {
            "filename": file.filename,
            "predictions": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

if __name__ == "__main__":
    # Inicia o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)