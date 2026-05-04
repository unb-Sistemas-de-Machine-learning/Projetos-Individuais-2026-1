# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

> **Integrantes:** Hian Praxedes de Souza Oliveira / Silas Neres  
> **Matrículas:** 200019520 / 200043536  
> **Data de entrega:** 12/04/2026

---

## 1. Resumo do Projeto

Este projeto implementa um sistema end-to-end de detecção de phishing em e-mails com foco em engenharia de ML Systems, utilizando MLflow para rastreamento de experimentos, registro de artefatos, versionamento e deploy local para inferência. O problema escolhido foi a classificação de textos de e-mail em duas classes: phishing ou legítimo. Para atender ao requisito de reuso de modelo pré-treinado, foi utilizado o modelo `ElSlay/BERT-Phishing-Email-Model`, integrado ao pipeline sem treinamento do zero. O dataset utilizado foi o `zefang-liu/phishing-email-dataset`, carregado programaticamente com a biblioteca `datasets` do ecossistema Hugging Face.

O pipeline implementado cobre ingestão, validação, normalização, particionamento, inferência em lote, avaliação, logging no MLflow, registro do modelo e serving local. Na execução principal registrada, o sistema processou 2631 exemplos no conjunto de teste, com `accuracy = 0.9945`, `precision = 0.9858`, `recall = 1.0000` e `f1 = 0.9928`, considerando os exemplos aceitos pelos guardrails. O modelo também foi servido localmente com sucesso e testado via endpoint `/invocations`. Em testes adversariais adicionais, o sistema obteve `21/30` acertos (`70%`), mostrando desempenho forte em casos claros e limitações em cenários de spear phishing e phishing misturado em mensagens corporativas mais realistas.

---

## 2. Escolha do Problema, Dataset e Modelo

### 2.1 Problema

O problema escolhido foi a detecção automática de phishing em e-mails. Esse problema é relevante porque ataques de phishing continuam sendo uma das formas mais comuns de engenharia social em ambientes corporativos e pessoais. Um sistema de classificação automática pode auxiliar na triagem inicial de mensagens suspeitas, reduzindo a carga manual de inspeção e servindo como apoio a fluxos de segurança.

Neste projeto, o objetivo não foi construir um detector do zero, mas sim estruturar um sistema de ML completo, rastreável, reproduzível e com deploy funcional, seguindo a proposta da disciplina.

### 2.2 Dataset

| Item | Descrição |
|------|-----------|
| **Nome do dataset** | `zefang-liu/phishing-email-dataset` |
| **Fonte** | Hugging Face Datasets |
| **Tamanho** | 18.650 registros carregados |
| **Tipo de dado** | Texto de e-mails para classificação binária |

### 2.3 Modelo pré-treinado

| Item | Descrição |
|------|-----------|
| **Nome do modelo** | `ElSlay/BERT-Phishing-Email-Model` |
| **Fonte** (ex: Hugging Face) | Hugging Face |
| **Tipo** (ex: classificação, NLP) | NLP / classificação de texto |
| **Fine-tuning realizado?** | Não |

---

## 3. Pré-processamento

As principais decisões de pré-processamento adotadas foram:

- carregamento programático do dataset com `datasets.load_dataset`, evitando download manual;
- inspeção inicial das colunas e geração de artefatos de validação;
- normalização do schema para um formato simples com as colunas `text` e `label`;
- padronização dos rótulos para classificação binária;
- remoção de valores nulos e remoção de registros duplicados;
- particionamento estratificado em treino, validação e teste;
- definição de guardrails para entradas vazias, muito curtas, muito longas e casos de baixa confiança.

---

## 4. Estrutura do Pipeline

O pipeline implementado segue a seguinte lógica:

```text
Ingestão → Validação → Normalização → Split → Carregamento do modelo → Inferência em lote → Avaliação → Registro no MLflow → Registro do modelo → Deploy
```

### Estrutura do código

