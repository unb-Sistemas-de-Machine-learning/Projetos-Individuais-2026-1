# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

> **Aluno(a):** João Filipe de Oliveira Souza
> **Matrícula:** 231035141
> **Data de entrega:** 15/04/2026

## 1. Resumo do Projeto

Este projeto implementa um sistema de machine learning end-to-end para classificação de imagens de animais utilizando o dataset CIFAR-10 e o modelo ResNet18 pré-treinado. O foco principal está na engenharia do pipeline de ML, incluindo ingestão de dados, pré-processamento, avaliação, registro no MLflow e deploy para inferência, com ênfase em boas práticas de ML Systems.

## 2. Escolha do Problema, Dataset e Modelo

### 2.1 Problema

O problema escolhido é a classificação de imagens em 6 classes de animais (pássaros, gatos, cervos, cachorros, sapos e cavalos) do dataset CIFAR-10. Este é um problema clássico de visão computacional que permite demonstrar um pipeline completo de ML sem a necessidade de treinar modelos do zero.

### 2.2 Dataset

| Item | Descrição |
|------|-----------|
| **Nome do dataset** | CIFAR-10 |
| **Fonte** | torchvision.datasets.CIFAR10 |
| **Tamanho** | 60.000 imagens ao todo, quando filtrada tem 30.000 (21.000 treino, 9.000 teste) |
| **Tipo de dado** | Imagens RGB 32x32 pixels |

### 2.3 Modelo pré-treinado

| Item | Descrição |
|------|-----------|
| **Nome do modelo** | ResNet18 |
| **Fonte** | torchvision.models.resnet18 (pretrained=True) |
| **Tipo** | Classificação de imagens (1000 classes ImageNet) |
| **Fine-tuning realizado?** | Sim |

## 3. Pré-processamento

- Redimensionamento das imagens de 32x32 para 224x224 pixels
- Aplicação de transformações ToTensor() para conversão em tensores PyTorch
- Filtragem do dataset para manter apenas as classes de animais (índices 2-7)
- Normalização implícita através do modelo pré-treinado

## 4. Estrutura do Pipeline

O pipeline segue uma arquitetura modular e reprodutível:

```
Ingestão → Pré-processamento → Carregamento do Modelo -> Fine Tunning → Avaliação → Registro MLflow → Inferência
```

### Estrutura do código

```
joao-filip-souza/
├── data/
│   ├── raw/          # Dados brutos baixados
│   └── processed/    # Dados processados
├── mlruns/           # Resultados e runs do MLflow
├── img_teste/        # Imagens de teste para inferência
├── src/
│   ├── data/
│   │   ├── ingestion.py      # Download e carregamento do CIFAR-10
│   │   └── preprocessing.py  # Transformações e filtragem
│   ├── model/
│   │   ├── model_loading.py     # Carregamento do ResNet18 pré-treinado
│   │   ├── training.py          # Fine-tuning do modelo
│   │   ├── evaluation.py        # Avaliação de desempenho
│   │   ├── predict.py           # Função de predição
│   │   └── model_registry.py    # Registro no MLflow Model Registry
│   ├── guardrails/
│   │   └── validation.py     # Validações de segurança e restrições
│   ├── pipeline/
│   │   └── run_pipeline.py   # Orquestração principal do pipeline
│   └── inference.py          # Script de deploy/inferência
├── requirements.txt
└── README.md
```

---

## 5. Uso do MLflow

### 5.1 Rastreamento de experimentos

O MLflow é utilizado para rastrear todos os aspectos do pipeline:

- **Parâmetros registrados:**
  - dataset: "CIFAR-10"
  - model: "ResNet18"
  - classes: "bird, cat, deer, dog, frog, horse"
  - dataset_size: tamanho total do dataset
  - filtered_classes: número de classes após filtragem
  - filtered_samples: número de amostras após filtragem

- **Métricas registradas:**
  - accuracy: acurácia no subset de teste
  - precision: precisão macro no subset de teste
  - mean_confidence: confiança média das predições

- **Artefatos salvos:**
  - Modelo PyTorch completo (mlflow.pytorch.log_model)

### 5.2 Versionamento e registro

O modelo é registrado automaticamente no MLflow Model Registry após cada execução do pipeline, permitindo versionamento automático e deploy consistente.

### 5.3 Evidências

Após executar o pipeline, inicie a UI do MLflow:

```bash
mlflow ui
```

Acesse http://localhost:5000 para visualizar:
- Experimentos registrados
- Parâmetros e métricas de cada run
- Modelos versionados
- Artefatos salvos

---

## 6. Deploy

O deploy é realizado através de um script Python que carrega o modelo do MLflow e executa inferência:

```bash
PYTHONPATH=. python3 src/inference.py --input_tensor random
```

O script:
- Carrega automaticamente a última/melhor versão do modelo registrado
- Aplica todas as validações de guardrails

---

## 7. Guardrails e Restrições de Uso

Foram implementados múltiplos mecanismos de segurança:

- **Validação de imagem**: Verifica formato do tensor (1, 3, H, W) e range de valores
- **Validação de confiança**: Rejeita predições com confiança < 0.5
- **Validação de domínio**: Alerta quando predição não é de animal
- **Limitação de entrada**: Controle de tamanho máximo da entrada
- **Tratamento de erros**: Mensagens claras para diferentes tipos de falha

Estes guardrails previnem uso indevido e garantem que o modelo só seja usado dentro do escopo esperado.

---

## 8. Observabilidade

O sistema oferece observabilidade completa através do MLflow:

- **Comparação de execuções**: Interface web permite comparar métricas entre runs
- **Análise de métricas**: Gráficos de acurácia, precisão e confiança ao longo do tempo
- **Capacidade de inspeção**: Logs detalhados de cada etapa do pipeline
- **Rastreamento de versão**: Histórico completo de mudanças no modelo e dados

---

## 9. Limitações e Riscos

- **Modelo pré-treinado**: ResNet18 foi treinado no ImageNet, necessita adaptação para CIFAR-10
- **Avaliação limitada**: Teste em subset do dataset CIFAR-10 para demonstração
- **Fine-tuning limitado**: Modelo adaptado para as 6 classes de animais especificadas
- **Dependência de PyTorch**: Sistema limitado a ecossistema PyTorch
- **Riscos de domínio**: Modelo pode falhar em imagens fora do domínio CIFAR-10 ou que não sejam dos animais especificados

---

## 10. Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o pipeline completo
python -m src.pipeline.run_pipeline

# 3. Iniciar MLflow UI para observabilidade
mlflow ui

# 4. Executar inferência de exemplo
PYTHONPATH=. python3 src/inference.py --input_tensor random

# 5. Verificar logs e métricas no navegador (http://localhost:5000)
```