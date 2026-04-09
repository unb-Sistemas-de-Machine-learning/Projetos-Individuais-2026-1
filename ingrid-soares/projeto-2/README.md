# Projeto 2: Sistema de Segurança Integrado (IDS & Phishing)

## 1. Visão Geral
Este repositório contém a implementação de um **Sistema de Segurança Integrado** (Intrusion Detection System - IDS e Phishing Detection) desenvolvido sob a ótica de **ML Systems**.

O projeto prioriza a engenharia de pipeline, versionamento de artefatos e observabilidade, garantindo que o sistema seja modular, reprodutível e robusto para ambientes de produção.

## 2. Arquitetura do Sistema
O sistema é composto por dois módulos independentes que compartilham a mesma infraestrutura de logging via **MLflow**:

*   **Módulo IDS:** Utiliza *Isolation Forest* para detecção de anomalias em tráfego de rede (Dataset CICIDS2017).
*   **Módulo Phishing:** Utiliza *DistilBERT* (Hugging Face) para classificação de URLs maliciosas.

## 3. Estrutura de Pastas
```
ingrid-soares/projeto-2/
├── data/ids             # Ingestão (ids/ e phishing/)
├── src/                 # Lógica (ids/ e phishing/ e common/)
├── models/              # Artefatos registrados
├── mlruns/              # Rastreamento MLflow
├── README.md            # Visão geral
└── detalhes-tecnicos.md # Detalhes extras
└── relatorio-entrega.md # Informações de escopo
└── relatorio-tecnico.md # Detalhes da implementação
```

## 4. Tecnologias
- **MLOps:** MLflow (tracking, registry, observabilidade).
- **ML Frameworks:** Scikit-Learn (IDS), PyTorch/Transformers (Phishing).
- **Ambiente:** Python 3.10.12, gerido via `pyenv`.
