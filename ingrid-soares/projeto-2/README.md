# Projeto 2: Sistema de Segurança Integrado (IDS & Phishing)

## Objetivo
Desenvolver um sistema de machine learning end-to-end, focado em **ML Systems**, utilizando **MLflow** para rastreamento de experimentos, versionamento, registro, deploy e observabilidade. O sistema integra dois módulos: detecção de anomalias em tráfego de rede (IDS) e detecção de phishing via URL.

## Estrutura do Repositório
- `data/`: Ingestão de dados brutos e limpos.
- `src/`: Lógica de pré-processamento, fine-tuning e inferência.
    - `ids/`: Módulo de detecção de intrusão baseado em *Isolation Forest*.
    - `phishing/`: Módulo de detecção de phishing baseado em *DistilBERT*.
    - `common/`: Utilitários compartilhados.

## Execução
1. `pip install -r requirements.txt`
2. **Treinamento IDS:** `python src/ids/model_training.py`
3. **Fine-tuning Phishing:** `TRAIN_EPOCHS=3 TRAIN_BATCH_SIZE=8 python src/phishing/fine_tuning.py`
4. **MLflow UI:** `mlflow ui`
5. **Inferência:** `python src/ids/inference.py` ou `python src/phishing/inference.py`
