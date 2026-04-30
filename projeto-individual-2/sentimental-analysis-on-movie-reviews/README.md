# Análise sentimental de resenhas de filmes

Sistema de ML end-to-end para classificação binária de sentimento (positivo/negativo) em resenhas de filmes, com rastreamento de experimentos, versionamento de modelo e deploy via MLflow.

- **Modelo:** [`distilbert-base-uncased-finetuned-sst-2-english`](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) (HuggingFace, sem fine-tuning)
- **Dataset:** [Stanford Large Movie Review Dataset (aclImdb)](https://ai.stanford.edu/~amaas/data/sentiment/) -- 25.000 resenhas de teste, balanceado
- **Rastreamento:** MLflow (8 experimentos, 1 modelo registrado)
- **Deploy:** Docker Compose (PostgreSQL + MLflow server + pipeline + API FastAPI)

## Estrutura do projeto

```
sentimental-analysis-on-movie-reviews/
├── src/
│   ├── pipeline.py          # orquestrador do pipeline (ponto de entrada)
│   ├── tracking.py          # wrapper MLflow (unico modulo que importa mlflow)
│   ├── api.py               # API FastAPI com guardrails
│   ├── guardrails.py        # validacoes de entrada isoladas
│   ├── data/
│   │   ├── ingest.py        # carrega aclImdb do disco
│   │   └── preprocess.py    # limpa HTML e normaliza whitespace
│   └── model/
│       ├── loader.py        # constroi o pipeline DistilBERT
│       └── evaluate.py      # inferencia e metricas
├── data/raw/aclImdb/        # dataset (nao versionado no git)
├── mlruns/                  # MLflow tracking store (versionado)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── EXPERIMENTS.md            # plano experimental detalhado
└── relatorio-entrega.md      # relatorio tecnico de entrega
```

## Como executar

### Pre-requisitos

- Python 3.10+ com virtualenv
- Docker e Docker Compose (para execucao containerizada)
- Dataset aclImdb em `data/raw/aclImdb/`

### Pipeline local (sem Docker)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Executar o pipeline sem rastreamento
python -m src.pipeline --data-dir data/raw/aclImdb --sample-size 200

# Executar com rastreamento MLflow
python -m src.pipeline --data-dir data/raw/aclImdb --sample-size 200 --track

# Executar com rastreamento e registro do modelo
python -m src.pipeline --data-dir data/raw/aclImdb --sample-size 200 --track --register-model

# Iniciar o MLflow UI
mlflow ui --backend-store-uri mlruns/
```

### Pipeline via Docker Compose

```bash
# Subir todos os servicos (banco, MLflow, pipeline e API)
docker compose up --build

# Ou subir servicos individualmente:
docker compose up -d --build mlflow          # MLflow + PostgreSQL
docker compose run --build pipeline          # executar pipeline
docker compose up --build api                # API de inferencia
```

## Experimentos

Oito experimentos foram executados cobrindo tres dimensoes de variacao. O plano completo esta em [`EXPERIMENTS.md`](./EXPERIMENTS.md).

| Exp | Dimensao | sample_size | max_length | seed | accuracy |
|-----|----------|-------------|------------|------|----------|
| 01 | Estabilidade | 100 | 512 | 42 | 0.890 |
| 02 | Estabilidade | 250 | 512 | 42 | 0.904 |
| 03 | Estabilidade | 500 | 512 | 42 | 0.914 |
| 04 | Estabilidade (registrado) | 1000 | 512 | 42 | 0.900 |
| 05 | Truncamento | 500 | 128 | 42 | 0.854 |
| 06 | Truncamento | 500 | 256 | 42 | 0.886 |
| 07 | Variancia | 500 | 512 | 43 | 0.914 |
| 08 | Variancia | 500 | 512 | 44 | 0.914 |

## API de inferencia

A API FastAPI (`src/api.py`) consome o modelo registrado no MLflow Model Registry e aplica guardrails antes da inferencia.

### Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `GET` | `/health` | Health check e status do modelo |
| `POST` | `/predict` | Classificacao de sentimento com guardrails |

### Guardrails implementados

| Guardrail | Codigo | HTTP |
|-----------|--------|------|
| Resenha vazia | `empty_review` | 422 |
| Resenha curta (< 5 palavras) | `review_too_short` | 422 |
| Idioma nao ingles | `non_english_review` | 422 |
| Excede 512 tokens | `review_too_long` | 422 |

A analise completa de guardrails, incluindo avaliacao de thresholds de confianca, esta em [`GUARDRAILS.md`](./GUARDRAILS.md).

### Exemplos de uso

Predicao valida:

```powershell
curl.exe -i -X POST "http://127.0.0.1:8000/predict" `
  -H "Content-Type: application/json" `
  --data-raw '{"text":"This movie had excellent acting, a strong script, and a beautiful ending that made the story memorable."}'
```

Guardrail de idioma (rejeita com 422):

```powershell
curl.exe -i -X POST "http://127.0.0.1:8000/predict" `
  -H "Content-Type: application/json" `
  --data-raw '{"text":"Este filme tem atuacoes excelentes e uma historia muito emocionante do comeco ao fim."}'
```

### Variaveis de ambiente

| Variavel | Padrao | Descricao |
|----------|--------|-----------|
| `MLFLOW_TRACKING_URI` | `mlruns/` | URI do servidor MLflow |
| `SENTIMENT_MODEL_URI` | `models:/sentiment-imdb/1` | URI do modelo registrado |
| `SENTIMENT_TOKENIZER_LOCAL_ONLY` | `1` | Usar tokenizer apenas do cache local |

## Documentacao

- [`EXPERIMENTS.md`](./EXPERIMENTS.md) -- plano experimental com justificativas
- [`GUARDRAILS.md`](./GUARDRAILS.md) -- analise de guardrails e thresholds
- [`relatorio-entrega.md`](./relatorio-entrega.md) -- relatorio tecnico de entrega
