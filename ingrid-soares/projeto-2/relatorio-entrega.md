# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

**Aluno(a):** Ingrid Soares  
**Matrícula:** [Sua matrícula]  
**Data de entrega:** 15/04/2026

---

## 1. Resumo do Projeto
Sistema integrado de cibersegurança utilizando ML para detecção de anomalias (IDS/CICIDS2017) e detecção de Phishing (URLs/Hugging Face). O projeto foca na engenharia de pipeline, versionamento e observabilidade, utilizando MLflow para todo o ciclo de vida dos modelos.

## 2. Escolha do Problema, Dataset e Modelo
### 2.1 Problema
Detecção de intrusões de rede (reconhecimento) e phishing. Problemas críticos em segurança corporativa.

### 2.2 Dataset
| Item | Descrição |
| :--- | :--- |
| Nome do dataset | CICIDS2017 e Dataset de URLs |
| Fonte | UNB / Kaggle |
| Tamanho | ~10GB / Variável |
| Tipo de dado | Rede (NetFlow) / Texto |

### 2.3 Modelo pré-treinado
| Item | Descrição |
| :--- | :--- |
| Nome do modelo | DistilBERT |
| Fonte | Hugging Face |
| Tipo | NLP - Classificação |
| Fine-tuning realizado? | Sim |

## 3. Pré-processamento
Limpeza de nomes de colunas, tratamento de valores `inf` e `NaN`, normalização de features e codificação de labels para o IDS.

## 4. Estrutura do Pipeline
Ingestão → Pré-processamento → Carregamento do modelo → Avaliação → Registro MLflow → Deploy

**Estrutura do código:**
```
projeto-2/
├── src/
├── data/
├── mlruns/
├── requirements.txt
└── README.md
```

## 5. Uso do MLflow
### 5.1 Rastreamento de experimentos
- **Parâmetros:** `contamination` (IDS), `learning_rate`, `epochs` (Phishing).
- **Métricas:** F1-Score, Precisão, Recall.
- **Artefatos:** Modelos salvos, artefatos de pré-processamento.

### 5.2 Versionamento e registro
Modelos registrados no MLflow Model Registry com assinaturas e metadados.

### 5.3 Evidências
*(Inserir prints da UI do MLflow aqui)*

## 6. Deploy
- **Método:** Script de inferência local (`src/*/inference.py`).
- **Execução:** Carregamento do modelo a partir do registro do MLflow.

## 7. Guardrails e Restrições de Uso
Implementação de validação de input de URLs e limiares de confiança para alertas de rede.

## 8. Observabilidade
Configuração de métricas de performance e comparação de execuções via MLflow UI.

## 9. Limitações e Riscos
Necessidade de retreinamento periódico devido à evolução das técnicas de ataque.

## 10. Como executar
1. `pip install -r requirements.txt`
2. `python src/ids/data_preprocessing.py`
3. `mlflow ui`
4. `python src/phishing/inference.py`

## 11. Referências
- UNB CICIDS2017 Dataset Documentation.
- Hugging Face Transformers Library.

## 12. Checklist de entrega
- [ ] Código-fonte completo
- [ ] Pipeline funcional
- [ ] Configuração do MLflow
- [ ] Evidências de execução
- [ ] Modelo registrado
- [ ] Script ou endpoint de inferência
- [ ] Relatório de entrega preenchido
- [ ] Pull Request aberto
