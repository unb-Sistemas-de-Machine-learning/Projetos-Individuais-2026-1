# Projetos Individuais 2026/1

Repositório destinado aos **projetos individuais** da disciplina de Sistemas de Machine Learning — 2026/1.

## Como submeter seu projeto

1. **Crie uma pasta com o seu nome** na raiz deste repositório (ex: `maria-silva/`).
2. **Coloque seus projetos individuais** dentro da sua pasta, organizando cada projeto em uma subpasta se necessário.
3. **A cada submissão, abra um Pull Request** para que o trabalho seja revisado e integrado ao repositório.

## Estrutura esperada

```
Projetos-Individuais-2026-1/
├── nome-do-aluno-1/
│   ├── projeto-1/
│   └── projeto-2/
├── nome-do-aluno-2/
│   ├── projeto-1/
│   └── projeto-2/
└── ...
```

## Projetos de Machine Learning

| # | Projeto | Descrição |
|---|---------|-----------|
| 0 | [Repositório de Projetos Individual](ingrid-soares/) | Todos os projetos da Disciplina Machine Learning por Ingrid Soares |
| 1 | [Agente de IA Orientado a Problema](projeto-individual-1/) | Projetar e implementar um agente de IA funcional com foco em requisitos, arquitetura e implementação |
| 2 | [Sistema de ML com MLflow](projeto-individual-2/) | Desenvolver um sistema de ML end-to-end com MLflow para rastreamento, versionamento, deploy e observabilidade |
| 3 | [Automação com n8n e Agentes de IA](projeto-individual-3/) | Projetar e implementar um fluxo automatizado com n8n, integrando agentes de IA para decisão e orquestração |
| 4 | [Construção Auditável de Agente de IA](projeto-individual-4/) | Desenvolver um agente de IA com processo auditável: Mission Brief, 3 soluções, ADRs, evidências e Merge-Readiness Pack |

---

## Regras

- Cada aluno deve trabalhar **somente dentro da sua própria pasta**.
- Utilize nomes de pasta em **letras minúsculas e separados por hífen** (ex: `joao-souza`).
- Sempre abra um **Pull Request** para cada nova submissão — não faça push direto na branch principal.
- Siga o **padrão de Pull Request** descrito abaixo.

---

## Padrão de Pull Request

Um bom texto de Pull Request (PR) não é "bonito" — ele é **operacional**. Ele deve permitir que outra pessoa entenda rapidamente **o que foi feito, por quê, como validar e quais são os impactos**.

### Estrutura de um bom Pull Request

#### 1. Título (curto e específico)

Use verbo no imperativo e seja direto sobre a mudança.

**Exemplos:**
- `Add MLflow tracking to training pipeline`
- `Refactor data ingestion for reproducibility`
- `Fix model inference bug in API endpoint`

#### 2. Contexto / Problema

Explique **por que** esse PR existe.

> O pipeline atual não registra experimentos, dificultando reprodutibilidade e comparação de modelos.

#### 3. O que foi feito

Descreva objetivamente as mudanças. Evite narrativa longa — use bullets.

- Integração do MLflow para tracking de experimentos
- Registro de parâmetros, métricas e artefatos
- Criação de script de execução (`train.py`)
- Ajustes na estrutura do projeto

#### 4. Como testar / validar

**Isso é obrigatório.** Se não tiver isso, o PR está incompleto.

- Rodar `python train.py`
- Acessar o MLflow UI (`mlflow ui`)
- Verificar se os experimentos estão sendo registrados
- Conferir métricas no dashboard

#### 5. Impacto / Riscos

Ajuda revisores a entenderem o que pode quebrar.

- Afeta o pipeline de treinamento
- Não impacta API de inferência
- Pode alterar resultados de experimentos anteriores

#### 6. Evidências (quando aplicável)

Especialmente importante em ML: prints do MLflow, gráficos, métricas, outputs.

#### 7. Checklist (opcional, mas recomendado)

- [ ] Código testado
- [ ] Pipeline executa do início ao fim
- [ ] Experimentos registrados no MLflow
- [ ] Documentação atualizada

---

### Exemplo completo de um bom PR

```
Title: Add MLflow tracking to training pipeline

## Context
The current training pipeline does not track experiments, making it hard
to reproduce results and compare model versions.

## What was done
- Integrated MLflow for experiment tracking
- Logged parameters, metrics and artifacts
- Created training script (train.py)
- Updated project structure for modular execution

## How to test
- Run: python train.py
- Start MLflow UI: mlflow ui
- Verify experiment logs and metrics in the dashboard

## Impact
- Affects training pipeline only
- No changes to inference API

## Evidence
- MLflow logs showing registered experiments
```

---

### Erros comuns (evitar)

- "Ajustes no código"
- "Melhorias diversas"
- PR sem instrução de teste
- PR sem contexto
- PR gigante sem explicação

> **Regra de ouro:** Um bom PR permite que alguém revise **sem precisar abrir o código inteiro**.

