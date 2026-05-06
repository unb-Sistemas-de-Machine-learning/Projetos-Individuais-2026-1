# ADR-003: Pré-serializar corpos JSON em Code nodes para HTTP Requests

## Status
Aceito

## Contexto
O workflow faz duas chamadas HTTP com corpos JSON complexos: uma para a Gemini API
e uma para a Slack Web API. O n8n oferece `contentType: "json"` no nó HTTP Request
com suporte a expressões no campo `body`.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| `contentType: "json"` com expressão inline (`={{ ... }}`) | Configuração direta no nó | Mistura sintaxe de expressão n8n com template de string — `{{ }}` dentro de `=...` não interpola, é avaliado como bloco JS, produzindo JSON inválido |
| `contentType: "raw"` com corpo pré-serializado via `JSON.stringify` no Code node | Serialização explícita e previsível; sem ambiguidade de sintaxe | Requer um campo extra no output do Code node (`gemini_body_str`, `slack_body_str`) |

## Decisão

Pré-serializar os corpos JSON em **Code nodes** usando `JSON.stringify()` e passá-los
como string para o HTTP Request com `contentType: "raw"` e
`rawContentType: "application/json"`.

Motivo: a abordagem inline gerou o erro `"Invalid JSON payload received. Unknown name
\"\": Proto fields must have a name"` (HTTP 400) na Gemini API. Após investigação,
identificou-se que n8n avalia o campo `body` prefixado com `=` como expressão
JavaScript pura — `{{ }}` dentro dela é tratado como blocos JS, não como
interpolação, resultando em corpo malformado.

O mesmo padrão foi aplicado ao Slack para consistência e para evitar o mesmo problema.

## Consequências

- Code nodes de "Build Prompt" e "Parse Response" incluem campos `*_body_str` com
  o JSON já serializado
- HTTP Request nodes usam `body: "={{ $json.gemini_body_str }}"` (referência simples,
  sem template)
- Padrão deve ser replicado nas Solutions B e C para qualquer HTTP Request com corpo
  JSON dinâmico

## Evidências
Erro HTTP 400 da Gemini API com mensagem `"Proto fields must have a name"` recebido
durante validação end-to-end da Solution A — confirmou que o corpo enviado continha
campo com chave vazia.
