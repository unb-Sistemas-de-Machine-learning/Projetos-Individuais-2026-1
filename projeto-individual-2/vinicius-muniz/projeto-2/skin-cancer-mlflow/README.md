# Skin Cancer Detection — ML Systems com MLflow

Sistema end-to-end de classificação de lesões de pele (benigna/maligna) usando
modelo pré-treinado do HuggingFace (`Anwarkh1/Skin_Cancer-Image_Classification`)
com foco em engenharia de ML: pipeline modular, versionamento, registro no
MLflow, deploy via FastAPI/CLI, guardrails e observabilidade.

## Estrutura

```
skin-cancer-mlflow/
├── configs/config.yaml        # parâmetros do pipeline e guardrails
├── data/
│   ├── raw/                   # imagens ISIC organizadas por pasta (label)
│   └── processed/             # index.csv, splits, métricas
├── models/pretrained/         # snapshot local do modelo HF
├── mlruns/                    # tracking + registry MLflow
├── src/
│   ├── config.py              # loader YAML
│   ├── data_ingestion.py      # índice + qualidade
│   ├── preprocessing.py       # splits estratificados
│   ├── guardrails.py          # L* pele + confiança mínima + validação
│   ├── model.py               # pyfunc wrapper com guardrails embutidos
│   ├── evaluate.py            # métricas + MLflow logging
│   ├── register.py            # Model Registry
│   ├── serve.py               # FastAPI
│   ├── predict_cli.py         # CLI (humano/JSON)
│   └── pipeline.py            # orquestrador
└── tests/test_guardrails.py
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Dados (ISIC)

Baixe imagens da [ISIC Gallery](https://gallery.isic-archive.com/) e coloque
em `data/raw/<label>/` onde `<label>` é `benign` ou `malignant`:

```
data/raw/
├── benign/ISIC_0000001.jpg
└── malignant/ISIC_0000042.jpg
```

Sugestão: ~300 imagens por classe para avaliação significativa.

## Pipeline

```bash
mlflow ui --backend-store-uri ./mlruns &   # UI em :5000
python -m src.pipeline --stage all
```

Estágios individuais: `ingest | preprocess | download_model | register | evaluate`.

## Inferência

### CLI (saída humana)

```bash
python -m src.predict_cli /caminho/para/imagem.jpg
# Lesão classificada como BENIGNA.
# Confiança: 95.9%.
# ...disclaimer
```

Saída JSON detalhada:

```bash
python -m src.predict_cli /caminho/para/imagem.jpg --json
```

### API (FastAPI)

```bash
python -m src.serve
curl -F "file=@imagem.jpg" http://localhost:8000/predict
```

### MLflow serve (direto do Registry)

```bash
mlflow models serve -m "models:/skin-cancer-classifier/latest" -p 5001 --no-conda
```

## Guardrails

- **Confiança mínima** (`min_confidence=0.70`): abaixo retorna `uncertain`.
- **Tom de pele (L\* ≥ 55)**: rejeita imagens que não sejam de pele clara.
  Dataset ISIC é enviesado para Fitzpatrick I–III; modelo não é válido fora
  desse escopo. Usa L* (CIE Lab) da borda em vez de ITA clássico porque a
  iluminação polarizada da dermatoscopia satura o canal b*.
- **Validação de entrada**: tamanho ≤ 10 MB, formatos permitidos, integridade.
- **Disclaimer médico** em toda resposta.

## Observabilidade

- Runs MLflow com params/metrics/artifacts (predições por imagem, matriz de
  confusão, `metrics.json`).
- Logs estruturados no serviço (`/predict` registra decisão por request).
- Métricas operacionais: `coverage`, `n_rejected_guardrail`, `n_uncertain`.
- UI comparativa: `mlflow ui --backend-store-uri ./mlruns` → http://localhost:5000

## Testes

```bash
pytest tests/
```
