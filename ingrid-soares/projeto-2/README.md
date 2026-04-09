# Projeto 2: Sistema de Segurança Integrado (IDS & Phishing)

## Objetivo
Desenvolver um sistema de machine learning end-to-end, focado em **ML Systems**, utilizando **MLflow** para rastreamento de experimentos, versionamento, registro, deploy e observabilidade. O sistema integra dois módulos: detecção de anomalias em tráfego de rede (IDS) e detecção de phishing via URL.

## Estrutura do Repositório
- `data/`: Ingestão de dados brutos e limpos.
- `src/`: Lógica de pré-processamento, treinamento e inferência.
- `detalhes-tecnicos.md`: Documentação técnica de engenharia.
- `relatorio-tecnico.md`: Relatório oficial de entrega.

## Execução
1. `pip install -r requirements.txt`
2. `python src/ids/data_preprocessing.py`
3. `python src/ids/model_training.py`
4. `mlflow ui`
