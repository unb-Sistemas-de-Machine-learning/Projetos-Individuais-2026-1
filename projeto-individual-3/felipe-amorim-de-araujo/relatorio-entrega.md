# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Felipe Amorim de Araújo
> **Matrícula:** 221022275
> **Data de entrega:** 05/05/2026

---

## 1. Resumo do Projeto

O **IssueTriageBot** automatiza a triagem de issues abertas no GitHub, eliminando o
trabalho manual de classificar tipo, severidade e componente afetado. Quando uma
issue é criada, o fluxo no n8n captura o evento via webhook, monta um prompt com os
dados da issue e chama a Gemini API para obter uma classificação estruturada em JSON.
Com base nessa classificação, o fluxo roteia a notificação ao canal Slack correto
(`#incidents` para bugs críticos, `#backlog` para bugs e features, `#questions` para
dúvidas) e persiste o registro completo no Google Sheets.

O papel da IA é central e decisório: é a classificação retornada pelo modelo que
determina tanto o canal de destino quanto os campos gravados no Sheets. Sem a IA,
o fluxo não tem como distinguir um incidente crítico de uma feature request.

Foram implementadas três soluções com níveis crescentes de resiliência — zero-shot,
few-shot com base de conhecimento, e validação de schema com retry automático — e
todas foram validadas com fluxo end-to-end real antes da comparação final. A
solution-c foi escolhida por ser a única que atende integralmente os critérios de
aceitação do mission-brief, incluindo retry automático e sinalização `ai_flagged=true`
para falhas totais da API.

---

## 2. Problema Escolhido

Equipes de desenvolvimento perdem tempo triando manualmente issues abertas no GitHub:
decidir se é um bug, feature ou dúvida, qual a urgência e qual time deve ser
notificado é um processo repetitivo, sujeito a inconsistências e que atrasa a
resposta a incidentes críticos.

O problema é relevante porque:

- **Incidentes críticos precisam de resposta imediata.** Um bug de produção que
  chega no canal errado ou fica sem notificação por minutos tem impacto real.
- **Triagem manual não escala.** Em repositórios com volume alto, o custo de leitura
  e julgamento de cada issue por um humano é desproporcional ao valor gerado.
- **Inconsistência gera ruído.** Times diferentes classificam a mesma issue de formas
  diferentes, tornando o histórico no Sheets pouco confiável para análise.

O IssueTriageBot trata o caso rotineiro de forma completamente automática, reservando
a intervenção humana para os casos sinalizados com `low_confidence` ou `ai_flagged`.

---

## 3. Desenho do Fluxo

O fluxo da **solution-c** (solução final escolhida) opera em etapas sequenciais com
branching condicional para retry e fallback:

```
GitHub Webhook (issues.opened)
  │
  ▼
Build Prompt ──── [valida título; monta prompt zero-shot + corpo Gemini]
  │
  ▼
Call Gemini API (Attempt 1) ──── [continueOnFail=true]
  │
  ▼
Validate Schema (Attempt 1) ──── [parse JSON; isValidSchema()]
  │
  ├── schema válido ──────────────────────────────────────┐
  │                                                        │
  └── schema inválido                                      │
        │                                                  │
        ▼                                                  │
  Call Gemini API (Retry) ──── [continueOnFail=true]       │
        │                                                  │
        ▼                                                  ▼
  Validate Schema (Retry)              Merge Valid Paths ──┤
        │                                                  │
        ├── schema válido ────────────────────────────────►│
        │                                                  │
        └── schema inválido                                │
              │                                            ▼
              ▼                                    Merge With Fallback
        Build Fallback (ai_flagged=true) ─────────────────┘
                                                           │
                                         ┌─────────────────┤
                                         │                 │
                                         ▼                 ▼
                                   Send to Slack    Prepare Sheets Row
                                   (HTTP Request)         │
                                                          ▼
                                                   Log to Sheets
```

### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| GitHub Webhook | `n8n-nodes-base.webhook` | Recebe eventos `issues.opened` do GitHub via HTTP POST |
| Build Prompt | `n8n-nodes-base.code` | Valida presença do título; extrai campos da issue; monta prompt e serializa corpo da requisição Gemini |
| Call Gemini API (Attempt 1) | `n8n-nodes-base.httpRequest` | Chama `gemini-2.5-flash-lite` com o prompt; `continueOnFail=true` permite que erros HTTP fluam adiante |
| Validate Schema (Attempt 1) | `n8n-nodes-base.code` | Faz parse da resposta; valida schema estritamente; formata mensagem Slack e linha Sheets; emite `schema_valid` |
| IF: Schema Valid? | `n8n-nodes-base.if` | Roteia para Merge (válido) ou Retry (inválido) com base em `schema_valid` |
| Call Gemini API (Retry) | `n8n-nodes-base.httpRequest` | Segunda chamada à Gemini com o mesmo prompt; `continueOnFail=true` |
| Validate Schema (Retry) | `n8n-nodes-base.code` | Idem Attempt 1, mas sobre a resposta do retry |
| IF: Retry Schema Valid? | `n8n-nodes-base.if` | Roteia para Merge (válido) ou Fallback (inválido) |
| Build Fallback | `n8n-nodes-base.code` | Cria classificação padrão (`unknown`) com `ai_flagged=true`; formata Slack e Sheets |
| Merge Valid Paths | `n8n-nodes-base.merge` | Converge attempt-1 OK e retry OK (modo append) |
| Merge With Fallback | `n8n-nodes-base.merge` | Converge caminhos válidos e fallback (modo append) |
| Send to Slack | `n8n-nodes-base.httpRequest` | Envia mensagem formatada com blocos Slack para o canal determinado pela classificação |
| Prepare Sheets Row | `n8n-nodes-base.code` | Extrai `sheets_row` do contexto para o nó Google Sheets |
| Log to Sheets | `n8n-nodes-base.googleSheets` | Appenda linha no Google Sheets via `autoMapInputData` |

---

## 4. Papel do Agente de IA

A Gemini API é o agente classificador do fluxo. Sem sua decisão, nenhuma ação de
roteamento ou persistência pode ocorrer.

- **Modelo/serviço utilizado:** Google Gemini 2.5 Flash Lite
  (`gemini-2.5-flash-lite:generateContent` via REST)

- **Tipo de decisão tomada pela IA:** Classificação estruturada multi-label —
  o modelo lê o título, corpo, labels e repositório da issue e retorna:
  - `type`: `bug` | `feature` | `question`
  - `severity`: `critical` | `medium` | `low`
  - `component`: `frontend` | `backend` | `infra` | `unknown`
  - `confidence`: float [0.0, 1.0]
  - `summary`: resumo em uma linha
  - `reasoning`: justificativa da classificação

- **Como a decisão da IA afeta o fluxo:**
  - `type=question` → notificação vai para `#questions`
  - `type=bug` + `severity=critical` → notificação vai para `#incidents`
  - qualquer outro caso → notificação vai para `#backlog`
  - `confidence < 0.7` → `low_confidence=true` no Sheets; banner de alerta no Slack
  - falha de API (ambas as tentativas) → `ai_flagged=true` no Sheets; roteamento
    padrão para `#backlog` com banner de alerta

A IA não apenas gera texto — ela determina o canal de entrega da notificação,
influencia diretamente a resposta operacional do time e produz metadados auditáveis
(`confidence`, `reasoning`) que permitem revisar a qualidade das classificações ao
longo do tempo.

---

## 5. Lógica de Decisão

**Condição 1 — Roteamento Slack (em `Validate Schema` / `Build Fallback`):**
- `type == 'question'` → canal `#questions`
- `type == 'bug'` AND `severity == 'critical'` → canal `#incidents`
- qualquer outro resultado → canal `#backlog`

**Condição 2 — Validação de schema pós-Gemini (IF: Schema Valid?):**
- `schema_valid == true` → dados fluem para Merge e seguem para entrega
- `schema_valid == false` → segunda chamada à Gemini API (Retry)

