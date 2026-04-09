# Detalhes Técnicos: Engenharia de ML e Arquitetura do Sistema

Este documento consolidado provê uma visão técnica aprofundada sobre a implementação, arquitetura de sistemas e os desafios enfrentados no desenvolvimento do pipeline do Projeto 2.

---

## 1. Engenharia de Dados (Pipeline de Ingestão)
O dataset `CICIDS2017` apresenta desafios de qualidade que impactam a estabilidade numérica dos modelos.

*   **Padronização:** Implementação do módulo `clean_column_names` via `str.strip()` para eliminar espaços em branco invisíveis nos cabeçalhos.
*   **Tratamento de Dados:** Substituição programática de valores infinitos (`np.inf`) e nulos (`NaN`) para garantir a estabilidade numérica dos algoritmos de ML.
*   **Modularidade:** Todo o pré-processamento é encapsulado em `src/ids/data_preprocessing.py`, separando a limpeza da etapa de treinamento.

## 2. Modelagem (Módulos de Segurança)
### 2.1 Módulo IDS (Intrusion Detection System)
*   **Status:** **Validado e Funcional**. O pipeline de treinamento está operacional (Ingestão -> Limpeza -> Treino -> Registro).
*   **Instrumentação:** Adicionado logging de métricas (`n_anomalies` e `n_normal`) via `mlflow.log_metric`.
*   **Abordagem:** *Unsupervised Anomaly Detection* via `IsolationForest`.
*   **Configuração:** Parâmetro `contamination` ajustado para isolar 1% do comportamento da rede como anômalo.

### 2.2 Módulo Phishing (NLP)
*   **Abordagem:** Classificação baseada em *Transformers* (fine-tuning do modelo `DistilBERT` da biblioteca `Hugging Face`).
*   **Componentes:** 
    - `src/phishing/data_preprocessing.py`: Pré-processamento e tokenização para NLP.
*   **Status:** Em desenvolvimento (Pipeline de dados implementado).

## 3. Arquitetura de ML Systems (MLOps em Ação)
O sistema foi estruturado para suportar o ciclo de vida completo de ML:

*   **Rastreabilidade (MLflow Tracking):** Registro automático de hiperparâmetros (contamination) e métricas. O log de métricas transforma dados brutos de execução em gráficos dinâmicos no dashboard, essenciais para validar o impacto dos parâmetros de treino.
*   **Reprodutibilidade:** Uso de `pyenv` (Python 3.10.12) e um `requirements.txt` rigoroso para evitar conflitos de dependências.
*   **Observabilidade:** Interface de comparação (`mlflow ui`) para inspeção de artefatos e métricas em tempo real.

## 4. Próximos Passos Técnicos
- **Módulo Phishing:** Finalizar o fine-tuning do `DistilBERT` e a integração com o MLflow.
- **Performance:** Migração do formato `csv` para `parquet` para otimização de I/O em grandes volumes.
- **Guardrails:** Implementação de camadas de validação de schemas de entrada (via `pydantic`) para garantir a integridade dos dados antes da inferência.
