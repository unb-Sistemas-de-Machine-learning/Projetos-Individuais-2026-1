# Merge-Readiness Pack

> **Projeto:** IssueTriageBot
> **Aluno(a):** Felipe Amorim de Araújo
> **Data:** 05/05/2026

---

## 1. Resumo da solução escolhida

**Solution C — Validação de Schema + Retry + Fallback com `ai_flagged`**

O IssueTriageBot recebe eventos `issues.opened` do GitHub via webhook, classifica
cada issue usando a Gemini API (tipo, severidade, componente, confiança, resumo) e
roteia a notificação ao canal Slack correto (`#incidents`, `#backlog` ou `#questions`),
registrando o resultado no Google Sheets.

A solution-c adiciona ao fluxo básico (solution-a) dois mecanismos de resiliência:

1. **Validação de schema** após cada resposta da Gemini: se `type` ou `severity`
   não forem valores reconhecidos, ou se `summary` estiver vazio, a resposta é
   rejeitada e uma segunda chamada à API é feita automaticamente.
2. **Fallback com `ai_flagged=true`** quando ambas as tentativas falham (incluindo
   erros HTTP como 401/429/500): a issue é roteada para `#backlog` com um banner
   de alerta e a linha no Sheets recebe `ai_flagged=TRUE` para revisão humana.

O prompt usa abordagem zero-shot (idêntica à solution-a), mantendo o custo por call
baixo e sem dependências externas além do código.

---

## 2. Comparação entre as três alternativas

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| **Abordagem** | Zero-shot: prompt direto, parse defensivo | Few-shot: 3 exemplos relevantes injetados da KB em runtime | Zero-shot + validação de schema + retry automático + fallback |
| **Custo** | Baixo — 1 call, ~650 tokens | Médio — 1 call, ~1 500 tokens | Baixo no happy path (1 call, ~650 tokens); médio no retry path (2 calls) |
| **Complexidade** | Baixa — 7 nós, 202 linhas de utils | Média — 7 nós, 300 linhas + `knowledge-base.json` | Alta — 14 nós, 261 linhas, IF/Merge nodes no workflow |
| **Qualidade da resposta** | Baseline — saídas inválidas normalizadas silenciosamente para `unknown` | Melhor em casos ambíguos — exemplos guiam o modelo | Garantida estruturalmente — schema inválido aciona retry antes de aceitar `unknown` |
| **Riscos** | Falha de API para o workflow; JSON malformado aceito sem sinal | KB desatualizada degrada qualidade sem sinal observável; drift KB ↔ workflow | Latência extra no retry path (~15s vs ~5s); workflow mais complexo |
| **Manutenibilidade** | Alta — 1 artefato, prompt simples | Média — KB precisa de curadoria; duas fontes de verdade | Alta — sem artefatos externos; `isValidSchema` precisa ser atualizado se enums mudarem |
| **Adequação ao problema** | MVP funcional; não cobre retry nem `ai_flagged` | Boa consistência; não cobre retry nem `ai_flagged` | Atende integralmente o mission-brief incluindo retry e `ai_flagged` |

**Solução escolhida:** C

**Justificativa:** Solution-c é a única que atende os dois critérios de aceitação
do mission-brief que exigem resiliência de API: retry automático e `ai_flagged=true`
no Sheets quando ambas as tentativas falham. No caminho normal (~99% dos casos), a
latência é idêntica à solution-a. A comparação completa com dados mensuráveis está
em `docs/adr/009-escolha-da-solucao-final.md`.

---

## 3. Testes executados

### Testes unitários (Jest)

| Suite | Arquivo | Testes | Resultado |
|-------|---------|--------|-----------|
| Solution A — utils | `tests/solution-a/utils.test.js` | 49 | ✅ Passou |
| Solution B — utils | `tests/solution-b/utils.test.js` | 70 | ✅ Passou |
| Solution B — knowledge base | `tests/solution-b/knowledge-base.test.js` | 12 | ✅ Passou |
| Solution C — utils | `tests/solution-c/utils.test.js` | 92 | ✅ Passou |
| **Total** | | **223** | ✅ **Todos passaram** |

Saídas completas em `docs/evidence/<solution>/jest-output.txt`.

### Testes de validação end-to-end (por solução)

