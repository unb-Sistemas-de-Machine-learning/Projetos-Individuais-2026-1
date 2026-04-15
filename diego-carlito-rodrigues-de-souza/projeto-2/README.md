# Sistema de Classificação de Tickets de Suporte

Pipeline end-to-end focado em MLOps, utilizando modelo Zero-Shot (BART), Guardrails de Segurança (PII e Confiança) e rastreabilidade completa via MLflow.

## Contribuidores

| Matrícula | Nome | GitHub
| --------- | ---- | ------ |
| 221007690 | Diego Carlito Rodrigues de Souza  | [@DiegoCarlito](https://github.com/DiegoCarlito) |
| 221008300 | Marcos Antonio Teles de Castilhos | [@Marcosatc147](https://github.com/Marcosatc147) |

## Estrutura do Projeto

* `src/ingest.py`: Ingestão, higienização e amostragem de dados.
* `src/model_engine.py`: Motor de inferência usando Hugging Face Transformers.
* `src/guardrails.py`: Travas de segurança para mascaramento de PII e filtro de baixa confiança (Revisão Humana).
* `src/main.py`: Orquestrador do pipeline e integração com MLflow.

## Como iniciar o ambiente

1. Crie o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Executar o Pipeline

1. **Execução do Orquestrador:**
Na raiz do projeto, execute o script principal (O dataset completo já está hospedado na pasta `data/` do repositório. O script orquestrador fará a leitura e a amostragem configurada automaticamente):
```bash
python src/main.py
```

*(Nota: Na primeira execução, os pesos do modelo BART-Large-MNLI serão baixados automaticamente para o cache local da máquina).*

2. **Resultados Locais:**
O arquivo processado, contendo as previsões do modelo e os acionamentos de segurança (Guardrails), será salvo automaticamente na pasta `logs/`.

## Rastreabilidade e Observabilidade (MLflow)

O projeto conta com rastreabilidade completa de parâmetros, latência e métricas de confiança. Para visualizar os resultados:

1. Em um novo terminal, com o `venv` ativado, inicie o servidor do MLflow:
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

2. Acesse `http://127.0.0.1:5000/` no seu navegador e abra o experimento **Zero-Shot_Ticket_Classification**.
