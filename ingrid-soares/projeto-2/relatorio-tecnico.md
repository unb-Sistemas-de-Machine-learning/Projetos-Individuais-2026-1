# Relatório Técnico Final: Sistema de Segurança Integrado (IDS & Phishing)

Este documento consolidado provê uma visão completa sobre a arquitetura do sistema, as escolhas de implementação e os desafios técnicos enfrentados no desenvolvimento do pipeline de ML.

---

## 1. Arquitetura do Sistema
O sistema foi desenhado para ser modular, permitindo a independência entre o módulo de detecção de tráfego de rede (IDS) e o módulo de detecção de Phishing.

- **Módulo IDS:** Foca em identificar anomalias (Port Scanning) através do dataset `CICIDS2017`.
- **Módulo Phishing:** Foca em classificar URLs como maliciosas ou legítimas usando modelos pré-treinados via `Hugging Face`.

## 2. Engenharia de ML e Pipeline
O fluxo foi construído priorizando a reprodutibilidade e a robustez:

### 2.1 Engenharia de Dados (Data Ingestion Pipeline)
O `CICIDS2017` apresenta desafios de qualidade (colunas com espaços ocultos, valores `Infinity`).
*   **Limpeza:** Padronização de cabeçalhos (`str.strip()`).
*   **Tratamento de Anomalias:** Substituição de `np.inf` por `np.nan` e remoção de nulos para estabilidade numérica.
*   **Modularidade:** Processamento centralizado em `src/ids/data_preprocessing.py`.

### 2.2 Modelagem (IDS - Port Scanning)
Escolhemos o **Isolation Forest** por sua eficiência em detecção de anomalias não supervisionada.
*   **Hiperparâmetros:** Contaminação definida para isolar o top 1% de comportamento anômalo.

## 3. Integração MLflow (Rastreamento e Observabilidade)
O MLflow é utilizado como backbone do sistema para garantir o ciclo de vida do modelo:
- **Rastreamento:** Registro de parâmetros (ex: taxas de contaminação) e métricas.
- **Versionamento:** Modelos versionados e persistidos como artefatos prontos para deploy.
- **Observabilidade:** Comparação de execuções para garantir que o melhor modelo seja promovido.

## 4. Próximos Passos Técnicos
- Implementar fine-tuning no modelo *DistilBERT* para o módulo Phishing.
- Adicionar mecanismos de *Guardrails* (validação de schema com `pydantic`).
- Migração de `csv` para `parquet` para otimização de performance.
