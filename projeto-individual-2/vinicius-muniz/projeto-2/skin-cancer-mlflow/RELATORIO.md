# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

> **Aluno(a):** Vinicius Eduardo Muniz da Silva
> **Matrícula:** 211031870
> **Data de entrega:** 15/04/2026

---

## 1. Resumo do Projeto

Sistema end-to-end de classificação de lesões dermatoscópicas em **benigna** ou
**maligna**, apoiado pelo modelo pré-treinado `Anwarkh1/Skin_Cancer-Image_Classification`
(HuggingFace). O foco é engenharia de ML Systems: pipeline modular com MLflow
para tracking, Model Registry, deploy via FastAPI e guardrails de segurança
(confiança mínima + restrição a pele clara, coerente com o viés do dataset
ISIC). Dados: 600 imagens do ISIC Archive (300 benignas, 300 malignas) com
split estratificado 70/10/20. Resultados no conjunto de teste (L* ≥ 55,
confiança ≥ 0.70): **acurácia 75%**, **F1-macro 0.75**, **ROC AUC 0.82**,
cobertura operacional 87% (13% rejeitado pelos guardrails ou marcado como
incerto — comportamento desejado). Modelo registrado no MLflow Registry como
`skin-cancer-classifier` v1 e exposto via endpoint `/predict` (FastAPI) e CLI.

---

## 2. Escolha do Problema, Dataset e Modelo

### 2.1 Problema

Classificação binária de lesões de pele (benigna vs maligna) a partir de
imagens dermatoscópicas. Relevante porque: (i) melanoma tem alta letalidade
quando detectado tarde; (ii) é o domínio sugerido pela disciplina; (iii)
sensibilidade clínica exige guardrails explícitos — terreno ideal para
exercitar ML Systems além da métrica bruta.

### 2.2 Dataset

| Item | Descrição |
|------|-----------|
| **Nome do dataset** | ISIC Archive (subconjunto) |
| **Fonte** | https://gallery.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery?filter=%5B%5D |
| **Tamanho** | 600 imagens (300 benignas + 300 malignas) |
| **Tipo de dado** | Imagens dermatoscópicas RGB (JPEG) |

### 2.3 Modelo pré-treinado

| Item | Descrição |
|------|-----------|
| **Nome do modelo** | `Anwarkh1/Skin_Cancer-Image_Classification` |
| **Fonte** | HuggingFace Hub |
| **Tipo** | Classificação de imagem (ViT, 7 classes HAM10000) |
| **Fine-tuning realizado?** | Não |

---

## 3. Pré-processamento

- **Indexação com SHA-1** (`data_ingestion.py`): cada arquivo recebe hash para
  detectar duplicatas e arquivos corrompidos; manifesto em `processed/index.csv`.
- **Relatório de qualidade** (`quality_report.json`): contagem por classe,
  duplicatas, arquivos vazios, labels desconhecidos.
- **Split estratificado** (train 70% / val 10% / test 20%) com semente fixa
  (42) para reprodutibilidade (`preprocessing.py`).
- **Filtragem por labels válidos**: apenas `benign`/`malignant` entram nos splits.
- **Redimensionamento**: delegado ao `AutoImageProcessor` do HuggingFace
  (normalização ImageNet, 224×224), garantindo consistência treino–inferência.
- **Sem augmentation**: como não há retreino, augmentations seriam ruído.

---

## 4. Estrutura do Pipeline

```
Ingestão → Pré-processamento → Download do modelo → Registro MLflow → Avaliação → Deploy
```

Orquestrado em `src/pipeline.py` com estágios independentes e executáveis
isoladamente (`--stage ingest|preprocess|download_model|register|evaluate|all`).

### Estrutura do código

```
projeto-2/skin-cancer-mlflow/
├── configs/
│   └── config.yaml              # parâmetros centralizados
├── data/
│   ├── raw/{benign,malignant}/  # imagens ISIC
│   └── processed/               # index.csv, splits, métricas
├── models/pretrained/           # snapshot local do HF
├── mlruns/                      # tracking + registry MLflow
├── src/
│   ├── config.py                # loader YAML
│   ├── data_ingestion.py        # índice + qualidade
│   ├── preprocessing.py         # splits estratificados
│   ├── guardrails.py            # L* pele + confiança mínima
│   ├── model.py                 # pyfunc wrapper
│   ├── evaluate.py              # métricas + MLflow logging
│   ├── register.py              # Model Registry
│   ├── serve.py                 # FastAPI
│   ├── predict_cli.py           # CLI humano/JSON
│   └── pipeline.py              # orquestrador
├── tests/test_guardrails.py
├── requirements.txt
├── README.md
└── RELATORIO.md
```

### Integração do modelo pré-treinado