```text
projeto-2/
├── configs/
├── data/
│   ├── raw/
│   └── processed/
├── evidence/
├── reports/
├── scripts/
│   ├── run_pipeline.py
│   ├── register_model.py
│   └── run_inference.py
├── src/
│   ├── data/
│   │   ├── download.py
│   │   ├── validate.py
│   │   ├── normalize.py
│   │   └── split.py
│   ├── model/
│   │   ├── load_model.py
│   │   └── predict.py
│   ├── evaluation/
│   │   └── evaluate.py
│   ├── serving/
│   │   └── guardrails.py
│   └── tracking/
├── tests/
├── requirements.txt
└── relatorio-entrega.md
```

---

## 5. Uso do MLflow

### 5.1 Rastreamento de experimentos

O MLflow foi utilizado para registrar a execução completa do pipeline de inferência e avaliação. O experimento foi criado com o nome `phishing-email-mlflow`, e cada execução registrou parâmetros, métricas e artefatos relevantes da pipeline.

- **Parâmetros registrados:**
  - `model_name`
  - `dataset_name`
  - `confidence_threshold`
  - `max_length`
  - `random_state`
  - `test_path`

- **Métricas registradas:**
  - `accuracy`
  - `precision`
  - `recall`
  - `f1`
  - `accept_rate`
  - `rejection_rate`
  - `abstain_rate`
  - `avg_latency_ms`

- **Artefatos salvos:**
  - `manifest.json`
  - `data_validation.json`
  - `test_predictions.csv`
  - `monitoring_summary.json`
  - `classification_report.json`
  - `error_examples.csv`
  - `confusion_matrix.png`

Na execução principal do projeto, foram obtidos os seguintes resultados:

- `total_rows = 2631`
- `accepted_count = 2370`
- `rejected_count = 251`
- `abstain_count = 10`
- `accuracy = 0.9945`
- `precision = 0.9858`
- `recall = 1.0000`
- `f1 = 0.9928`
- `avg_latency_ms = 534.82`

### 5.2 Versionamento e registro

Após o logging da execução principal, o modelo foi logado no MLflow e registrado no **Model Registry** com o nome:

```text
phishing-email-detector
```

Esse registro permitiu criar uma versão reutilizável do modelo e utilizá-la posteriormente no serving local com `models:/phishing-email-detector/1`.

### 5.3 Evidências

As evidências coletadas do MLflow incluíram:

- experimento e run visíveis na UI;
- parâmetros e métricas registrados;
- artefatos da execução disponíveis na interface;
- modelo registrado em `Registered Models`;
- serving do modelo com acesso funcional ao endpoint `/invocations`.

---

## 6. Deploy

O modelo foi disponibilizado para inferência local utilizando o serving do MLflow a partir do modelo registrado no Model Registry.

- **Método de deploy:** `mlflow models serve`
- **Como executar inferência:** servidor local com endpoint REST

### Subida do tracking server

