# IssueTriageBot

Agente de triagem automática de issues GitHub usando n8n + Gemini API.

Quando uma issue é criada, o fluxo classifica tipo, severidade e componente via IA
e roteia a notificação ao canal Slack correto (`#incidents`, `#backlog` ou
`#questions`), registrando o resultado no Google Sheets.

> **Aluno:** Felipe Amorim de Araújo · **Matrícula:** 221022275
> **Projeto Individual 3 — Automação com n8n e Agentes de IA**

---

## Como funciona

```
GitHub issues.opened
        │
        ▼
   Build Prompt
        │
        ▼
 Gemini API (Attempt 1)
        │
   schema válido? ──── sim ──────────────────────┐
        │ não                                     │
        ▼                                         │
 Gemini API (Retry)                               │
        │                                         │
   schema válido? ──── sim ──────────────────────►│
        │ não                                     ▼
        ▼                                   Slack + Sheets
  Fallback ai_flagged=true ────────────────────────┘
```

A IA retorna um JSON com `type`, `severity`, `component`, `confidence` e `summary`.
Esse resultado determina o canal Slack e todos os campos gravados no Sheets.

---

## Soluções implementadas

| | Solution A | Solution B | Solution C |
|---|---|---|---|
| Abordagem | Zero-shot | Few-shot + knowledge base | Zero-shot + validação + retry |
| Calls/issue | 1 | 1 | 1–2 |
| Nós n8n | 7 | 7 | 14 |
| Testes Jest | 49 | 82 | 92 |
| `ai_flagged` | ✗ | ✗ | ✅ |

**Solução escolhida: C** — única que cobre retry automático e `ai_flagged=true`
conforme os critérios de aceitação do mission-brief. Ver
[ADR-009](docs/adr/009-escolha-da-solucao-final.md) para a comparação completa.

---

## Estrutura do projeto

```
├── solutions/
│   ├── solution-a/          # Zero-shot
│   │   ├── utils.js
│   │   └── workflow.json
│   ├── solution-b/          # Few-shot com knowledge base
│   │   ├── utils.js
│   │   ├── workflow.json
│   │   └── knowledge-base.json
│   └── solution-c/          # Validação de schema + retry (solução final)
│       ├── utils.js
│       └── workflow.json
├── tests/
│   ├── solution-a/utils.test.js
│   ├── solution-b/utils.test.js
│   ├── solution-b/knowledge-base.test.js
│   └── solution-c/utils.test.js
├── docs/
│   ├── adr/                 # 9 ADRs com decisões arquiteturais
│   ├── evidence/            # Screenshots e logs de cada solução
│   ├── mission-brief.md
│   ├── workflow-runbook.md
│   ├── mentorship-pack.md
│   └── merge-readiness-pack.md
├── agent.md
├── relatorio-entrega.md
└── docker-compose.yml
```

---

## Pré-requisitos

- Docker e Docker Compose
- [ngrok](https://ngrok.com) (para expor o webhook localmente)
- Node.js 18+ (apenas para rodar os testes)
- Chave da [Gemini API](https://ai.google.dev)
- Slack bot token com escopo `chat:write` e canais `#incidents`, `#backlog`, `#questions`
- Google Sheets com as colunas: `timestamp`, `issue_number`, `title`, `url`, `type`, `severity`, `component`, `confidence`, `low_confidence`, `ai_flagged`, `summary`, `reasoning`

---

## Instalação e execução

### 1. Testes unitários

```bash
npm install
npm test                    # 223 testes, 4 suites
npm run test:solution-c     # apenas a solução final
```

### 2. Subir o n8n

Crie um arquivo `.env` na raiz com suas credenciais:

```env
GEMINI_API_KEY=sua_chave_aqui
SLACK_BOT_TOKEN=xoxb-seu-token
GOOGLE_SHEETS_ID=id_da_planilha
```

Suba o ambiente:

```bash
docker-compose up -d
```

O n8n estará disponível em `http://localhost:5678`
(usuário: `admin`, senha: `changeme` — altere em `docker-compose.yml`).

### 3. Expor o webhook

```bash
ngrok http 5678
# Copie a URL: https://<random>.ngrok-free.app
```

### 4. Importar e configurar o workflow

1. No n8n: **Workflows → Import** → selecione `solutions/solution-c/workflow.json`
2. Abra o nó **Log to Sheets** e configure a credencial Google Sheets OAuth
3. Ative o workflow

### 5. Registrar o webhook no GitHub

No repositório de teste: **Settings → Webhooks → Add webhook**

| Campo | Valor |
|-------|-------|
| Payload URL | `https://<ngrok-url>/webhook/github-issues` |
| Content type | `application/json` |
| Events | `Issues` |

> ⚠️ A URL do ngrok muda a cada restart — atualize o webhook se reiniciar o ngrok.

### 6. Testar

Abra uma issue no repositório e verifique:
- Mensagem Slack no canal correto em < 30s
- Linha registrada no Google Sheets com todos os campos

---

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `GEMINI_API_KEY` | Chave da Gemini API (Google AI Studio) |
| `SLACK_BOT_TOKEN` | Bot token do Slack (`xoxb-...`) |
| `GOOGLE_SHEETS_ID` | ID da planilha (extraído da URL do Sheets) |

---

## Decisões arquiteturais

| ADR | Decisão |
|-----|---------|
| [001](docs/adr/001-tunnel-para-webhook-local.md) | ngrok em vez do tunnel nativo removido no n8n 2.x |
| [002](docs/adr/002-slack-http-request-em-vez-de-no-slack.md) | HTTP Request em vez do nó Slack para blocos formatados |
| [003](docs/adr/003-pre-serializacao-json-em-code-nodes.md) | Pré-serializar JSON como string nos Code nodes |
| [004](docs/adr/004-automapinputdata-para-google-sheets.md) | `autoMapInputData` para o Google Sheets |
| [005](docs/adr/005-selecao-de-exemplos-few-shot.md) | Scoring de overlap ponderado para selecionar exemplos (solution-b) |
| [006](docs/adr/006-formato-do-prompt-few-shot.md) | Formato do bloco few-shot no prompt (solution-b) |
| [007](docs/adr/007-criterio-de-validacao-de-schema.md) | `type`/`severity=unknown` rejeitados; `component=unknown` aceito |
| [008](docs/adr/008-continueonerror-nos-nos-gemini.md) | `continueOnFail=true` nos nós HTTP da Gemini |
| [009](docs/adr/009-escolha-da-solucao-final.md) | Comparação das 3 soluções e escolha da solution-c |
