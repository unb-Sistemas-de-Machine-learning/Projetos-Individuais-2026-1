# Detalhes Técnicos: Engenharia de ML e Arquitetura do Sistema

Este documento consolidado provê uma visão técnica aprofundada sobre a implementação, arquitetura de sistemas e os desafios enfrentados no desenvolvimento do pipeline do Projeto 2.

---

## 1. Engenharia de Dados (Pipeline de Ingestão)
O dataset `CICIDS2017` apresenta desafios de qualidade que impactam a estabilidade numérica dos modelos.

*   **Padronização:** Implementação do módulo `clean_column_names` via `str.strip()` para eliminar espaços em branco invisíveis nos cabeçalhos.
*   **Tratamento de Dados:** Substituição programática de valores infinitos (`np.inf`) e nulos (`NaN`) para garantir a estabilidade numérica dos algoritmos.
*   **Modularidade:** Todo o pré-processamento é encapsulado em `src/ids/data_preprocessing.py`, separando a limpeza da etapa de treinamento.

## 2. Modelagem (Módulos de Segurança)
### 2.1 Módulo IDS (Intrusion Detection System)
*   **Status:** **Validado e Funcional**. O pipeline de treinamento está operacional (Ingestão -> Limpeza -> Treino -> Registro).
*   **Abordagem:** *Unsupervised Anomaly Detection* via `IsolationForest`.
*   **Seleção:** Eficaz na detecção de *Port Scanning* com datasets de alto volume.
*   **Configuração:** Parâmetro `contamination` ajustado para isolar 1% do comportamento da rede como anômalo.

### 2.2 Módulo Phishing (NLP)
*   **Abordagem:** Classificação baseada em *Transformers* (fine-tuning do modelo `DistilBERT`).
*   **Status:** Próximo passo (Planejamento de implementação).

## 3. Arquitetura de ML Systems (MLOps em Ação)
O sistema foi estruturado para suportar o ciclo de vida completo de ML:

*   **Rastreabilidade (MLflow Tracking):** Registro automático de hiperparâmetros e persistência de modelos no MLflow. A estrutura `mlruns/` armazena todos os metadados de execução.
*   **Reprodutibilidade:** Uso de `pyenv` (Python 3.10.12) e um `requirements.txt` rigoroso para evitar conflitos de dependências.
*   **Observabilidade:** Interface de comparação (`mlflow ui`) para garantir que o melhor modelo seja promovido.

## 4. Próximos Passos
- **Módulo Phishing:** Iniciar o desenvolvimento de `src/phishing/data_preprocessing.py` utilizando `DistilBERT`.
- **Performance:** Migração de `csv` para `parquet` para otimização de I/O em grandes volumes.
- **Guardrails:** Implementação de camadas de validação de schemas de entrada (via `pydantic`).