`src/model.py` encapsula o modelo em `SkinCancerPyfunc` (`mlflow.pyfunc.PythonModel`):
`load_context` carrega processor + pesos do snapshot local; `predict` aplica
guardrails de entrada, faz forward, agrega as 7 classes em binário e aplica
guardrail de confiança. Mesmo artefato serve para avaliação, CLI e endpoint HTTP.

---

## 5. Uso do MLflow

### 5.1 Rastreamento de experimentos

Experiment: `skin-cancer-detection` em `./mlruns`.

- **Parâmetros registrados:** `hf_model_id`, `min_confidence`,
  `skin_tone_ita_min` (threshold de L*), `split`, `n_images`.
- **Métricas registradas:** `accuracy`, `f1_macro`, `precision_macro`,
  `recall_macro`, `roc_auc`, `coverage`, `n_evaluated`, `n_total`,
  `n_rejected_guardrail`, `n_uncertain`.
- **Artefatos salvos:** `predictions.csv` (predição por imagem),
  `confusion_matrix.csv`, `metrics.json` — sob `artifact_path=eval/<split>`.

### 5.2 Versionamento e registro

Três coisas são versionadas juntas para garantir reprodutibilidade:

**1. Código.** Controlado por git. `.gitignore` ignora dados brutos
(`data/raw`), snapshot do modelo (`models/pretrained`) e o próprio tracking
(`mlruns`), porque esses diretórios são reconstruíveis a partir do código
e das imagens.

**2. Dados.** Cada imagem é identificada pelo seu **SHA-1** em
`data/processed/index.csv`. Esse arquivo é um manifesto: se duas pessoas
têm o mesmo `index.csv`, têm exatamente o mesmo dataset. Mudou uma
imagem? O hash muda, o manifesto muda, fica rastreável.

**3. Modelo.** O `src/register.py` chama `mlflow.pyfunc.log_model(...)`
com `registered_model_name="skin-cancer-classifier"`. Cada execução:

  - Cria um **run** no experiment `skin-cancer-detection` (pasta em
    `mlruns/251178895474994468/<run_id>/`).
  - Empacota o modelo + processor + `config.yaml` + `requirements.txt` +
    assinatura de entrada (`path` ou `image_b64`) dentro de `artifacts/model/`.
  - Registra uma **nova versão** em `mlruns/models/skin-cancer-classifier/`
    (v1, v2, v3...). A versão aponta para o run que a criou.

Por que `config.yaml` entra no pacote: os thresholds dos guardrails
(confiança, L*) mudam o comportamento do modelo tanto quanto os pesos.
Versionar juntos evita que alguém baixe a v1 e use thresholds diferentes.

**Como ver cada versão:**

```bash
mlflow ui --backend-store-uri ./mlruns   # UI > aba "Models"
ls mlruns/models/skin-cancer-classifier/ # version-1/, version-2/, ...
```

**Como carregar uma versão específica:**

```python
import mlflow.pyfunc
model = mlflow.pyfunc.load_model("models:/skin-cancer-classifier/1")
# ou "models:/skin-cancer-classifier/latest"
```

### 5.3 Evidências

- Experiment criado: ver `mlruns/251178895474994468/`.
- Modelo registrado: `mlruns/models/skin-cancer-classifier/version-1/`.
- Runs de avaliação: `mlruns/251178895474994468/<run_id>/` com metrics.json e
  artefatos `eval/test/`.
- UI: `mlflow ui --backend-store-uri ./mlruns` → http://localhost:5000

Resultados da última run de avaliação (split test, 120 imagens):

```json
{
  "coverage": 0.87, "n_evaluated": 104, "n_total": 120,
  "n_rejected_guardrail": 6, "n_uncertain": 11,
  "accuracy": 0.75, "f1_macro": 0.75,
  "precision_macro": 0.75, "recall_macro": 0.75, "roc_auc": 0.82
}
```

---

## 6. Deploy

- **Método de deploy:** (1) FastAPI (`src/serve.py`) que carrega do Registry
  (`MODEL_STAGE`/`MODEL_VERSION` via env, fallback para pyfunc local); (2)
  CLI (`src/predict_cli.py`); (3) `mlflow models serve` direto do Registry.

- **Como executar inferência:**

```bash
# (A) CLI — saída humana
python -m src.predict_cli /caminho/para/imagem.jpg

# (B) CLI — JSON detalhado
python -m src.predict_cli /caminho/para/imagem.jpg --json

# (C) FastAPI
python -m src.serve        # sobe em http://localhost:8000
curl -F "file=@imagem.jpg" http://localhost:8000/predict

# (D) MLflow serve (direto do Registry)
mlflow models serve -m "models:/skin-cancer-classifier/latest" -p 5001 --no-conda
```

---

## 7. Guardrails e Restrições de Uso

Implementados em `src/guardrails.py`, embutidos no pyfunc, no CLI e no endpoint:

