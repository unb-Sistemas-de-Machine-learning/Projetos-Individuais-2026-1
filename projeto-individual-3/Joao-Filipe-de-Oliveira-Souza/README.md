# Sistema de Triagem Automatica de Demandas Academicas

Projeto de automacao com n8n e agente de IA para classificar demandas, estimar urgencia e encaminhar para o time responsavel com rastreabilidade.

## Objetivo

Automatizar a triagem inicial de solicitacoes em texto livre, reduzindo tempo de resposta e erros de encaminhamento.

## Fluxo implementado

```text
Formulario -> Preparar contexto -> Agente classificador -> Validacao de confianca -> Persistencia -> Roteamento por urgencia -> Acao de saida
```

## Arquitetura (workflow n8n)

Workflow principal: `src/workflows/Sistema de Triagem Automática de Demandas-2.json`

Nos principais:

- `Formulário de Demanda`: coleta nome, email, assunto e descricao.
- `Preparar Contexto para IA`: consolida dados para inferencia.
- `Agente Classificador` + `OpenAI GPT-5 Mini` + `Parser de Classificação`: classifica e retorna JSON estruturado.
- `Verificar Confiança da IA`: aplica limiar de confianca (`>= 0.70`).
- `Armazenar Demanda`: persiste campos de auditoria.
- `Rotear por Urgência`: direciona para alta, media ou baixa urgencia.
- `Enviar email - alta prioridade` / `Enviar Email - Média Urgência`: acao para casos de maior prioridade.

## Regras de decisao

- Se `confianca >= 0.70`: usa `categoria` e `urgencia` previstas pela IA.
- Se `confianca < 0.70`: aplica fallback para `categoria_final = outro` e `urgencia_final = media`.

## Integracoes

- OpenAI (classificacao por IA)
- Gmail (encaminhamento por email)
- n8n Data Table (persistencia de trilha)

## Estrutura do projeto

```text
.
├── agent.md
├── docs/
│   ├── README.md
│   ├── mission-brief.md
│   ├── mentorship-pack.md
│   ├── workflow-runbook.md
│   ├── merge-readiness-pack.md
│   ├── adr/
│   │   └── 001-escolha-da-solucao.md
│   └── evidence/
│       ├── README.md
│       └── evidence-log.md
├── solutions/
│   ├── solution-a/
│   │   ├── README.md
│   │   └── prompt-template.md
│   ├── solution-b/
│   │   ├── README.md
│   │   ├── prompt-template.md
│   │   └── kb/
│   │       └── politicas.md
│   └── solution-c/
│       └── README.md
├── src/
│   └── workflows/
│       └── Sistema de Triagem Automática de Demandas-2.json
├── tests/
│   ├── README.md
│   └── casos-teste-triagem.csv
└── relatorio-entrega.md
```

## Como executar

1. Abrir o n8n.
2. Importar `src/workflows/Sistema de Triagem Automática de Demandas-2.json`.
3. Configurar credenciais do OpenAI e Gmail no n8n.
4. Ativar o workflow e enviar uma demanda pelo formulario.
5. Validar rota executada e dados persistidos no Data Table.

## Documentacao de engenharia

- Mission brief: `docs/mission-brief.md`
- Mentorship pack: `docs/mentorship-pack.md`
- Workflow runbook: `docs/workflow-runbook.md`
- Merge readiness: `docs/merge-readiness-pack.md`
- ADR de decisao: `docs/adr/001-escolha-da-solucao.md`
- Evidencias: `docs/evidence/README.md`

## Alternativas de solucao

- `solutions/solution-a/`: abordagem de prompt unico.
- `solutions/solution-b/`: abordagem com base de conhecimento.
- `solutions/solution-c/`: pipeline multi-etapas (solucao final).

## Testes

- Matriz de testes: `tests/casos-teste-triagem.csv`
- Procedimento de execucao: `tests/README.md`
- Registro de evidencias: `docs/evidence/evidence-log.md`

## Status da entrega

- Workflow funcional exportado.
- Relatorio tecnico preenchido.
- Artefatos obrigatorios em `docs/` preenchidos.
- Estrutura de `solutions/` criada com tres alternativas documentadas.
- Testes manuais e log de evidencias estruturados.

