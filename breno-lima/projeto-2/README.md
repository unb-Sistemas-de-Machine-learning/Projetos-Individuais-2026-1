# Projeto 2 — Sistema de ML com MLflow

**Aluno:** Breno Queiroz Lima | **Matrícula:** 211063069

Sistema de machine learning end-to-end para **classificação de câncer de pele**, com foco em engenharia de ML Systems usando MLflow.

---

## Problema

Classificação automática de imagens dermatoscópicas (ISIC Archive) utilizando o modelo pré-treinado [`gianlab/swin-tiny-patch4-window7-224-finetuned-skin-cancer`](https://huggingface.co/gianlab/swin-tiny-patch4-window7-224-finetuned-skin-cancer) (Swin Transformer, Hugging Face).

---

## Estrutura

```
projeto-2/
├── src/
│   ├── data/
│   │   ├── ingestion.py       # ISICClient: download via API
│   │   └── dataset.py         # SkinCancerDataset: particionamento 70/15/15
│   ├── model/
│   │   └── model_service.py   # ModelService: inferência + guardrails
│   └── pipeline/
│       └── run_experiment.py  # Orquestração + integração MLflow
├── data/raw/                  # Imagens baixadas do ISIC Archive
├── mlflow.db                  # Tracking SQLite
├── mlruns/                    # Artefatos MLflow
├── requirements.txt
└── relatorio-entrega.md
```

---

## Como executar

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar o pipeline (ingestão + avaliação + registro no MLflow)
python src/pipeline/run_experiment.py

# 4. Visualizar experimentos
mlflow ui --backend-store-uri sqlite:///mlflow.db
# Acesse http://localhost:5000

# 5. Servir o modelo para inferência
mlflow models serve \
  --model-uri "models:/SkinCancerClassifier/latest" \
  --port 5001 \
  --no-conda
```

---

## Pipeline

```
Ingestão (ISIC API)
    ↓ Validação e Download
    ↓ Particionamento 70/15/15
    ↓ Carregamento do modelo (Hugging Face)
    ↓ Pré-processamento (AutoImageProcessor)
    ↓ Inferência no split de teste
    ↓ Guardrails (confiança < 0.6 → warning)
    ↓ Registro no MLflow (params, métricas, artefatos, Model Registry)
    ↓ Deploy via mlflow models serve
```

---

## MLflow

| O que é rastreado | Detalhe |
|---|---|
| Parâmetros | `model_name`, `dataset_size`, `train/val/test_size` |
| Métricas | `avg_confidence`, `min/max_confidence`, `warnings_count`, `confidence_per_image` (por step) |
| Artefatos | `sample_predictions.json`, modelo PyTorch |
| Model Registry | `SkinCancerClassifier` — nova versão a cada execução |

---

## Guardrails

- Predições com `confidence < 0.6` geram aviso explícito no campo `warnings`
- Imagens corrompidas/inválidas são rejeitadas na ingestão
- ⚠️ Este sistema **não substitui diagnóstico médico**

---

## Relatório

Ver [`relatorio-entrega.md`](./relatorio-entrega.md) para detalhes de decisões de projeto, observabilidade, limitações e referências.
