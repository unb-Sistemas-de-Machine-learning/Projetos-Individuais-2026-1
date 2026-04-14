# Relatório de Entrega — Projeto Individual 2: Sistema de ML com MLflow

> **Aluno(a):** Ana Luiza Soares de Carvalhoo
> **Matrícula:** 231011088
> **Data de entrega:** [DD/MM/AAAA]

---

## 1. Resumo do Projeto

_Apresente um resumo executivo do projeto (máx. 200 palavras): qual o problema escolhido, qual o modelo reutilizado e qual o principal resultado obtido._

---

## 2. Escolha do Problema, Dataset e Modelo

### 2.1 Problema

_Descreva o problema escolhido e por que ele é relevante._

### 2.2 Dataset

| Item | Descrição |
|------|-----------|
| **Nome do dataset** | Contradictory, My Dear Watson |
| **Fonte** | (Kanggle)[https://www.kaggle.com/competitions/contradictory-my-dear-watson/data] |
| **Tamanho** | 2.77 MB |
| **Tipo de dado** | csv |

### 2.3 Modelo pré-treinado

| Item | Descrição |
|------|-----------|
| **Nome do modelo** | |
| **Fonte** (ex: Hugging Face) |  |
| **Tipo** (ex: classificação, NLP) | |
| **Fine-tuning realizado?** | Sim / Não |

---

## 3. Pré-processamento

_Descreva as decisões de pré-processamento aplicadas aos dados:_

- 
- 
- 

---

## 4. Estrutura do Pipeline

_Descreva a estrutura do pipeline implementado. Inclua diagrama se possível._

```
Ingestão → Pré-processamento → Carregamento do modelo → Avaliação → Registro MLflow → Deploy
```

### Estrutura do código

```
projeto-2/
├── src/
│   ├── ...
├── data/
│   ├── ...
├── mlruns/
├── requirements.txt
└── README.md
```

---

## 5. Uso do MLflow

### 5.1 Rastreamento de experimentos

_Descreva como o MLflow foi utilizado para rastrear experimentos:_

- **Parâmetros registrados:**
- **Métricas registradas:**
- **Artefatos salvos:**

### 5.2 Versionamento e registro

_Descreva como o modelo foi versionado e registrado no MLflow._

### 5.3 Evidências

_Inclua prints da UI do MLflow ou logs mostrando os experimentos registrados._

---

## 6. Deploy

_Descreva como o modelo foi disponibilizado para inferência:_

- **Método de deploy:** (ex: MLflow serve, endpoint REST, script local)
- **Como executar inferência:**

```bash
# Exemplo de comando para inferência
```

---

## 7. Guardrails e Restrições de Uso

_Descreva os mecanismos implementados para evitar uso indevido:_

- 
- 
- 

---

## 8. Observabilidade

_Descreva como o monitoramento do sistema foi configurado:_

- **Comparação de execuções:**
- **Análise de métricas:**
- **Capacidade de inspeção:**

---

## 9. Limitações e Riscos

_Descreva as limitações do sistema e riscos identificados._

---

## 10. Como executar

_Instruções passo a passo para rodar o projeto:_

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente (se necessário)
export ...

# 3. Executar o pipeline
python src/main.py

# 4. Iniciar o MLflow UI
mlflow ui

# 5. Executar inferência
python src/inference.py
```

---

## 11. Referências

1. 
2. 
3. 

---

## 12. Checklist de entrega

- [ ] Código-fonte completo
- [ ] Pipeline funcional
- [ ] Configuração do MLflow
- [ ] Evidências de execução (logs, prints ou UI)
- [ ] Modelo registrado
- [ ] Script ou endpoint de inferência
- [ ] Relatório de entrega preenchido
- [ ] Pull Request aberto