**Condição 3 — Retry (IF: Retry Schema Valid?):**
- `schema_valid == true` → dados fluem para Merge e seguem para entrega
- `schema_valid == false` → Build Fallback com `ai_flagged=true`

**Critério de `schema_valid`** (implementado em `isValidSchema()`):
- `type` ∈ `{bug, feature, question}` — `unknown` é inválido (aciona retry)
- `severity` ∈ `{critical, medium, low}` — `unknown` é inválido (aciona retry)
- `component` ∈ `{frontend, backend, infra, unknown}` — `unknown` é válido por spec
- `confidence` ∈ `[0.0, 1.0]`, `low_confidence` booleano, `summary` não-vazio

**Condição 4 — Input inválido (em `Build Prompt`):**
- `title` ausente ou vazio → retorno antecipado com `invalid_input=true`; fluxo
  encerrado antes de chamar a Gemini

---

## 6. Integrações

| Serviço | Finalidade |
|---------|------------|
| **GitHub** | Fonte de eventos — webhook `issues.opened` dispara o fluxo |
| **Google Gemini API** (`gemini-2.5-flash-lite`) | Classificação da issue em tipo, severidade, componente e confiança |
| **Slack** (API `chat.postMessage`) | Entrega de notificações formatadas nos canais `#incidents`, `#backlog` e `#questions` |
| **Google Sheets** (API v4) | Persistência de todos os campos da classificação para rastreabilidade e auditoria |
| **ngrok** | Tunnel HTTP para expor o webhook do n8n local ao GitHub durante desenvolvimento |

---

## 7. Persistência e Rastreabilidade

Toda issue processada gera uma linha no Google Sheets com os seguintes campos:

| Campo | Descrição |
|-------|-----------|
| `timestamp` | ISO 8601 do momento do processamento |
| `issue_number` | Número da issue no GitHub |
| `title` | Título original da issue |
| `url` | Link direto para a issue no GitHub |
| `type` | Classificação: `bug`, `feature`, `question` ou `unknown` |
| `severity` | Urgência: `critical`, `medium`, `low` ou `unknown` |
| `component` | Componente: `frontend`, `backend`, `infra` ou `unknown` |
| `confidence` | Score de confiança em percentual (ex: `87%`) |
| `low_confidence` | `true` se confiança < 70% — sinaliza revisão recomendada |
| `ai_flagged` | `true` somente quando ambas as chamadas à Gemini falharam |
| `summary` | Resumo em uma linha gerado pela IA |
| `reasoning` | Justificativa da classificação gerada pela IA |

A combinação de `confidence`, `low_confidence` e `ai_flagged` permite três níveis
de auditoria: classificação de alta confiança (revisão opcional), classificação de
baixa confiança (revisão recomendada) e falha total de IA (revisão obrigatória).

---

## 8. Tratamento de Erros e Limites

- **Falhas da Gemini API (4xx/5xx):** `continueOnFail=true` nos nós HTTP impede
  que o workflow pare. A resposta de erro flui para o nó de validação, que detecta
  `candidates` ausente e marca `schema_valid=false`, acionando o retry. Se o retry
  também falhar, `Build Fallback` produz `ai_flagged=true` e a issue é roteada
  para `#backlog` com banner de alerta. Evidenciado em
  `docs/evidence/solution-c/sheets-ai-flagged.png`.

- **Resposta malformada da IA (JSON inválido ou enums indesejados):**
  `parseGeminiResponse` extrai o JSON (removendo eventuais blocos de código markdown),
  e `isValidSchema` rejeita resultados onde `type` ou `severity` foram normalizados
  para `unknown` — indicando que o modelo retornou um valor não previsto. Isso
  aciona o retry sem nenhuma intervenção humana.

- **Entradas inválidas (issue sem título):** `Build Prompt` valida a presença do
  campo `title` antes de qualquer chamada à IA. Issues sem título retornam
  `invalid_input=true` e o fluxo encerra sem chamar a Gemini nem gravar no Sheets.

- **Baixa confiança (não é erro):** quando `confidence < 0.7`, a classificação é
  aceita normalmente. O campo `low_confidence=true` é gravado no Sheets e o banner
  "⚠️ Low confidence" aparece na mensagem Slack. `low_confidence` e `ai_flagged`
  são sinais distintos — documentados em `agent.md` e no ADR-007.

