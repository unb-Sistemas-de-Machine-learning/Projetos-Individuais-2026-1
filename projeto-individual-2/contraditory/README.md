# Contradictory, My Dear Watson — Sistema NLI com MLflow

> Para maiores detalhes leia o [**relatório de entrega completo**](./relatorio-entrega.md).

Sistema de **Inferência de Linguagem Natural (NLI)** que classifica relações entre premissas e hipóteses usando **DeBERTa-v3-small** (Cross-Encoder). Integrado com **MLflow** via **DagsHub** para rastreamento de experimentos e deploy com guardrails.

## 🚀 Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar pipeline completo
python src/ingestion.py
python src/preprocessing.py
python src/train.py

# 3. Deploy e inferência
python src/model_wrapper.py
```

## 📊 Dataset & Modelo

| Item | Descrição |
|------|-----------|
| **Dataset** | Contradictory, My Dear Watson (Kaggle) — 2.77 MB |
| **Idioma** | Inglês (filtrado do dataset multilíngue) |
| **Modelo** | `nli-deberta-v3-small` (Hugging Face) |
| **Tipo** | Cross-Encoder / Transformers |

## 🏗️ Estrutura

```
src/
├── ingestion.py           # Carga inicial
├── preprocessing.py       # Filtragem para inglês
├── train.py               # Fine-tuning (3 épocas)
├── model_wrapper.py       # Wrapper com guardrails
└── test_train.py          # Suite de testes
```

## 🛡️ Guardrails

- **Idioma:** Rejeita inputs fora do inglês (via `langdetect`)
- **Formato:** Valida par Premissa/Hipótese
- **Confiança:** Sinaliza predições incertas (score ≤ 0.5)

## 📈 MLflow Integration

- **Registry:** [DagsHub - Ana-Luiza-SC/contraditory](https://dagshub.com/Ana-Luiza-SC/contraditory)
- **Parâmetros rastreados:** learning_rate, batch_size, epochs, metrics
- **Artefatos:** Matriz de confusão, pesos do modelo

## 📝 Mais detalhes

Consulte o [**relatório de entrega completo**](./relatorio-entrega.md) para:
- Análise de limitações e riscos
- Observações técnicas sobre guardrails
- Instruções detalhadas de execução
- Referências e checklist

## 👤 Aluno

**Ana Luiza Soares de Carvalho** — Matrícula: 231011088  
Data de entrega: 15/04/2026
