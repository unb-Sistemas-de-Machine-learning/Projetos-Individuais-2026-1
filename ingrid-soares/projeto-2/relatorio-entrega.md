# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

**Aluno(a):** Ingrid Soares  
**Matrícula:** 160125162
**Data de entrega:** 15/04/2026

---

## 1. Resumo do Projeto
Sistema de segurança integrado para detecção de anomalias em tráfego de rede (IDS/CICIDS2017) e Phishing (URLs/Hugging Face). Foco em engenharia de pipeline, versionamento e observabilidade via MLflow.

## 2. Escolha do Problema, Dataset e Modelo
### 2.1 Problema
Detecção de intrusões (reconhecimento/scanning) e phishing. Problemas críticos em segurança corporativa que exigem abordagens de ML para identificar novas ameaças em tempo real.

### 2.2 Dataset
| Item | Descrição |
| :--- | :--- |
| Nome do dataset | CICIDS2017 e Dataset de URLs |
| Fonte | UNB / Kaggle |

### 2.3 Modelo pré-treinado
| Item | Descrição |
| :--- | :--- |
| Nome | DistilBERT |
| Fonte | Hugging Face |
| Tipo | NLP - Classificação (Fine-tuning realizado via Transformers) |
| Fine-tuning realizado? | Sim (Pipeline implementado) |

## 3. Pré-processamento
Limpeza de colunas (remoção de espaços), tratamento de valores `inf`/`NaN`, normalização de features numéricas e tokenização para NLP.

## 4. Estrutura do Pipeline
Ingestão → Pré-processamento → Carregamento do modelo → Avaliação → Registro MLflow → Deploy

## 5. Uso do MLflow
- **Rastreamento:** Parâmetros (*contamination*, *learning_rate*) e métricas (*F1-Score*, *n_anomalies*) registrados automaticamente a cada execução.
- **Evidências:** Logs, artefatos de modelos registrados no Model Registry.

## 6. Deploy
Script local de inferência via MLflow Models, permitindo a predição em tempo real de novos fluxos de rede e URLs.

## 7. Guardrails e Restrições de Uso
Validação de inputs e limiares de confiança (thresholds) para minimizar falsos positivos em alertas críticos.

## 8. Observabilidade
Configuração de métricas de performance via MLflow UI para inspeção comparativa de experimentos.

## 9. Limitações e Riscos
Necessidade de retreinamento periódico frente a novas variantes de ataques e risco de degradação da performance do modelo (*Data Drift*).

## 10. Como executar
1. `pip install -r requirements.txt`
2. `python src/ids/data_preprocessing.py`
3. `python src/ids/model_training.py`
4. `mlflow ui`

## 11. Referências
- UNB CICIDS2017
- Hugging Face Transformers Library.

## 12. Checklist de entrega
- [x] Código-fonte completo
- [x] Pipeline funcional
- [x] Configuração do MLflow
- [x] Evidências de execução
- [x] Modelo registrado
- [x] Script de inferência
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto
