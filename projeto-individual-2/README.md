# Projeto Individual 2: Sistema de ML com MLflow (ML Systems)

## Objetivo

Desenvolver um **sistema de machine learning end-to-end**, com foco em **ML Systems**, utilizando a ferramenta MLflow para rastreamento de experimentos, versionamento, registro, deploy e observabilidade.

O foco principal da atividade está na **engenharia do pipeline**, e não na construção de modelos do zero.

O projeto pode ser feito em grupos de até 3 pessoas


## Contexto do problema (flexível)

O estudante pode escolher livremente o contexto da aplicação.

Um exemplo sugerido é detecção/classificação de câncer de pele utilizando:

- Dados do [ISIC Archive](https://www.isic-archive.com/)
- Modelos do Hugging Face, como o modelo *VRJBro/skin-cancer-detection*

> **Importante:** O contexto de câncer de pele é **apenas ilustrativo**. O estudante pode escolher:
>
> - Outro problema (ex: NLP, classificação de texto, recomendação, detecção de fraude, etc.)
> - Outro dataset
> - Outro modelo pré-treinado
>
> Desde que mantenha o foco em **ML Systems + MLflow**.



## Escopo do trabalho

O sistema deve conter, no mínimo:

### 1. Aquisição e preparação dos dados

- Escolha e documentação do dataset
- Pré-processamento
- Particionamento
- Tratamento de qualidade dos dados



### 2. Reuso de modelo pré-treinado (obrigatório)

- Utilizar um modelo já treinado (ex: Hugging Face)
- Integrar o modelo ao pipeline
- Opcional: realizar fine-tuning ou adaptação

> **Não é permitido treinar modelo do zero.**



### 3. Rastreamento de experimentos

Uso do MLflow para registrar:

- Parâmetros
- Métricas
- Artefatos
- Versões



### 4. Pipeline de versionamento e deploy

O pipeline deve contemplar:

- Ingestão de dados
- Pré-processamento
- Carregamento do modelo
- (Opcional) retreinamento/fine-tuning
- Avaliação
- Registro no MLflow
- Deploy para inferência

Deve evidenciar:

- **Versionamento** (dados, código e modelo)
- **Reprodutibilidade**
- **Organização modular**

---

### 5. Guardrails e restrições de uso

Implementar mecanismos para evitar uso indevido do modelo.

Exemplos:

- Recusar inferência fora do escopo do dataset
- Evitar respostas com falsa confiança
- Explicitar limitações

> Em domínios sensíveis (ex: saúde), isso é **obrigatório**.



### 6. Observabilidade

- Configurar monitoramento via MLflow
- Comparar execuções
- Analisar métricas e artefatos
- Demonstrar capacidade de inspeção do sistema



## Entregas obrigatórias

- Código-fonte completo
- Pipeline funcional
- Configuração do MLflow
- Evidências de execução (logs, prints ou UI)
- Modelo registrado
- Script ou endpoint de inferência



## Relatório técnico

O relatório deve justificar:

- Escolha do problema, dataset e modelo
- Decisões de pré-processamento
- Integração do modelo pré-treinado
- Estrutura do pipeline
- Uso do MLflow
- Versionamento
- Deploy
- Guardrails
- Observabilidade
- Limitações e riscos

> Utilize o template disponível em [`templates/relatorio-entrega.md`](templates/relatorio-entrega.md)



## Critério central de avaliação

> O principal critério é a **qualidade da engenharia do sistema de ML**.

### Será mais bem avaliado:

- Pipeline bem estruturado
- Uso consistente de MLflow
- Boas práticas de versionamento
- Presença de guardrails
- Observabilidade clara

### Do que:

- Modelos complexos sem engenharia adequada



## Critérios de Avaliação

| Critério | Peso |
|----------|------|
| Pipeline (estrutura, modularidade, reprodutibilidade) | 40% |
| Uso do MLflow (rastreamento, registro, versionamento) | 25% |
| Guardrails e restrições de uso | 15% |
| Observabilidade e monitoramento | 10% |
| Relatório técnico e documentação | 10% |


## Como submeter

**Data limite de entrega: 15/04/2026**

1. Dentro da  pasta `projeto-2/`, crie uma subpasta com o nome do seu projeto
2. Coloque todos os entregáveis dentro dessa subpasta
3. Abra um **Pull Request** para submissão
