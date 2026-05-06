# ADR-002: HTTP Request em vez do nó Slack para envio de blocos

## Status
Aceito

## Contexto
O workflow precisa enviar mensagens formatadas com Block Kit do Slack (blocos com
campos de tipo, severidade, componente e link para a issue). O n8n tem um nó nativo
`n8n-nodes-base.slack` com o parâmetro `blocksUi` destinado a esse fim.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| Nó `n8n-nodes-base.slack` com `blocksUi` | Integrado ao n8n; usa credencial configurada | `blocksUi` não aceita expressões dinâmicas — ignora os blocos e envia apenas o campo `text` |
| HTTP Request → `chat.postMessage` (Slack Web API) | Controle total sobre o payload; blocos funcionam via corpo pré-serializado | Requer `SLACK_BOT_TOKEN` como variável de ambiente; não usa a credencial n8n |

## Decisão

Usar **HTTP Request** chamando `https://slack.com/api/chat.postMessage` com corpo
pré-serializado em JSON no Code node anterior. O token é injetado via
`$env.SLACK_BOT_TOKEN`.

Motivo: confirmado em execução real que o nó Slack envia apenas o `text` plano,
ignorando `blocksUi` quando o valor é uma expressão. A Slack Web API via HTTP Request
recebe e renderiza os blocos corretamente.

## Consequências

- O Switch node e os 3 nós Slack foram removidos — o roteamento de canal ficou no
  Code node "Parse Response", e um único HTTP Request substitui todos os três
- `SLACK_BOT_TOKEN` precisa estar no `.env` e no `docker-compose.yml`
- O bot token (xoxb-...) deve ter o scope `chat:write` no app Slack

## Evidências
Saída real do nó Slack com `blocksUi` em `docs/evidence/solution-a/` — a resposta
da Slack API mostra apenas um bloco `rich_text` gerado pelo campo `text`, sem os
blocos customizados que estavam em `blocksUi`.