| Caso | Canal esperado | A | B | C |
|------|---------------|---|---|---|
| `[TEST] App crashes on login` (bug crítico) | `#incidents` | ✅ | ✅ | ✅ |
| `[TEST] Add dark mode support` (feature) | `#backlog` | ✅ | ✅ | ✅ |
| `[TEST] How do I reset my password?` (question) | `#questions` | ✅ | ✅ | ✅ |
| `GEMINI_API_KEY` inválida → `ai_flagged=true` | `#backlog` | ❌ workflow para | ❌ workflow para | ✅ |

Latência medida (criação da issue → mensagem no Slack):
- Solution-c caminho normal: < 10s ✅ (SLA do mission-brief: < 30s)
- Solution-c caminho retry: ~15s ✅

---

## 4. Evidências de funcionamento

| Arquivo | Solução | Conteúdo |
|---------|---------|----------|
| `docs/evidence/solution-a/github-webhook-delivered.png` | A | 3 entregas com 200 OK |
| `docs/evidence/solution-a/slack-{incidents,backlog,questions}.png` | A | Mensagens nos 3 canais |
| `docs/evidence/solution-a/sheets-rows.png` | A | 3 linhas no Sheets |
| `docs/evidence/solution-b/github-webhook-delivered.png` | B | 3 entregas com 200 OK |
| `docs/evidence/solution-b/slack-{incidents,backlog,questions}.png` | B | Mensagens nos 3 canais |
| `docs/evidence/solution-b/sheets-rows.png` | B | 3 linhas no Sheets |
| `docs/evidence/solution-c/github-webhook-delivered.png` | C | 4 entregas com 200 OK |
| `docs/evidence/solution-c/slack-{incidents,backlog,questions}.png` | C | Mensagens nos 3 canais |
| `docs/evidence/solution-c/sheets-rows.png` | C | 4 linhas no Sheets |
| `docs/evidence/solution-c/sheets-ai-flagged.png` | **C** | Linha com `ai_flagged=TRUE` |
| `docs/evidence/solution-c/n8n-execution-log-ai-flagged.png` | **C** | Caminho retry → fallback executado |

---

## 5. Limitações conhecidas

- **URL do ngrok muda a cada restart**: o webhook no GitHub precisa ser atualizado
  manualmente se o ngrok for reiniciado. Uma URL fixa (Cloudflare Tunnel ou plano
  pago do ngrok) eliminaria esse atrito operacional.
- **Free tier da Gemini API**: o rate limit do tier gratuito pode causar 429s em
  uso intenso. A solution-c trata isso via retry + fallback, mas em produção real
  seria necessário um plano pago ou circuit breaker com backoff exponencial.
- **Sem deduplicação de eventos**: se o GitHub reenviar o mesmo webhook (retry do
  GitHub em falha de entrega), a issue pode ser processada e registrada duas vezes
  no Sheets. Uma chave de idempotência por `issue.number` resolveria.
- **A vantagem qualitativa da solution-b não foi evidenciada**: os casos de teste
  do runbook são suficientemente claros para que o Gemini os classifique corretamente
  sem exemplos. A diferença da solution-b seria observável em datasets com issues
  ambíguas — não foi possível medir com os casos disponíveis.

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Gemini API indisponível ou rate limit excedido | Média | Médio | Retry automático (solution-c); fallback com `ai_flagged=true` no Sheets |
| Classificação incorreta pela IA | Média | Médio | Prompt estruturado com regras explícitas; campo `confidence` exposto no Sheets; `low_confidence=true` sinaliza revisão |
| Payload do GitHub em formato inesperado | Baixa | Baixo | Validação de `title` em Build Prompt antes de chamar a Gemini; retorno antecipado com `invalid_input=true` |
| Credenciais Slack/Sheets expiradas | Baixa | Alto | Erro visível no execution log do n8n; nós de entrega não têm `continueOnFail` — falha é explícita |
| URL do ngrok expirada entre sessões | Alta (dev) | Baixo | Atualizar webhook no GitHub antes de cada sessão de testes; não se aplica em produção com URL fixa |

---

## 7. Decisões arquiteturais