```bash
python -m mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

### Registro do modelo

```bash
python -m scripts.register_model
```

### Serving do modelo registrado

```bash
python -m mlflow models serve -m models:/phishing-email-detector/1 -p 5001 --env-manager local
```

### Exemplo de inferência

```bash
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5001/invocations" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"dataframe_records":[{"text":"Dear user, your account has been suspended. Click here immediately to verify your credentials and avoid permanent closure."}]}'
```

Durante os testes de serving:
- uma mensagem legítima retornou `LABEL_0`;
- uma mensagem de phishing retornou `LABEL_1`.

---

## 7. Guardrails e Restrições de Uso

Foram implementados mecanismos básicos para reduzir uso indevido do sistema:

- rejeição de entrada vazia (`empty_text`);
- rejeição de texto muito curto (`too_short`);
- rejeição de texto excessivamente longo (`too_long`);
- política de abstenção para casos de baixa confiança (`low_confidence`);
- separação entre casos aceitos, rejeitados e em abstenção no relatório de monitoramento.

Esses guardrails não eliminam risco de erro, mas ajudam a evitar inferências automáticas em entradas inadequadas ou pouco confiáveis. Os testes adversariais também mostraram que guardrails de qualidade de entrada não resolvem o problema de mensagens maliciosas sofisticadas quando elas são escritas em contexto corporativo convincente.

---

## 8. Observabilidade

O monitoramento do sistema foi configurado por meio do MLflow, utilizando tanto o tracking de execuções quanto o armazenamento de artefatos de avaliação.

- **Comparação de execuções:** o projeto foi preparado para registrar múltiplas runs dentro do experimento `phishing-email-mlflow`, permitindo comparação posterior entre configurações.
- **Análise de métricas:** accuracy, precision, recall, f1, taxas de rejeição/abstenção e latência média foram registradas na UI.
- **Capacidade de inspeção:** a run salva permite abrir diretamente os artefatos de avaliação, como `classification_report.json`, `error_examples.csv` e `confusion_matrix.png`.

Além das métricas do pipeline principal, foi executado um teste adversarial manual com 30 exemplos divididos em grupos de dificuldade. Nesse teste, o sistema obteve:

- `FINAL SCORE = 21/30`
- `ACCURACY = 70.00%`

Detalhamento por grupo:
- `safe_corporate: 4/4 (100.00%)`
- `safe_weird_ham: 4/4 (100.00%)`
- `phishing_spam: 4/4 (100.00%)`
- `phishing_stock: 4/4 (100.00%)`
- `phishing_mixed_professional: 0/4 (0.00%)`
- `phishing_spear: 0/4 (0.00%)`
- `ambiguous_borderline: 5/6 (83.33%)`

Esse resultado indica que o sistema responde muito bem a casos claros e próximos do padrão do dataset, mas apresenta limitação importante em spear phishing e em phishing escondido em mensagens corporativas realistas.

---

## 9. Limitações e Riscos

As principais limitações e riscos identificados foram:

- o sistema foi estruturado com foco em pipeline, rastreamento e deploy, e não em validação externa ampla;
- o modelo utilizado já foi previamente ajustado para a tarefa, o que reduz o foco em modelagem e desloca a ênfase para integração e operação;
- o serving local em Windows exigiu cuidado adicional com dependências e configuração de ambiente;
- os guardrails implementados são básicos e não cobrem todos os cenários possíveis de uso indevido;
- a interpretação final do resultado do classificador ainda deve ser tratada como apoio automatizado, não como decisão única;
- em testes adversariais, o sistema falhou completamente nos grupos `phishing_mixed_professional` e `phishing_spear`, indicando fragilidade diante de e-mails maliciosos mais profissionais e contextualmente realistas.

Além disso, a suíte de testes automatizados ainda precisa ser consolidada de forma mais completa antes de uma submissão final robusta.

---

## 10. Como executar

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Baixar os dados
python src/data/download.py

# 4. Validar os dados
python src/data/validate.py

# 5. Normalizar o dataset
python src/data/normalize.py

# 6. Gerar splits
python src/data/split.py

# 7. Subir o MLflow Tracking Server
python -m mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db

# 8. Rodar o pipeline principal
python -m scripts.run_pipeline

# 9. Registrar o modelo
python -m scripts.register_model

# 10. Servir o modelo registrado
python -m mlflow models serve -m models:/phishing-email-detector/1 -p 5001 --env-manager local

# 11. Executar inferência via endpoint
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5001/invocations" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"dataframe_records":[{"text":"Dear user, please verify your account immediately by clicking the secure link below."}]}'
```

---

## 11. Referências

1. Hugging Face Datasets. `zefang-liu/phishing-email-dataset`.
2. Hugging Face Models. `ElSlay/BERT-Phishing-Email-Model`.
3. MLflow Documentation. Tracking, Model Registry e Local Model Serving.

---

## 12. Checklist de entrega

- [x] Código-fonte completo
- [x] Pipeline funcional
- [x] Configuração do MLflow
- [x] Evidências de execução (logs, prints ou UI)
- [x] Modelo registrado
- [x] Script ou endpoint de inferência
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto
