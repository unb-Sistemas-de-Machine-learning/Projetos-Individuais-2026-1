# Projeto 3 — Automação Inteligente de Emissão de Notas Fiscais

> **Aluno:** Guilherme Westphall
> **Matrícula:** 211061805
> **Domínio:** Automação de processo financeiro recorrente com agentes de IA e aprovação humana

---

## Problema escolhido

Prestadores de serviço que faturam por hora precisam emitir notas fiscais duas vezes por mês. O processo manual envolve consultar horas registradas no Productive.io, calcular o total, preparar um e-mail profissional e enviá-lo ao contratante — um fluxo repetitivo e sujeito a erros e esquecimentos.

Esta automação elimina as etapas manuais de consulta, cálculo e redação, mantendo o controle humano sobre o momento e o conteúdo do envio por meio de aprovação explícita via Telegram.

---

## Solução final (Solution C — dois agentes)

O fluxo é orquestrado no n8n e usa dois agentes de IA independentes:

- **Agente Rascunhador**: recebe os dados consolidados da nota e gera o rascunho do e-mail ao contratante e a mensagem interna de aprovação.
- **Agente Revisor**: valida o rascunho quanto a tom, profissionalismo e ausência de dados internos sigilosos ou conteúdo inadequado.

Após a revisão pelos agentes, o prestador recebe a mensagem no Telegram e decide se aprova, rejeita ou solicita alterações com o comando `edit`. Somente após aprovação explícita o e-mail é enviado pelo Gmail.

```text
Schedule/Telegram Trigger
→ Calcular período de faturamento
→ Buscar entradas no Productive.io (HTTP Request)
→ Consolidar horas e calcular valor (Code)
→ Agente Rascunhador (Ollama): gera rascunho e mensagem de aprovação
→ Agente Revisor (Ollama): valida tom, conteúdo e conformidade
→ Switch: recommended_action
   → request_approval → Telegram: aprovação humana (approve / reject / edit)
      → approve → Gmail: enviar e-mail + Google Drive: registrar
      → edit → Agente Revisor: revisar e reapresentar
      → reject → registrar rejeição
   → needs_manual_review → Telegram: alerta de revisão manual
   → stop → registrar e encerrar
```

---

## Integrações externas

| Serviço | Finalidade |
|---------|-----------|
| Productive.io | Fonte das entradas de tempo, consultadas via API REST |
| Ollama (local) | Modelo de linguagem para os dois agentes de IA |
| Telegram | Aprovação humana e controle do fluxo (approve / reject / edit) |
| Gmail | Envio do e-mail com a nota fiscal ao contratante |
| Google Drive | Registro dos rascunhos aprovados e log de auditoria |

---

## Como a IA influencia o fluxo

Os agentes retornam um JSON estruturado com o campo `recommended_action`, que determina o caminho seguido pelo workflow:

- `request_approval` → fluxo solicita aprovação humana via Telegram
- `needs_manual_review` → fluxo alerta para revisão manual
- `stop` → fluxo interrompe e registra o motivo

O Agente Revisor adiciona uma segunda camada: seu `review_status` (`approved` ou `needs_revision`) pode reter o rascunho antes mesmo de chegar ao Telegram. O comando `edit` no Telegram realimenta o Revisor para uma nova rodada de revisão.

---

## Workflows exportados

| Arquivo | Solução | Descrição |
|---------|---------|-----------|
| `automation-invoice-two-agent-review-ngrok.json` | **Solution C (final)** | Dois agentes: Rascunhador e Revisor, com suporte ao comando `edit` |
| `automation-invoice-complete-ngrok.json` | Solution A (baseline) | Agente único com validação e aprovação humana |

---

## Como importar e executar

**Pré-requisitos:**

- n8n instalado (local ou servidor)
- Ollama em execução com modelo configurado (ex.: `ollama run llama3`)
- Webhook exposto publicamente (ex.: ngrok) para receber respostas do Telegram
- Credenciais configuradas no n8n: Telegram, Gmail, Google Drive e Productive.io

**Passos:**

```text
1. Importar automation-invoice-two-agent-review-ngrok.json no n8n.
2. Configurar credenciais em cada nó que as solicitar.
3. Ajustar variáveis: PRODUCTIVE_PERSON_ID, HOURLY_RATE, CURRENCY.
4. Ativar o webhook (ngrok ou equivalente).
5. Ativar o workflow no n8n.
6. Executar manualmente ou aguardar o agendamento (dias 1 e 16).
7. Responder no Telegram com approve, reject ou edit.
```

---

## Evidências de funcionamento

As evidências estão em `docs/evidences/`:

| Arquivo | Descrição |
|---------|-----------|
| `evidence1.png` | Telegram — rascunho da Invoice #018, período 16–30/04, 65 horas, com instruções de aprovação |
| `evidence2.png` | Telegram — rascunho revisado após comando `edit`: tom formal aplicado, alterações rastreadas |
| `evidence3.png` | Telegram — confirmação de envio pelo Gmail após aprovação |
| `evidence4.png` | Gmail — e-mail enviado (versão do rascunho inicial) |
| `evidence5.png` | Gmail — e-mail enviado (versão revisada após `edit`) |
| `evidence6.png` | Telegram — segunda execução com aprovação direta e envio confirmado |
| `evidence7.jpeg` | Google Drive — pasta `Invoices/Draft` com histórico de rascunhos da Invoice-018 |

---

## Estrutura do repositório

```text
projeto-3/
├── agent.md
├── README.md
├── relatorio-entrega.md
├── automation-invoice-complete-ngrok.json        ← Solution A
├── automation-invoice-two-agent-review-ngrok.json ← Solution C (final)
├── docs/
│   ├── mission-brief.md
│   ├── mentorship-pack.md
│   ├── workflow-runbook.md
│   ├── merge-readiness-pack.md
│   ├── adr/
│   │   └── 001-escolha-da-solucao.md
│   └── evidences/
│       ├── evidence1.png
│       ├── evidence2.png
│       ├── evidence3.png
│       ├── evidence4.png
│       ├── evidence5.png
│       ├── evidence6.png
│       └── evidence7.jpeg
└── solutions/
    ├── solution-a/README.md   ← Agente único (implementada)
    ├── solution-b/README.md   ← Base de conhecimento histórica (proposta)
    └── solution-c/README.md   ← Dois agentes (implementada — solução final)
```

---

## Artefatos obrigatórios

| Artefato | Arquivo |
|----------|---------|
| Mission Brief | [docs/mission-brief.md](docs/mission-brief.md) |
| Agent.md | [agent.md](agent.md) |
| Mentorship Pack | [docs/mentorship-pack.md](docs/mentorship-pack.md) |
| Workflow Runbook | [docs/workflow-runbook.md](docs/workflow-runbook.md) |
| ADR — Escolha da solução | [docs/adr/001-escolha-da-solucao.md](docs/adr/001-escolha-da-solucao.md) |
| Merge-Readiness Pack | [docs/merge-readiness-pack.md](docs/merge-readiness-pack.md) |
| Relatório de Entrega | [relatorio-entrega.md](relatorio-entrega.md) |
| Solution A | [solutions/solution-a/README.md](solutions/solution-a/README.md) |
| Solution B | [solutions/solution-b/README.md](solutions/solution-b/README.md) |
| Solution C | [solutions/solution-c/README.md](solutions/solution-c/README.md) |
