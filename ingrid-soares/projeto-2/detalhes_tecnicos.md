# Detalhamento do Projeto: Sistema de Segurança Integrado (IDS & Phishing Detection)

Este documento detalha o **Projeto Individual 2**, focado em **ML Systems** aplicado à **Cibersegurança**. O sistema integra dois módulos de segurança operando sobre o mesmo pipeline de ML gerenciado pelo MLflow.

---

## 1. Estrutura do Projeto
O projeto está organizado para garantir modularidade e reprodutibilidade:
- `data/`: Armazena datasets brutos e processados (ex: `cleaned_ids_data.csv`).
- `src/`: Contém os módulos de processamento:
    - `ids/`: Pré-processamento e treinamento do modelo de rede.
    - `phishing/`: Extração de features e modelo de classificação de URLs.
- `models/`: Artefatos dos modelos treinados.
- `mlruns/`: Registro de experimentos do MLflow.

---

## 2. Implementação do Módulo IDS (Etapa Atual)
Atualmente, estamos focados no **Módulo IDS**.
- **Dataset:** `CICIDS2017`.
- **Objetivo:** Detectar atividades de reconhecimento (*Port Scanning*) e padrões anômalos.
- **Implementação:** O script `src/ids/data_preprocessing.py` realiza a limpeza necessária, tratando colunas com espaços, valores infinitos e dados nulos, garantindo a integridade dos dados antes da alimentação do modelo.

### Como Executar:
Após baixar os arquivos CSV do dataset para `data/ids/`, execute o pré-processamento:
```bash
python src/ids/data_preprocessing.py
```
Este comando gerará o arquivo `cleaned_ids_data.csv`, pronto para ser usado no treinamento do modelo clássico (ex: Isolation Forest).

---

## 3. Próximos Passos
1. Finalizar o pipeline de treinamento (`model_training.py`) registrando parâmetros e artefatos no **MLflow**.
2. Implementar o módulo de **Phishing de URLs** usando `DistilBERT`.
3. Integrar **Guardrails** e métricas de **Observabilidade** para monitorar o desempenho em tempo real.
4. Refinar os relatórios técnicos conforme os templates fornecidos.
