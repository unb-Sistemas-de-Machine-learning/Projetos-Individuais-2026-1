# Sistema de ML com MLflow - Classificacao de Sentimento

Projeto de referencia para a Parte 2 da disciplina de ML Systems, com foco em engenharia de pipeline e uso completo de MLflow.

## 1. Problema

Classificacao de sentimento de reviews de filmes (positivo ou negativo) usando modelo pre-treinado.

## 2. Modelo reutilizado

- Modelo: distilbert-base-uncased-finetuned-sst-2-english
- Fonte: Hugging Face
- Tipo: classificacao de texto
- Fine-tuning: nao

## 3. Estrutura de pastas

```text
sistema-mlflow-sentimento/
├── data/
│   └── imdb_sample.csv
├── docs/
│   └── relatorio-entrega.md
├── mlruns/
├── reports/
├── src/
│   ├── config.py
│   ├── data_pipeline.py
│   ├── evaluation.py
│   ├── guardrails.py
│   ├── inference.py
│   ├── main.py
│   └── model_pipeline.py
├── requirements.txt
└── README.md
```

## 4. O que este pipeline faz

1. Carrega dataset local de reviews
2. Faz preprocessamento simples de texto
3. Divide em treino e teste
4. Carrega modelo pre-treinado do Hugging Face
5. Avalia no conjunto de teste
6. Registra parametros, metricas e artefatos no MLflow
7. Salva e registra modelo no Model Registry local
8. Permite inferencia via script

## 5. Guardrails implementados

- Rejeita entrada vazia
- Rejeita textos muito curtos ou muito longos
- Rejeita entrada com baixa densidade textual
- Aplica limiar de confianca para evitar resposta com falsa certeza

## 6. Como executar

### 6.1 Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 6.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6.3 Rodar pipeline e registrar experimento

```bash
python src/main.py
```

### 6.4 Subir MLflow UI

```bash
mlflow ui --backend-store-uri file:./mlruns --port 5000 --host 127.0.0.1
```

Acesse: http://127.0.0.1:5000

### 6.5 Rodar inferencia

```bash
python src/inference.py --text "This movie was amazing and very emotional"
```

## 7. Evidencias para o relatorio

Evidencias ja geradas no projeto:

- `docs/evidencias/01-runs.png`
- `docs/evidencias/02-run-metricas.png`
- `docs/evidencias/03-model-registry.png`
- `docs/evidencias/04-run-artifacts.png`
- `reports/confusion_matrix.png`
- `reports/predicoes_teste.csv`
- `reports/runs_comparison.csv`

Para regenerar 3 runs comparaveis:

```bash
python src/main.py
python src/main.py
python src/main.py
```

Para atualizar o comparativo CSV via script rapido:

```bash
.venv/bin/python - <<'PY'
import sys
sys.path.append('src')
import mlflow, config

mlflow.set_tracking_uri(config.TRACKING_URI)
exp = mlflow.get_experiment_by_name(config.EXPERIMENT_NAME)
runs = mlflow.search_runs([exp.experiment_id], order_by=['attributes.start_time DESC'])
cols = ['run_id','status','start_time','metrics.accuracy','metrics.precision','metrics.recall','metrics.f1','params.batch_size','params.test_size','tags.registered_model_version']
for c in cols:
	if c not in runs.columns:
		runs[c] = None
out = runs[runs['status'] == 'FINISHED'].dropna(subset=['metrics.accuracy'])[cols].head(10)
out.to_csv('reports/runs_comparison.csv', index=False)
print('reports/runs_comparison.csv atualizado')
PY
```

## 8. Checklist para PR

- [ ] Atualizar `docs/relatorio-entrega.md` com nome e matricula
- [ ] Garantir que os 4 prints estao em `docs/evidencias/`
- [ ] Garantir que `reports/runs_comparison.csv` esta atualizado
- [ ] Rodar inferencia de validacao e anexar saida no relatorio
- [ ] Revisar README e comandos de reproducao
- [ ] Abrir PR com titulo e descricao claros

## 9. Limites do exemplo

- Dataset pequeno para facilitar execucao rapida
- Sem fine-tuning
- Modelo em ingles
- Guardrails simples (baseline)

Para melhorar a nota, voce pode ampliar dataset, adicionar validacoes de dominio e incluir testes automatizados.
