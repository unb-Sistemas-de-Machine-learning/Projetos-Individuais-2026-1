# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

> **Aluno(a):** Ana Luiza Soares de Carvalho
> **Matrícula:** 231011088
> **Data de entrega:** 15/04/2026

---

## 1. Resumo do Projeto

O projeto desenvolve um sistema de Inferência de Linguagem Natural (NLI) para classificar relações entre premissas e hipóteses (contradição, neutralidade ou implicação). Utilizou-se o modelo pré-treinado **DeBERTa-v3-small** em arquitetura de **Cross-Encoder**. O foco central foi a engenharia de **ML Systems**, integrando o **MLflow** via **DagsHub** para rastreamento de experimentos, versionamento de artefatos e registro de modelos. Foi realizada uma tentativa experimental de implementar **Guardrails** de idioma no deploy para mitigar predições fora do domínio, embora a camada tenha apresentado rigidez na validação de alguns termos em inglês.

---

## 2. Escolha do Problema, Dataset e Modelo

### 2.1 Problema

O problema de NLI busca identificar se uma hipótese é logicamente verdadeira, falsa ou neutra em relação a uma premissa. É relevante para tarefas de auditoria de consistência textual e sistemas de checagem de fatos.

### 2.2 Dataset

| Item | Descrição |
|------|-----------|
| **Nome do dataset** | Contradictory, My Dear Watson |
| **Fonte** | [Kaggle](https://www.kaggle.com/competitions/contradictory-my-dear-watson/data) |
| **Tamanho** | 2.77 MB |
| **Tipo de dado** | CSV |

### 2.3 Modelo pré-treinado

| Item | Descrição |
|------|-----------|
| **Nome do modelo** | `nli-deberta-v3-small` |
| **Fonte** (ex: Hugging Face) | Hugging Face (`cross-encoder/nli-deberta-v3-small`) |
| **Tipo** (ex: classificação, NLP) | NLP (Cross-Encoder / Transformers) |
| **Fine-tuning realizado?** | Sim |

---

## 3. Pré-processamento

As decisões de pré-processamento visaram a especialização do modelo no idioma inglês:

- **Filtragem de Idioma:** Recorte do dataset original (multilíngue) para conter apenas amostras em inglês.
- **Particionamento Estratificado:** Divisão em 80/20 (treino/validação) mantendo o equilíbrio das classes.
- **Tokenização e Padronização:** Conversão dos pares de texto em tensores com limite de 128 tokens para otimização de memória.

---

## 4. Estrutura do Pipeline

O pipeline foi modularizado para garantir isolamento e reprodutibilidade de cada etapa:

```
Ingestão → Pré-processamento → Carregamento do modelo → Avaliação → Registro MLflow → Deploy
```

### Estrutura do código

```
contraditory/
├── src/
│   ├── ingestion.py           # Carga inicial dos dados
│   ├── preprocessing.py       # Filtragem e limpeza
│   ├── train.py               # Fine-tuning e registro de logs
│   ├── model_wrapper.py       # Wrapper experimental de inferência
│   └── deploy_guardrails.py   # Registro do modelo final com lógica extra
├── data/
│   ├── train.csv              # Bruto
│   └── processed/             # Processado
├── mlruns/                    # Logs locais (residência gitignore)
├── requirements.txt           # Dependências
└── README.md
└── relatorio-entrega.md
```

---

## 5. Uso do MLflow

### 5.1 Rastreamento de experimentos

O MLflow foi utilizado para centralizar toda a vida útil do experimento no DagsHub:

- **Repositório de Tracking:** [https://dagshub.com/Ana-Luiza-SC/contraditory](https://dagshub.com/Ana-Luiza-SC/contraditory)
- **Parâmetros registrados:** `learning_rate` (2e-5), `num_train_epochs` (3), `batch_size`, `model_name`.
- **Métricas registradas:** `f1_macro`, `accuracy`, `loss`, `eval_runtime`.
- **Artefatos salvos:** Matriz de confusão (CSV), dataset processado e arquivos do modelo (`config.json`, pesos).

### 5.2 Versionamento e registro

O modelo foi versionado em duas fases no **Model Registry**: primeiro como um checkpoint bruto de treinamento e, posteriormente, como uma versão de produção (`contraditory-crossencoder-final`) encapsulada em um wrapper Python personalizado.

### 5.3 Evidências

Experimentos e métricas registrados podem ser consultados no link oficial do DagsHub citado acima, onde constam as execuções de Ingestão, Pré-processamento e Treinamento.

---

## 6. Deploy

O modelo foi disponibilizado via o ecossistema do MLflow para consumo em tempo de execução.

- **Método de deploy:** Script local de inferência carregando o modelo do Registry (`mlflow.pyfunc`).
- **Como executar inferência:**

```bash
# Exemplo de comando via script Python de teste
python src/test.py
```

---

## 7. Guardrails e Restrições de Uso

Implementou-se uma tentativa experimental de validação de entrada:

- **Validação de Idioma:** Tentativa de uso da biblioteca `langdetect` para rejeitar frases fora do idioma inglês.
- **Restrição Sintática:** O wrapper garante que a entrada seja um par Premissa/Hipótese antes de processar.
- **Filtro de Confiança:** Predições com scores inconsistentes são sinalizadas para evitar respostas de falsa confiança.

---

## 8. Observabilidade

O monitoramento foi focado na inspeção do comportamento do modelo em diferentes cenários:

- **Comparação de execuções:** Análise entre o modelo bruto e a versão com guardrails via interface DagsHub.
- **Análise de métricas:** Inspeção da matriz de confusão para validar a capacidade de distinção entre classes.
- **Capacidade de inspeção:** Logs de inferência que detalham o motivo de rejeição ou o nível de confiança da predição.

---

## 9. Limitações e Riscos

- **Instabilidade nos Guardrails:** A camada de detecção de idioma apresentou "falsos negativos", rejeitando frases válidas em inglês (como nomes próprios) devido à rigidez do algoritmo experimental.
- **Sensibilidade Ortográfica:** Erros de digitação impactam a detecção do idioma, gerando erros de acesso.
- **Custo de Inferência:** O uso de Cross-Encoders é computacionalmente mais caro que arquiteturas mais simples em larga escala.

---

## 10. Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar DagsHub (Credenciais via token ou inicialização de script)
python -c "import dagshub; dagshub.init(repo_owner='Ana-Luiza-SC', repo_name='contraditory', mlflow=True)"

# 3. Executar o pipeline completo
python src/ingestion.py
python src/preprocessing.py
python src/train.py

# 4. Registrar deploy experimental
python src/deploy_guardrails.py

# 5. Executar inferência
python src/test.py
```

---

## 11. Referências

1. Hugging Face: `nli-deberta-v3-small` Cross-Encoder.
2. DagsHub MLflow Integration Documentation.
3. Kaggle Competition: *Contradictory, My Dear Watson*.

---

## 12. Checklist de entrega

- [x] Código-fonte completo
- [x] Pipeline funcional
- [x] Configuração do MLflow
- [x] Evidências de execução (logs, prints ou UI)
- [x] Modelo registrado
- [x] Script ou endpoint de inferência
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto

---

## 13. Observações Técnicas

Durante o desenvolvimento, observou-se que a camada de **Guardrails** de idioma (implementada via `langdetect`) apresentou um comportamento excessivamente restritivo, não reconhecendo algumas palavras ou nomes próprios legítimos em inglês, o que resultou em rejeições indevidas de inferência. 

Por esse motivo, o modelo mais estável e recomendado para avaliação de acurácia lógica neste projeto é o **Cross-Encoder original (sem o wrapper final)**. A versão registrada com Guardrails permanece no Model Registry como uma prova de conceito de segurança em ML Systems, demonstrando a capacidade de interceptar e filtrar dados, embora necessite de ajustes na sensibilidade idiomática para uso em produção.