- **Limiar de confiança (0.70):** predições abaixo retornam `decision="uncertain"`
  com mensagem recomendando avaliação médica — evita falsa confiança.
- **Restrição de tom de pele (L* ≥ 55):** imagens cujo L* mediano da borda
  (pele saudável) é baixo são rejeitadas, explicitando que o ISIC tem
  representação predominantemente de pele clara (Fitzpatrick I–III).
  Implementação usa L* (CIE Lab) em vez de ITA clássico porque a iluminação
  polarizada da dermatoscopia satura o canal b*, tornando ITA instável.
- **Validação de arquivo:** tamanho ≤ 10 MB, formatos `jpg/jpeg/png`,
  integridade verificada com `PIL.verify()`.
- **Disclaimer médico obrigatório** em toda resposta: ferramenta educacional,
  não substitui avaliação clínica.

---

## 8. Observabilidade

- **Comparação de execuções:** MLflow UI permite comparar runs variando
  threshold de confiança e L* — params/metrics lado a lado em
  `http://localhost:5000`.
- **Análise de métricas:** além de qualidade (accuracy/F1/AUC), métricas
  operacionais (`coverage`, `n_rejected_guardrail`, `n_uncertain`) sinalizam
  desvio de distribuição (ex: drop de coverage → imagens fora do domínio).
- **Capacidade de inspeção:** `predictions.csv` logado como artefato permite
  análise caso a caso (prob por classe, L*, decisão). Logs estruturados em
  `serve.py` registram decisão por request (`logger.info("predict result=...")`).
- **Matriz de confusão** salva como artefato para cada execução de avaliação.

---

## 9. Limitações e Riscos

- **Viés racial do dataset:** ISIC é enviesado para pele clara; o guardrail
  explicita a restrição mas não resolve — usuários com pele escura não são
  atendidos. Mitigação futura: incorporar Fitzpatrick17k ou DDI.
- **Não é diagnóstico médico:** ferramenta educacional; decisões clínicas
  exigem triagem humana.
- **Proxy L* aproximado:** detecta tom da moldura; com zoom extremo na lesão
  pode rejeitar pele clara legítima (comportamento conservador, falso positivo
  na rejeição).
- **Generalização fora do ISIC:** iluminação/dispositivo afetam predições;
  sem dados de produção para calibrar.
- **Sem fine-tuning:** acurácia limitada ao checkpoint público (~75%); não
  atinge estado-da-arte clínico.
- **Sem monitoramento contínuo em produção:** apenas logs por request; não há
  job automatizado detectando drift.
- **Desbalanceamento real:** em população geral, prevalência de malignidade é
  muito menor que 50% — métrica agregada não reflete cenário clínico.

---

## 10. Como executar

```bash
# 1. Ir para a pasta e criar venv
cd projeto-2/skin-cancer-mlflow
python -m venv .venv && source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Colocar imagens ISIC em:
#    data/raw/benign/    (300+ imagens)
#    data/raw/malignant/ (300+ imagens)

# 4. Rodar pipeline completo
python -m src.pipeline --stage all

# 5. Abrir MLflow UI
mlflow ui --backend-store-uri ./mlruns     # http://localhost:5000

# 6. Inferência — CLI
python -m src.predict_cli /caminho/imagem.jpg

# 7. Inferência — API
python -m src.serve
curl -F "file=@/caminho/imagem.jpg" http://localhost:8000/predict

# 8. Testes
pytest tests/
```

Estágios individuais: `--stage ingest|preprocess|download_model|register|evaluate`.

---

## 11. Referências

1. ISIC Archive — https://gallery.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery?filter=%5B%5D
2. Anwarkh1, *Skin_Cancer-Image_Classification* (HuggingFace) — https://huggingface.co/Anwarkh1/Skin_Cancer-Image_Classification
3. Tschandl et al., *The HAM10000 dataset* (Scientific Data, 2018).
4. Del Bino et al., *Variations in skin colour and the amount of constitutive melanin* (Pigment Cell Melanoma Res., 2015) — base conceitual para uso de L*/ITA.
5. MLflow Documentation — https://mlflow.org/docs/latest/
6. HuggingFace Transformers — https://huggingface.co/docs/transformers

---

## 12. Checklist de entrega

- [x] Código-fonte completo (`src/`, `tests/`, `configs/`)
- [x] Pipeline funcional (`src/pipeline.py`, todos os estágios rodam)
- [x] Configuração do MLflow (`mlruns/`, experiment + registry populados)
- [x] Evidências de execução (métricas logadas, artefatos em `mlruns/`)
- [x] Modelo registrado (`skin-cancer-classifier` v1)
- [x] Script ou endpoint de inferência (`predict_cli.py` + `serve.py`)
- [x] Relatório de entrega preenchido (este arquivo)
- [x] Pull Request aberto
