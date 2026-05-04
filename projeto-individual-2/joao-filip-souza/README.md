# Sistema de ML com MLflow - Classificação de Animais CIFAR-10

Este projeto implementa um sistema end-to-end de machine learning para classificação de imagens de **animais** usando o dataset CIFAR-10, com foco em ML Systems e rastreamento via MLflow.

## Estrutura do Projeto

```
joao-filip-souza/
├── data/
│   ├── raw/          # Dados brutos baixados
│   └── processed/    # Dados processados
├── mlruns/           # Resultados do MLflow
├── img_teste/        # Imagens de teste para inferência
├── src/
│   ├── data/
│   │   ├── ingestion.py      # Download do dataset
│   │   └── preprocessing.py  # Pré-processamento (filtra apenas animais)
│   ├── model/
│   │   ├── model_loading.py  # Carregamento do ResNet18
│   │   ├── training.py       # Fine-tuning do modelo
│   │   ├── evaluation.py     # Avaliação do modelo
│   │   ├── predict.py        # Função de predição
│   │   └── model_registry.py # Registro no MLflow Model Registry
│   ├── guardrails/
│   │   └── validation.py     # Validações e guardrails
│   ├── pipeline/
│   │   └── run_pipeline.py   # Pipeline principal
│   └── inference.py          # Script de deploy/inferência
├── requirements.txt
└── README.md
```

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

### Pipeline Completo
```bash
python3 -m src.pipeline.run_pipeline
```

### Inferência
```bash
# Tensor aleatório
PYTHONPATH=. python3 src/inference.py --input_tensor random

# Imagem específica (exemplo)
PYTHONPATH=. python3 src/inference.py --input_tensor img_teste/IMG_7878.JPG

# Tensor salvo
PYTHONPATH=. python3 src/inference.py --input_tensor /caminho/para/tensor.pt
```

### MLflow UI
```bash
mlflow ui
```

## Funcionalidades

- **Ingestão de Dados**: Download automático do CIFAR-10
- **Pré-processamento**: Filtragem para **classes de animais apenas** (bird, cat, deer, dog, frog, horse), redimensionamento
- **Modelo**: ResNet18 pré-treinado (PyTorch)
- **Avaliação**: Métricas de acurácia e precisão
- **MLflow**: Rastreamento completo de experimentos
- **Guardrails**: Validações de entrada e confiança
- **Deploy**: Script de inferência via MLflow

## Guardrails Implementados

- Validação de formato da imagem
- Verificação de confiança da predição
- **Controle de domínio**: Modelo treinado apenas com classes de animais (sempre dentro do domínio esperado)
- Limitação de tamanho de entrada

## Limitações

- Modelo pré-treinado pode não ser otimizado para CIFAR-10
- Avaliação limitada a subset pequeno
- Não inclui fine-tuning do modelo
- Interface de usuário básica (linha de comando)