---

## 9. Diferenciais implementados

- [ ] Memória de contexto
- [x] Multi-step reasoning — solution-c implementa validação de schema + retry
  automático + fallback, um pipeline de decisão em múltiplas etapas onde a saída
  de cada estágio condiciona a execução do próximo
- [x] Integração com base de conhecimento — solution-b carrega `knowledge-base.json`
  com 7 issues classificadas e seleciona os 3 exemplos mais relevantes por scoring
  de overlap ponderado de tokens e labels (ADR-005)
- [ ] Uso de embeddings / busca semântica — a seleção de exemplos da solution-b
  usa overlap literal de tokens, não vetores semânticos

---

## 10. Limitações e Riscos

**Limitações:**

- **URL do ngrok muda a cada restart:** o webhook no GitHub precisa ser atualizado
  manualmente. Em produção, uma URL fixa é necessária.
- **Sem deduplicação de eventos:** se o GitHub reenviar o mesmo webhook, a issue
  pode ser processada e registrada duas vezes no Sheets. Uma chave de idempotência
  por `issue.number` resolveria.
- **Vantagem qualitativa da solution-b não evidenciada:** os casos de teste do
  runbook são suficientemente claros para classificação correta sem exemplos. A
  diferença da abordagem few-shot seria observável em issues ambíguas, mas não foi
  possível medir com os casos disponíveis.

**Riscos:**

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Classificação incorreta pela IA | Média | Médio | `confidence` + `reasoning` expostos no Sheets para auditoria; `low_confidence` sinaliza revisão |
| Rate limit Gemini free tier | Média | Médio | Retry automático absorve falhas transitórias; `ai_flagged=true` garante rastreabilidade da falha |
| Payload GitHub em formato inesperado | Baixa | Baixo | Validação de `title` antes de chamar a IA; campos opcionais com defaults seguros |
| Credenciais Slack/Sheets expiradas | Baixa | Alto | Nós de entrega sem `continueOnFail` — falha é explícita no execution log do n8n |

---

## 11. Como executar

```bash
# 1. Clonar o repositório e instalar dependências de teste
npm install

# 2. Executar os testes unitários (223 testes, 4 suites)
npm test

# 3. Subir o n8n localmente
docker-compose up -d

# 4. Abrir tunnel público em outro terminal
ngrok http 5678
# Copiar a URL gerada: https://<random>.ngrok-free.app

# 5. Acessar o n8n em http://localhost:5678
# Importar: Workflows → Import → solutions/solution-c/workflow.json

# 6. Configurar variáveis de ambiente no n8n (Settings → Environment Variables):
#   GEMINI_API_KEY   = <chave Google AI Studio>
#   SLACK_BOT_TOKEN  = <bot token com escopo chat:write>
#   GOOGLE_SHEETS_ID = <ID da planilha (da URL)>

# 7. Configurar credencial Google Sheets OAuth no nó "Log to Sheets"

# 8. Ativar o workflow

# 9. Registrar webhook no repositório GitHub de teste:
#   URL: https://<ngrok-url>/webhook/github-issues
#   Content type: application/json
#   Evento: Issues

# 10. Criar uma issue e verificar mensagem no Slack (< 30s) e linha no Sheets
```

---

## 12. Referências

1. Google. *Gemini API Documentation — generateContent*. Disponível em: https://ai.google.dev/api/generate-content
2. n8n. *n8n Documentation — Code Node, HTTP Request, Google Sheets*. Disponível em: https://docs.n8n.io
3. GitHub. *Webhooks documentation — issues event*. Disponível em: https://docs.github.com/en/webhooks/webhook-events-and-payloads#issues

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (.json) — `solutions/solution-c/workflow.json`
- [x] Código auxiliar incluído — `solutions/solution-{a,b,c}/utils.js`, `knowledge-base.json`
- [x] Demonstração do fluxo — screenshots em `docs/evidence/solution-c/` (4 casos de teste)
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
