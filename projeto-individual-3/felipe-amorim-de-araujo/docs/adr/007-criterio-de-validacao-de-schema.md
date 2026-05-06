# ADR-007: Critério de Validação de Schema na Solution-C

## Status
Aceito

## Contexto

A solution-c introduz validação explícita do JSON retornado pela Gemini API antes de aceitar a classificação. O runbook descreve a solução como: "chamar Gemini, validar schema JSON, retry em caso de saída inválida, fallback com `ai_flagged=true`."

A palavra "inválida" impõe uma escolha de design real: o que exatamente constitui uma saída inválida que justifica uma nova chamada à API?

A solution-a já realiza normalização defensiva em `validateClassification`: se o modelo retorna `"type": "incident"` (não reconhecido), o campo é silenciosamente normalizado para `"unknown"` e a classificação é aceita sem retry. Isso garante que o fluxo nunca trave, mas aceita resultados degradados sem sinalizá-los.

A solution-c precisa de um critério mais estrito — preciso o suficiente para capturar falhas reais de classificação, mas sem rejeitar saídas legítimas do modelo (ex: `component=unknown` é explicitamente permitido pelas regras do prompt).

Restrições relevantes:
- Cada retry adiciona latência (~5–10s) e consome quota da API — o critério não pode ser excessivamente restritivo.
- O mission-brief exige que o fallback seja acionado apenas por falha completa da API, não por baixa confiança (`low_confidence` é sinal distinto de `ai_flagged`).
- O campo `component=unknown` é um valor legítimo na especificação do agente (`agent.md`) — não pode ser considerado falha.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Aceitar qualquer JSON parseável (sem validação de enum)** | Zero retries, latência mínima | Não diferencia solution-c de solution-a; falha silenciosa ao aceitar `type=unknown` como resultado válido |
| **Rejeitar qualquer campo `unknown` incluindo `component`** | Critério simétrico, simples de explicar | `component=unknown` é válido por especificação — rejeitar força retry desnecessário para issues cujo componente genuinamente não pode ser determinado |
| **Rejeitar apenas `type=unknown` e `severity=unknown`, aceitar `component=unknown` (escolhido)** | Alinhado com o schema do agente; `type` e `severity` são os campos de roteamento críticos — se inválidos, a notificação Slack vai para o canal errado | Assimetria entre campos pode ser confusa para quem lê o código sem contexto |
| **Validar apenas presença dos campos (não os valores)** | Máxima tolerância, sem retries por enums | Aceita `"type": "incident"` como válido; o roteamento para Slack ficaria incorreto mesmo sem sinalizar falha |
| **Rejeitar se `confidence < 0.7`** | Usa o sinal de confiança explícito do modelo | Confunde dois sinais distintos: `low_confidence` indica incerteza semântica legítima, não falha de formato — misturá-los viola o contrato do `agent.md` |

## Decisão

**Rejeitar quando `type` ou `severity` não estão nos conjuntos de valores válidos definidos pelo agente, ou quando `summary` é vazio.**

Critério implementado em `isValidSchema()` em `solutions/solution-c/utils.js`:

```
type      ∈ {bug, feature, question}       — 'unknown' é INVÁLIDO (aciona retry)
severity  ∈ {critical, medium, low}        — 'unknown' é INVÁLIDO (aciona retry)
component ∈ {frontend, backend, infra, unknown} — 'unknown' é VÁLIDO (por spec)
confidence: número em [0.0, 1.0]
low_confidence: booleano
summary: string não-vazia
reasoning: string (pode ser vazia)
parse_error: ausente ou false
```

Racional:
- `type` e `severity` são os campos que determinam o roteamento Slack (`#incidents`, `#backlog`, `#questions`). Uma classificação com `type=unknown` enviaria a issue para `#backlog` sem qualquer indicação de qual canal é o correto — isso é uma falha de roteamento, não apenas de metadado.
- `component=unknown` não afeta o roteamento e é explicitamente previsto nas regras do prompt ("cannot determine from available context").
- `summary` vazio indica resposta degenerada — o modelo gerou um JSON estruturalmente válido mas semanticamente vazio.

## Consequências

- **Latência no retry path**: quando o modelo retorna um enum inválido (ex: `"type": "incident"`), a solution-c faz uma segunda chamada à API, adicionando ~5–10s. Na prática, o Gemini quase nunca retorna enums inválidos com o prompt atual — o retry path é exercitado principalmente por erros de API (timeout, quota) e não por enum inválido.
- **Assimetria `type`/`severity` vs. `component`**: documentada explicitamente em `utils.js` por comentário inline e aqui no ADR, para evitar confusão futura.
- **`isValidSchema` é chamado sobre o resultado normalizado de `parseGeminiResponse`**: se o modelo retorna `"type": "incident"`, `validateClassification` normaliza para `'unknown'`, e então `isValidSchema` rejeita porque `'unknown' ∉ VALID_TYPES`. O pipeline é linear e sem branching interno.
- **`low_confidence` e `ai_flagged` permanecem sinais distintos**: `low_confidence=true` significa que o modelo classificou com confiança abaixo de 70% — a classificação é aceita, apenas sinalizada para revisão. `ai_flagged=true` significa que ambas as chamadas à API falharam — não há classificação confiável.

## Evidências

- `docs/evidence/solution-c/jest-output.txt` — 29 testes de `isValidSchema` cobrindo todos os casos de borda: `type=unknown` rejeitado, `component=unknown` aceito, `summary` vazio rejeitado, `parse_error` rejeitado, reasoning vazio aceito.
- `docs/evidence/solution-c/sheets-ai-flagged.png` — linha no Google Sheets com `ai_flagged=TRUE`, confirmando que o fallback é acionado quando ambos os retornos da API falham na validação de schema.
- `docs/evidence/solution-c/n8n-execution-log-ai-flagged.png` — execution log mostrando o caminho completo: Attempt 1 → schema inválido → Retry → schema inválido → Build Fallback → Merge.
