# Sistema de Classificação de Tickets de Suporte

Pipeline end-to-end com MLflow focado em MLOps, Guardrails e Rastreabilidade.

## Contribuidores

| Matrícula | Nome | GitHub
| --------- | ---- | ------ |
| 221007690 | Diego Carlito Rodrigues de Souza  | [@DiegoCarlito](https://github.com/DiegoCarlito) |
| 221008300 | Marcos Antonio Teles de Castilhos | [@Marcosatc147](https://github.com/Marcosatc147) |

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

3. Inicie o servidor do MLflow (em outro terminal):
```bash
mlflow ui
```