| Nome | Matrícula |
|------|-----------|
| Hian Praxedes de Souza Oliveira | 200019520 |
| Silas Neres | 200043536 |

# Phishing Email MLflow

Sistema end-to-end de detecção de phishing em e-mails com foco em **ML Systems**, utilizando **MLflow** para rastreamento de experimentos, registro do modelo e deploy local para inferência.

## Objetivo

O projeto implementa uma pipeline completa para classificação de e-mails em duas classes:
- **phishing**
- **legitimate**

O foco principal não está em treinar um modelo do zero, mas em estruturar um sistema reprodutível com:
- ingestão e preparação de dados
- avaliação
- tracking com MLflow
- model registry
- serving local
- guardrails básicos

## Dataset

- **Nome:** `zefang-liu/phishing-email-dataset`
- **Fonte:** Hugging Face Datasets
- **Tipo:** classificação de texto
- **Tamanho carregado:** 18.650 exemplos

O dataset é carregado programaticamente com a biblioteca `datasets`.

## Modelo pré-treinado

- **Nome:** `ElSlay/BERT-Phishing-Email-Model`
- **Fonte:** Hugging Face
- **Tipo:** classificação de texto com BERT
- **Fine-tuning no projeto:** não

## Estrutura do projeto

```text
projeto-2/
├── configs/
├── data/
│   ├── raw/
│   └── processed/
├── evidence/
├── reports/
├── scripts/
│   ├── run_pipeline.py
│   ├── register_model.py
│   └── run_inference.py
├── src/
│   ├── data/
│   │   ├── download.py
│   │   ├── validate.py
│   │   ├── normalize.py
│   │   └── split.py
│   ├── model/
│   │   ├── load_model.py
│   │   └── predict.py
│   ├── evaluation/
│   │   └── evaluate.py
│   ├── serving/
│   │   └── guardrails.py
│   └── tracking/
├── tests/
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.13
- PowerShell (Windows) ou terminal equivalente
- acesso à internet para baixar o dataset e o modelo na primeira execução

## Instalação

### 1. Criar o ambiente virtual

```powershell
python -m venv .venv
```

### 2. Ativar o ambiente virtual

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

## Pipeline completo

### 1. Baixar o dataset

```powershell
python src/data/download.py
```

### 2. Validar os dados

```powershell
python src/data/validate.py
```

### 3. Normalizar o dataset

```powershell
python src/data/normalize.py
```

### 4. Criar os splits

```powershell
python src/data/split.py
```

Isso deve gerar:
- `data/processed/normalized.csv`
- `data/processed/train.csv`
- `data/processed/val.csv`
- `data/processed/test.csv`

## Subindo o MLflow

Em um terminal separado:

```powershell
python -m mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

A interface ficará disponível em:

```text
http://127.0.0.1:5000
```

## Executando o pipeline principal

Com o MLflow server rodando, execute:

```powershell
python -m scripts.run_pipeline
```

Esse comando:
- carrega o conjunto de teste
- aplica os guardrails
- executa inferência em lote
- calcula métricas
- registra parâmetros, métricas e artefatos no MLflow

### Arquivos gerados

Na pasta `reports/`, são gerados:
- `test_predictions.csv`
- `monitoring_summary.json`
- `classification_report.json`
- `error_examples.csv`
- `confusion_matrix.png`

## Guardrails implementados

O sistema possui regras básicas para reduzir uso indevido:
- rejeição de texto vazio
- rejeição de texto muito curto
- rejeição de texto muito longo
- abstenção em casos de baixa confiança

Os status possíveis são:
- `accepted`
- `rejected`
- `abstain`

## Registro do modelo

Para logar e registrar o modelo no MLflow Model Registry:

```powershell
python -m scripts.register_model
```

O modelo é registrado com o nome:

```text
phishing-email-detector
```

## Inferência a partir do modelo registrado

### Script local

```powershell
python -m scripts.run_inference
```

## Deploy local com MLflow Serving

No Windows, o serving foi executado com o ambiente local.

### 1. Ativar a venv

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Configurar variáveis de ambiente

```powershell
$env:MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
$env:MLFLOW_REGISTRY_URI="http://127.0.0.1:5000"
```

### 3. Servir o modelo registrado

```powershell
python -m mlflow models serve -m models:/phishing-email-detector/1 -p 5001 --env-manager local
```

### 4. Verificar saúde do serviço

```text
http://127.0.0.1:5001/health
```

## Testando o endpoint de inferência

### Exemplo legítimo

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5001/invocations" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"dataframe_records":[{"text":"Hello team, please find attached the updated meeting notes for tomorrow."}]}'
```

### Exemplo de phishing

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5001/invocations" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"dataframe_records":[{"text":"Dear user, your account has been suspended. Click here immediately to verify your credentials and avoid permanent closure."}]}'
```

Nos testes realizados:
- o exemplo legítimo retornou `LABEL_0`
- o exemplo de phishing retornou `LABEL_1`

## Resultados obtidos na execução principal

Na execução registrada do pipeline:
- `total_rows = 2631`
- `accepted_count = 2370`
- `rejected_count = 251`
- `abstain_count = 10`
- `accuracy = 0.9945`
- `precision = 0.9858`
- `recall = 1.0000`
- `f1 = 0.9928`
- `avg_latency_ms = 534.82`

## Evidências

A pasta `evidence/` deve conter prints de:
- MLflow UI com as runs
- detalhes da run
- artifacts da run
- Registered Models com `phishing-email-detector`
- terminal do `run_pipeline.py`
- terminal do `register_model.py`
- `/health`
- inferência do caso legítimo
- inferência do caso phishing
- testes passando

## Testes

Para executar os testes automatizados presentes no projeto:

```powershell
python -m pytest -q
```

## Limitações

- o foco do projeto está na engenharia do sistema e não em validação externa ampla do modelo;
- os guardrails implementados são básicos;
- a interpretação do classificador deve ser usada como apoio automatizado, não como decisão única;
- a compatibilidade de serving local em Windows exigiu configuração adicional de ambiente.

## Tecnologias utilizadas

- Python
- Hugging Face Transformers
- Hugging Face Datasets
- PyTorch
- MLflow
- pandas
- scikit-learn
- matplotlib
- pytest

