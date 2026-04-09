# Detalhes Técnicos: Engenharia de ML e Arquitetura do Sistema

Este documento consolidado provê uma visão técnica aprofundada sobre a implementação, arquitetura de sistemas e os desafios enfrentados no desenvolvimento do pipeline do Projeto 2.

---

## 1. Engenharia de Dados (Pipeline de Ingestão)
O dataset `CICIDS2017` apresenta desafios de qualidade que impactam a estabilidade numérica dos modelos.

*   **Padronização:** Implementação do módulo `clean_column_names` via `str.strip()` para eliminar espaços em branco invisíveis nos cabeçalhos.
*   **Tratamento de Dados:** Substituição programática de valores infinitos (`np.inf`) e nulos (`NaN`) para garantir a convergência dos algoritmos.
*   **Modularidade:** Todo o pré-processamento é encapsulado em `src/ids/data_preprocessing.py`, separando a limpeza da etapa de treinamento.

## 2. Modelagem (Módulos de Segurança)
### 2.1 Módulo IDS (Intrusion Detection System)
*   **Abordagem:** *Unsupervised Anomaly Detection* via `Isolation Forest`.
*   **Seleção:** Escolhido pela eficácia na detecção de *Port Scanning* com datasets de alto volume.
*   **Configuração:** Parâmetro `contamination` ajustado para isolar 1% do comportamento da rede como anômalo.

### 2.2 Módulo Phishing (NLP)
*   **Abordagem:** Classificação baseada em *Transformers* (fine-tuning do modelo `DistilBERT`).
*   **Estrutura:** Integração via `Hugging Face Transformers` para extração de features textuais de URLs.

## 3. Arquitetura de ML Systems
O sistema foi estruturado para suportar o ciclo de vida completo de ML (*MLOps*):

*   **Rastreabilidade (MLflow Tracking):** Registro automático de hiperparâmetros (contamination, learning rates) e métricas de performance (F1-Score, Recall).
*   **Reprodutibilidade:** Uso de `pyenv` (Python 3.10.12) e um `requirements.txt` rigoroso para evitar o "Dependency Hell".
*   **Observabilidade:** Monitoramento contínuo através da `MLflow UI`, permitindo a inspeção de artefatos e comparação de experimentos em tempo real.

## 4. Próximos Passos Técnicos
- **Performance:** Migração do formato `csv` para `parquet` para otimização de I/O em grandes volumes.
- **Guardrails:** Implementação de camadas de validação de schemas de entrada (via `pydantic`) para garantir a integridade dos dados antes da inferência.
- **Monitoramento:** Configuração de Dashboards de drift de dados e performance do modelo em ambiente de produção.
