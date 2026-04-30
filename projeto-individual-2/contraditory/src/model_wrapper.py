import mlflow.pyfunc
import numpy as np
import pandas as pd
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class ContraditoryGuardrailWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        from sentence_transformers import CrossEncoder
        # Carrega o modelo dos artefatos
        self.model = CrossEncoder(context.artifacts["model_path"])

    def predict(self, context, model_input):
        # Garante que o input seja tratado como string, seja DataFrame ou Lista
        if isinstance(model_input, pd.DataFrame):
            text1 = str(model_input.iloc[0, 0])
            text2 = str(model_input.iloc[0, 1])
        else:
            text1 = str(model_input[0][0])
            text2 = str(model_input[0][1])

        # Guardrail de Idioma
        try:
            if detect(text1) != 'en' or detect(text2) != 'en':
                return {"prediction": "REJECTED", "reason": "Only English supported."}
        except:
            return {"error": "Language detection failed."}

        # Predição
        raw_score = self.model.predict([(text1, text2)])
        
        # O CONSERTO ESTÁ AQUI: Forçamos a conversão para um float puro
        # Pegamos o primeiro elemento do array e transformamos em número
        score = float(np.array(raw_score).flatten()[0])

        # Guardrail de Confiança
        status = "high_confidence" if score > 0.5 else "low_confidence"

        return {
            "score": score, 
            "status": status,
            "decision": "contradiction" if score > 0.5 else "neutral/entailment"
        }