| ADR | Decisão |
|-----|---------|
| [ADR-001](adr/001-tunnel-para-webhook-local.md) | ngrok em vez do tunnel nativo do n8n (removido no n8n 2.x) |
| [ADR-002](adr/002-slack-http-request-em-vez-de-no-slack.md) | HTTP Request em vez do nó Slack para envio de blocos formatados |
| [ADR-003](adr/003-pre-serializacao-json-em-code-nodes.md) | Pré-serializar corpos JSON como string em Code nodes para HTTP Requests |
| [ADR-004](adr/004-automapinputdata-para-google-sheets.md) | `autoMapInputData` + Code node de flatten para o Google Sheets |
| [ADR-005](adr/005-selecao-de-exemplos-few-shot.md) | Overlap ponderado de tokens/labels para seleção de exemplos da KB (solution-b) |
| [ADR-006](adr/006-formato-do-prompt-few-shot.md) | Formato do bloco de exemplos no prompt few-shot (solution-b) |
| [ADR-007](adr/007-criterio-de-validacao-de-schema.md) | `type`/`severity=unknown` rejeitados como schema inválido; `component=unknown` aceito |
| [ADR-008](adr/008-continueonerror-nos-nos-gemini.md) | `continueOnFail=true` nos nós HTTP da Gemini para habilitar retry em erros 4xx/5xx |
| [ADR-009](adr/009-escolha-da-solucao-final.md) | Comparação das 3 soluções; escolha da solution-c |

---

## 8. Instruções de execução

```bash
# 1. Subir o n8n localmente
docker-compose up -d

# 2. Em outro terminal, abrir tunnel público
ngrok http 5678
# Copiar a URL: https://<random>.ngrok-free.app

# 3. Acessar o n8n
# http://localhost:5678

# 4. Importar o workflow da solution-c
# Workflows → Import → selecionar solutions/solution-c/workflow.json

# 5. Configurar as variáveis de ambiente no n8n
# Settings → Environment Variables:
#   GEMINI_API_KEY=<sua chave>
#   SLACK_BOT_TOKEN=<seu token>
#   GOOGLE_SHEETS_ID=<id da planilha>

# 6. Configurar a credencial Google Sheets OAuth no nó "Log to Sheets"

# 7. Ativar o workflow

# 8. Registrar o webhook no GitHub
# Repositório → Settings → Webhooks → Add webhook
#   Payload URL: https://<ngrok-url>/webhook/github-issues
#   Content type: application/json
#   Events: Issues

# 9. Executar testes unitários
npm test

# Para rodar apenas a solution-c:
npm run test:solution-c
```

**Variáveis de ambiente necessárias:**

| Variável | Descrição |
|----------|-----------|
| `GEMINI_API_KEY` | Chave da Gemini API (Google AI Studio) |
| `SLACK_BOT_TOKEN` | Bot token do Slack com escopo `chat:write` |
| `GOOGLE_SHEETS_ID` | ID da planilha Google Sheets (da URL) |

---

## 9. Checklist de revisão

- [x] Mission brief atendido — todos os critérios de aceitação cobertos, incluindo retry e `ai_flagged`
- [x] Três soluções implementadas e validadas com fluxo end-to-end completo
- [x] Testes unitários executados: 223 testes, 4 suites, 100% passando
- [x] Evidências registradas em `docs/evidence/` para as 3 soluções
- [x] `sheets-ai-flagged.png` presente (obrigatório solution-c)
- [x] 9 ADRs registrados em `docs/adr/` cobrindo todas as decisões com alternativas e evidências
- [x] Commits com mensagens descritivas e racionalidade da decisão
- [x] `solutions/solution-{a,b,c}/utils.js` e `workflow.json` presentes
- [x] `agent.md` preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido na ordem das etapas

---

## 10. Justificativa para merge

A entrega cobre integralmente o contrato definido no mission-brief e no workflow-runbook:

- **Três soluções funcionais e comparadas**: cada solução foi executada com fluxo
  real (GitHub webhook → Gemini → Slack + Sheets), não apenas testada com Jest.
  A comparação usa dados mensuráveis — não preferência subjetiva.

- **Critérios de aceitação atendidos**: issues críticas chegam ao `#incidents` em
  < 10s; roteamento correto para `#backlog` e `#questions`; toda issue processada
  gera linha no Sheets; falha total da Gemini gera `ai_flagged=true` — todos
  evidenciados com screenshots.

- **Processo auditável**: cada decisão técnica relevante tem ADR com contexto,
  alternativas descartadas com prós/contras, decisão baseada em evidência mensurável,
  e referência ao arquivo de evidência. Nenhum ADR foi escrito retroativamente sem
  evidência.

- **223 testes passando**: cobertura de funções puras cobrindo casos normais,
  edge cases e os três caminhos da lógica de retry — condição necessária satisfeita
  antes de cada validação end-to-end.
