# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

> **Alunos:** Felipe Amorim de Araujo e Gabryel Nicolas Soares de Sousa 
> **Matrícula:** 2210/221022570  
> **Data de entrega:** 15/04/2026  

---

## 1. Resumo do Projeto

Este projeto implementa um pipeline de Machine Learning end-to-end para detecção de objetos astronômicos estrelas, galáxias e quasares em imagens do céu provenientes do Sloan Digital Sky Survey (SDSS). O sistema reutiliza o modelo pré-treinado YOLOS-small (hustvl/yolos-small, Hugging Face) como detector genérico de bounding boxes, aproveitando sua capacidade de localização espacial sem remapear as classes do dataset COCO original. O pipeline abrange ingestão automática de imagens via API do SDSS, pré-processamento com arcsinh stretch, guardrails, rastreamento com MLflow, registro no Model Registry e deploy via mlflow serve. Também há um módulo opcional de fine-tuning com anotações automáticas. O foco está na engenharia do sistema, com rastreabilidade e observabilidade completas.

---

## 2. Escolha do Problema, Dataset e Modelo

### 2.1 Problema

Detecção de objetos em imagens astronômicas do SDSS. O sistema identifica e delimita objetos celestes com bounding boxes.

Relevância:
- Alto volume de imagens impossibilita análise manual
- Modelos modernos não são amplamente testados nesse domínio
- Desafio técnico devido à gama dinâmica das imagens

### 2.2 Dataset

| Item | Descrição |
|------|----------|
| **Nome do dataset** | SDSS DR17 |
| **Fonte** | https://skyserver.sdss.org |
| **Tamanho** | 20 a 150 regiões (imagens 640x640) |
| **Tipo de dado** | Imagens RGB + catálogo astronômico |

### 2.3 Modelo pré-treinado

| Item | Descrição |
|------|----------|
| **Nome do modelo** | hustvl/yolos-small |
| **Fonte** | Hugging Face |
| **Tipo** | Detecção de objetos |
| **Fine-tuning realizado?** | Sim (opcional) |

---

## 3. Pré-processamento

- Arcsinh stretch para compressão de faixa dinâmica
- Conversão para RGB
- Resize automático via YolosImageProcessor
- Filtragem de objetos com magnitude alta (ruído)

---

## 4. Estrutura do Pipeline
    Ingestão → Pré-processamento → Modelo → Avaliação → MLflow → Deploy

### Estrutura do código
    felipe-amorim-de-araujo/
    ├── src/
    │   ├── __init__.py
    │   ├── data/
    │   │   ├── __init__.py
    │   │   ├── ingest.py
    │   │   └── preprocess.py
    │   ├── model/
    │   │   ├── __init__.py
    │   │   ├── detector.py
    │   │   └── guardrails.py
    │   ├── pipeline.py
    │   └── inference.py
    ├── tests/
    │   ├── data/
    │   │   ├── test_ingest.py
    │   │   └── test_preprocess.py
    │   ├── model/
    │   │   ├── test_detector.py
    │   │   └── test_guardrails.py
    │   └── test_pipeline.py
    ├── data/
    │   ├── raw/
    │   └── processed/
    ├── mlruns/
    ├── pyproject.toml
    └── README.md

---

## 5. Uso do MLflow

### 5.1 Rastreamento de experimentos

- **Parâmetros registrados:**
  - n_regions
  - confidence_threshold
  - model_name

- **Métricas registradas:**
  - detection_rate
  - inference_time
  - confidence stats

- **Artefatos salvos:**
  - detections.json
  - imagens anotadas
  - modelo treinado

### 5.2 Versionamento e registro

Modelo registrado como **space-detector** no MLflow Model Registry, com versionamento automático por execução.

### 5.3 Evidências

*(Inserir prints da UI do MLflow)*

---

## 6. Deploy

- **Método de deploy:** MLflow serve (endpoint REST local)

```bash
# Iniciar o servidor
mlflow models serve -m "models:/space-detector/1" --port 5001 --no-conda
```
- **Como executar inferência:** 
```bash
python -m src.inference --image data/raw/field_0000.jpg --endpoint http://localhost:5001 
```


## 7. Guardrails e Restrições de Uso

- **Validação de entrada:**
  - Apenas imagens RGB
  - Dimensões entre 100px e 4096px
  - Rejeição de imagens muito escuras (média < 2)
  - Rejeição de imagens superexpostas (média > 250)

- **Validação de saída:**
  - Filtro por confiança (threshold padrão: 0.4)
  - Remoção de bounding boxes muito grandes (>25% da imagem)
  - Alertas para:
    - nenhuma detecção
    - muitas detecções (>150)

---

## 8. Observabilidade

- Comparação de execuções via MLflow UI
- Métricas por imagem (step metrics)
- Inspeção via artefatos:
  - `detections.json`
  - imagens anotadas
- Rastreabilidade por versão de modelo e commit

---

## 9. Limitações e Riscos

- Transferência de domínio (modelo treinado no COCO)
- Dependência da API do SDSS e Hugging Face
- Dificuldade com objetos muito pequenos
- Ausência de métricas supervisionadas (mAP)
- Pipeline não escalável (processamento sequencial)

---

## 10. Como executar

```bash id="6q8c5m"
# 1. Instalar dependências
uv sync

# 2. Executar o pipeline
uv run python -m src.pipeline --n-regions 5 --confidence-threshold 0.4

# 3. Iniciar MLflow UI
uv run mlflow ui --port 5000

# 4. Servir modelo
uv run mlflow models serve -m "models:/space-detector/1" --port 5001 --no-conda

# 5. Executar inferência
uv run python -m src.inference --image data/raw/field_0000.jpg

# 6. Rodar testes
uv run pytest tests/ -v

## 11. Referências

1. Fang, Y. et al. (2021). YOLOS: You Only Look at One Sequence. arXiv:2106.00666.  
2. SDSS Collaboration. SDSS Data Release 17. https://www.sdss.org/dr17/  
3. Hugging Face. hustvl/yolos-small model card. https://huggingface.co/hustvl/yolos-small  
4. MLflow Documentation. https://mlflow.org/docs/latest/index.html  
5. Lupton, R. et al. (2004). Preparing Red-Green-Blue Images from CCD Data (arcsinh stretch).  

---

## 12. Checklist de entrega

- [] Código-fonte completo  
- [] Pipeline funcional  
- [] Configuração do MLflow  
- [] Evidências de execução  
- [] Modelo registrado  
- [] Script ou endpoint de inferência  
- [] Relatório de entrega preenchido  
- [] Pull Request aberto  