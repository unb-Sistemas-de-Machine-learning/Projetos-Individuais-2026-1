# PR - Projeto Individual 2 (MLflow)

## Resumo
Implementa sistema de ML end-to-end para classificacao de sentimento com rastreamento de experimentos, versionamento de modelo e inferencia local.

## Entregas cobertas
- [x] Pipeline funcional
- [x] Uso de MLflow (parametros, metricas, artefatos)
- [x] Registro de modelo no Model Registry
- [x] Guardrails na inferencia
- [x] Observabilidade com comparacao de runs
- [x] Relatorio tecnico atualizado

## Evidencias
- UI runs: `docs/evidencias/01-runs.png`
- UI metricas: `docs/evidencias/02-run-metricas.png`
- UI artifacts: `docs/evidencias/04-run-artifacts.png`
- UI model registry: `docs/evidencias/03-model-registry.png`
- Comparativo de execucoes: `reports/runs_comparison.csv`

## Como reproduzir
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
mlflow ui --backend-store-uri file:./mlruns --port 5000 --host 127.0.0.1
python src/inference.py --text "This movie was amazing and very emotional"
```

## Observacoes
- Backend local de arquivo no MLflow foi usado por simplicidade academica.
- Em producao, migrar para backend SQL (ex: sqlite/postgres) e artifact store dedicado.
