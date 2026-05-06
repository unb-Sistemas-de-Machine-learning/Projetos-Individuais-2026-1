# ADR-008: `continueOnFail: true` nos Nós HTTP da Gemini API

## Status
Aceito

## Contexto

A solution-c implementa retry automático quando a Gemini API retorna uma resposta inválida. O fluxo esperado é:

```
Call Gemini (Attempt 1) → schema inválido? → Call Gemini (Retry) → schema inválido? → Build Fallback (ai_flagged=true)
```

Por padrão, o nó HTTP Request do n8n lança uma exceção e interrompe a execução do workflow quando recebe uma resposta com status HTTP não-2xx (ex: 401 Unauthorized por chave inválida, 429 Too Many Requests por rate limit, 500 Internal Server Error).

Com o comportamento padrão, qualquer falha de API — que é exatamente o cenário que a solution-c deve tratar — mata o workflow antes de chegar ao nó de validação de schema. O caminho de retry e fallback nunca é exercitado para erros de HTTP.

O runbook exige explicitamente: "configurar key Gemini inválida, abrir issue, confirmar que `ai_flagged=true` aparece na linha do Sheets" como caso de teste obrigatório da solution-c. Esse caso de teste é impossível de executar sem um mecanismo que permita ao workflow continuar após um erro HTTP.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **`continueOnFail: true` no nó HTTP (escolhido)** | Nativo do n8n; o nó emite um item de erro com `{error, statusCode}` no output principal; o código de validação de schema recebe esse item e trata como resposta inválida (`candidates` ausente → `responseText = ''` → `parse_error=true` → `schema_valid=false`) | A mensagem de erro da API (ex: "API key not valid") não é propagada como contexto para o fallback — perde-se o motivo da falha |
| **Nó de tratamento de erro separado (Error Trigger)** | Captura erros em qualquer nó do workflow; permite lógica de fallback centralizada | Exige configuração de sub-workflow separado; incompatível com o modelo linear de um único workflow exigido pelo mentorship-pack |
| **Try/catch dentro do Code node de validação** | Lógica de retry toda em JS, sem depender de feature do n8n | O Code node não pode fazer chamadas HTTP — o retry real (segunda chamada à Gemini) teria que ser simulado ou inlinado, o que não é um retry de verdade |
| **Verificar o status HTTP no IF node antes de validar schema** | Explícito; fácil de ler no grafo do workflow | Dobra o número de IF nodes (um para status HTTP, outro para schema); aumenta complexidade do grafo sem ganho real — o código de validação já detecta resposta vazia |

## Decisão

**Adicionar `"continueOnFail": true` nos dois nós HTTP Request que chamam a Gemini API** (`Call Gemini API (Attempt 1)` e `Call Gemini API (Retry)`).

Com `continueOnFail: true`, quando a API retorna 4xx ou 5xx, o nó emite um item com o erro no output principal em vez de interromper o workflow. O campo `candidates` estará ausente nesse item. O nó "Validate Schema" subsequente já trata a ausência de `candidates`:

```javascript
const candidates = geminiData.candidates || [];
const responseText = candidates[0]?.content?.parts?.[0]?.text || '';
// responseText = '' → parseError = true → schemaValid = false
```

Com `schema_valid=false`, o IF node roteia para o retry (Attempt 1) ou para o Build Fallback (Attempt 2), produzindo `ai_flagged=true` no Sheets.

O nó "Send to Slack" e o nó "Log to Sheets" não recebem `continueOnFail` — erros neles devem ser visíveis para diagnóstico operacional.

## Consequências

- **O fallback `ai_flagged=true` é exercitável em teste**: usar uma chave Gemini inválida no `GEMINI_API_KEY` do n8n aciona corretamente o caminho Attempt 1 → falha → Retry → falha → Build Fallback. Evidenciado em `sheets-ai-flagged.png`.
- **Erros de API são silenciados no log de execução do n8n**: com `continueOnFail: true`, o nó aparece como verde (sucesso) no execution log mesmo quando a API retornou 401. O diagnóstico de "por que foi para o fallback" requer inspecionar o output do nó de validação, não o nó HTTP.
- **Aplica-se apenas à Gemini API, não ao Slack nem ao Sheets**: erros nos nós de entrega (Slack, Sheets) interrompem o workflow normalmente — são falhas de infraestrutura, não de classificação, e devem ser investigadas.
- **Não afeta o caminho feliz**: quando a Gemini retorna 200 com JSON válido, `continueOnFail` não tem efeito — o comportamento é idêntico ao de `continueOnFail: false`.

## Evidências

- `docs/evidence/solution-c/sheets-ai-flagged.png` — linha com `ai_flagged=TRUE` no Google Sheets, produzida com `GEMINI_API_KEY=INVALID_KEY_TEST`.
- `docs/evidence/solution-c/n8n-execution-log-ai-flagged.png` — execution log do caso ai_flagged mostrando o caminho completo através dos nós de retry e fallback.
