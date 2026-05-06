# Projeto 2: Sistema de Segurança Integrado (IDS & Phishing)

## Objetivo
Desenvolver um pipeline de Machine Learning Systems (MLOps) completo para detecção de ameaças cibernéticas. O sistema integra dois módulos especializados:
1. IDS (Intrusion Detection System): Detecção de anomalias em tráfego de rede (CICIDS2017) via Isolation Forest.
2. Phishing Detector: Classificação semântica de URLs maliciosas via Fine-tuning do DistilBERT (Hugging Face).

O foco central é a engenharia de pipeline, utilizando MLflow para rastreamento, versionamento de artefatos, observabilidade e registro de modelos.

## Arquitetura do Sistema
O sistema segue padrões de modularidade, garantindo a separação entre ingestão, treinamento e inferência:

```text
projeto-2/
├── data/               # Datasets brutos e processados
├── mlruns/             # Central de experimentos e rastreabilidade (MLflow)
├── src/                # Lógica central
│   ├── ids/            # Pipeline de anomalia de rede
│   ├── phishing/       # Pipeline de NLP/Phishing (fine-tuning)
│   └── common/         # Utilitários de infraestrutura (logging/config)
└── requirements.txt    # Dependências fixadas
```

## Funcionalidades MLOps
- Rastreabilidade: Todos os experimentos são registrados via mlflow.start_run.
- Registro de Modelos: Modelos versionados via MLflow Registry.
- Reprodutibilidade: Ambientes gerenciados e dependências fixadas em requirements.txt.
- Guardrails: Validação de schemas de entrada (via pydantic) para evitar injeção de dados malformados.
- Observabilidade: Monitoramento de métricas (Accuracy, F1, n_anomalies) via dashboard nativo do MLflow.

## Como Executar

### 1. Preparação do Ambiente
```bash
pip install -r requirements.txt
```

### 2. Execução de Treinamento
*   IDS (Anomalia de Rede):
    ```bash
    python src/ids/model_training.py
    ```
*   Phishing (Fine-tuning DistilBERT):
    ```bash
    TRAIN_EPOCHS=3 TRAIN_BATCH_SIZE=8 python src/phishing/fine_tuning.py
    ```

### 3. Observabilidade
```bash
mlflow ui
# Acesse http://localhost:5000 para monitorar experimentos e artefatos
```

### 4. Inferência (Deploy Local)
```bash
# Para IDS:
python src/ids/inference.py

# Para Phishing:
python src/phishing/inference.py
```

## Documentação Técnica
- Detalhes Técnicos: Engenharia e Arquitetura.
- Relatório de Entrega: Documento oficial de submissão.
