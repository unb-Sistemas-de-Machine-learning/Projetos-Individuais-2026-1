# Projeto Individual 3 — Entrega Final

## Identificação

- **Aluno(a):** Patricia Helena Macedo da Silva
- **Matrícula:** 221037993
- **Tema:** Triagem automática de suporte técnico com n8n e IA

---

## 1. Objetivo do projeto

Implementar uma automação no **n8n** que receba chamados de suporte técnico, use IA para classificação e decisão, aplique roteamento condicional e registre tudo para auditoria.

Fluxo macro esperado:

`Entrada -> IA classifica -> decisão -> ação`

---

## 2. Solução final escolhida

A solução final adotada foi a **Solução B**:

- classificação por IA;
- recuperação de FAQ no Google Sheets (RAG leve);
- geração de orientação contextual em segunda chamada de IA;
- roteamento condicional (`auto`, `revisao`, `escala`);
- persistência na aba `Tickets`.

Referência da decisão:

- `docs/adr/001-escolha-da-solucao.md`

---

## 3. Estrutura do projeto (entrega)

```text
projeto-3/
├── agent.md
├── docs/
│   ├── mission-brief.md
│   ├── mentorship-pack.md
│   ├── workflow-runbook.md
│   ├── merge-readiness-pack.md
│   ├── relatorio-entrega.md
│   ├── adr/
│   │   └── 001-escolha-da-solucao.md
│   └── evidence/
├── solutions/
│   ├── solution-a/
│   │   └── README.md
│   ├── solution-b/
│   │   └── README.md
│   └── solution-c/
│       └── README.md
├── src/workflows/
│   ├── solution-a-prompt-simples.json
│   ├── solution-b-faq-sheets.json
│   └── solution-c-multietapas.json
├── tests/
│   └── casos-de-teste.md
└── README.md
```

---

## 4. Três soluções implementadas

### Solução A — Prompt único + roteamento

- Uma chamada de IA para classificação estruturada.
- Roteamento por `Switch`.
- Persistência em planilha.

Arquivo:

- `src/workflows/solution-a-prompt-simples.json`

### Solução B — RAG leve com FAQ (escolhida)

- IA classifica chamado.
- FAQ é lido no Google Sheets.
- IA gera orientação com contexto recuperado.
- Roteamento e persistência.

Arquivo:

- `src/workflows/solution-b-faq-sheets.json`

### Solução C — Multi-etapas

- IA 1 classifica.
- IA 2 redige orientação.
- Regra de validação define rota final.

Arquivo:

- `src/workflows/solution-c-multietapas.json`

---

## 5. Tecnologias e integrações

- **n8n** (orquestração)
- **Google Gemini API** (`gemini-2.5-flash`) para classificação e geração
- **Google Sheets** para FAQ e auditoria de tickets
- **Webhook HTTP** para entrada de chamadas

---

## 6. Como executar (resumo)

1. Importar `src/workflows/solution-b-faq-sheets.json` no n8n.
2. Configurar Gemini (`x-goog-api-key`) nos nós HTTP.
3. Configurar Google Sheets (OAuth2 + `Document ID`).
4. Garantir abas:
  - `FAQ` (`titulo`, `resposta`)
  - `Tickets` (`timestamp`, `email`, `mensagem`, `categoria`, `urgencia`, `confianca`, `rota`, `resumo`, `orientacao`)
5. Executar webhook via `POST` com JSON contendo `message` (e opcionalmente `email`).

---

## 7. Evidências

As evidências de execução e teste estão em:

- `docs/evidence/`

---

## 8. Documentos principais da entrega

- Mission Brief: `docs/mission-brief.md`
- Agent: `agent.md`
- Mentorship Pack: `docs/mentorship-pack.md`
- Workflow Runbook: `docs/workflow-runbook.md`
- ADR da escolha final: `docs/adr/001-escolha-da-solucao.md`
- Merge Readiness: `docs/merge-readiness-pack.md`
- Relatório técnico: `docs/relatorio-entrega.md`

---

## 9. Status final

- Três soluções implementadas/documentadas (A/B/C)
- Solução final escolhida e justificada (B)
- Testes e casos de teste documentados
- Evidências referenciadas
- Documentação técnica completa
- PR final (conforme fluxo da disciplina)

