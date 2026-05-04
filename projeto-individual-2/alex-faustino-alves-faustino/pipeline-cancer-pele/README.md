# Pipeline: Detecção e Classificação de Câncer de Pele 

Este diretório contém um pipeline de engenharia de machine learning focado na execução em lote, avaliação e registro de um modelo pré-treinado para classificação de lesões de pele (benigno vs. maligno).

## 1. Visão Geral

Código principal (src/main.py): Executa inferência em lote, aplica as camadas de validação (guardrails) e registra as métricas no MLflow.

API REST (src/api.py): Servidor FastAPI para inferência em tempo real via endpoint /predict.


Dados: Imagens separadas nas pastas data/benign e data/malignant, acompanhadas de seus respectivos arquivos metadata.csv.

## 2. Requisitos e Instalação
Python 3.10+

Ambiente Virtual (recomendado)

Para configurar o ambiente localmente, siga os passos:

```Bash
# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate
```
```Bash
# instale as dependências
pip install -r requirements.txt
```

## 3. Variáveis de Ambiente
O pipeline depende de configurações definidas em um arquivo .env na raiz do projeto.

Parâmetros disponíveis:

HF_MODEL_ID: ID do modelo no Hugging Face (Padrão: VRJBro/skin-cancer-detection).

HUGGINGFACE_HUB_TOKEN (ou HF_TOKEN): Token de leitura para baixar modelos de repositórios privados (opcional).

MLFLOW_TRACKING_URI: URL do servidor MLflow (ex: http://localhost:5000).

MLFLOW_EXPERIMENT_NAME: Nome do experimento no MLflow.

MLFLOW_MODEL_NAME: Nome para registro do modelo no Model Registry.

## 4. Como Executar o Pipeline (Batch)

Este fluxo avalia todo o dataset presente na pasta data/ e envia as métricas para o MLflow.

### Passo 1: Iniciar o servidor MLflow
Abra uma nova janela do terminal, ative o venv e rode:

```Bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```
Acesse http://localhost:5000 no navegador para ver a interface gráfica.

### Passo 2: Executar a validação e inferência
No terminal principal, carregue as variáveis e rode o script:

```Bash
# Carrega as variáveis do .env (Linux/Mac)
set -a; [ -f .env ] && source .env || true; set +a
```
```Bash
# Executa o pipeline
python src/main.py
```

### 5. Deploy: API de Inferência (FastAPI)
O projeto inclui um servidor para testes de inferência em tempo real. A API carrega o classificador via transformers.pipeline e expõe a rota POST /predict.

Para rodar a API:

```Bash
# A API iniciará em http://0.0.0.0:8000
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```
Acesse http://localhost:8000/docs para interagir com o Swagger UI, fazer upload de imagens e receber as predições em JSON.