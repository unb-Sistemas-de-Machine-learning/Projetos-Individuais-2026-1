# YouTube Spam MLflow Pipeline

Projeto de ML Systems para classificacao de spam em comentarios do YouTube usando:

- Dataset YouTube Spam Collection (https://archive.ics.uci.edu/dataset/380/youtube+spam+collection)
- Modelo pre-treinado do Hugging Face: `mrm8488/bert-tiny-finetuned-sms-spam-detection`
- Fine-tuning no domínio dos comentários do YouTube
- MLflow para tracking, registro e observabilidade
- FastAPI para deploy de inferencia
- Guardrails


## 1. Ambiente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Pipeline

Adapta o modelo pré-treinado (SMS) ao dataset de comentários do YouTube, avalia no conjunto de teste temporal e registra no MLflow.

```bash
python scripts/finetune.py
```


## 3. Abrir UI do MLflow

```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

Acesse `http://127.0.0.1:5000`.

## 4. API de inferencia

Em um terminal:

```bash
python scripts/serve.py
```

API sobe em `http://127.0.0.1:8000`.


### Testar a API

**Prever spam (unitário):**
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"content":"Check out my channel and subscribe"}'
```

Resposta:
```json
{
  "allowed":false,
  "guardrail_reason":"Call-to-action excessivo detectado","prediction":"rejected",
  "spam_probability":0.0
}
```

# Relatório de entrega
Veja o relatório de entrega [aqui](docs/relatorio-entrega.md)