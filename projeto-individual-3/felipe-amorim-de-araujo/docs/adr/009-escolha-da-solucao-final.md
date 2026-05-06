# ADR-009: Comparação das Três Soluções e Escolha da Solução Final

## Status
Aceito

## Contexto

O workflow-runbook exige que as três soluções sejam implementadas, testadas com
fluxo end-to-end completo (GitHub webhook → Gemini → Slack + Sheets) e comparadas
em critérios mensuráveis antes de eleger uma solução final. Este ADR fecha o ciclo
das etapas 6 e 7 do runbook, citando evidências coletadas durante a execução real
de cada solução.

As três abordagens exploradas:

- **Solution A (zero-shot):** prompt mínimo enviado diretamente ao Gemini; parse
  defensivo normaliza saídas inválidas para `unknown` sem sinalização.
- **Solution B (few-shot com knowledge base):** carrega `knowledge-base.json` com
  7 issues classificadas; seleciona os 3 exemplos mais relevantes por scoring de
  overlap ponderado (labels ×3, título ×2, corpo ×1) e injeta no prompt em runtime.
- **Solution C (validação de schema + retry + fallback):** mesma abordagem de prompt
  da solution-a, mas adiciona validação estrita pós-parse, retry automático quando
  o schema é inválido, e fallback explícito com `ai_flagged=true` quando ambas as
  tentativas falham.

---

## Comparação por critério

### Custo (chamadas à API e tamanho de prompt)

| | Solution A | Solution B | Solution C |
|---|---|---|---|
| Calls/issue (caminho normal) | 1 | 1 | 1 |
| Calls/issue (caminho retry) | — | — | 2 |
| Tokens estimados/call | ~650 | ~1 500 (+ 3 exemplos) | ~650 |
| Custo relativo | Baixo | Médio | Baixo no happy path; Médio no retry path |

Solution-b é a mais cara por call — o prompt com 3 exemplos injetados (~850 tokens
extras) aumenta o custo por requisição em ~30% comparado a A e C. Solution-c incorre
em custo duplo apenas quando a Gemini retorna schema inválido, que na prática ocorreu
0 vezes nas execuções normais dos 4 casos de teste — o retry path foi exercitado
apenas forçando uma chave inválida.

**Vencedor por custo: A ≈ C (happy path) < B**

---

### Complexidade de implementação

| | Solution A | Solution B | Solution C |
|---|---|---|---|
| `utils.js` (linhas) | 202 | 300 | 261 |
| `workflow.json` (linhas) | 172 | 172 | 334 |
| Nós no workflow n8n | 7 | 7 | 14 |
| Testes Jest | 49 | 82 | 92 |
| Artefatos extras | — | `knowledge-base.json` | — |

Solution-c tem o dobro de nós no workflow (14 vs 7), dois nós IF e dois nós Merge
que não existem nas outras. A lógica de branching é a principal fonte de complexidade
— qualquer alteração no fluxo precisa ser consistente em ambos os caminhos (attempt-1
e retry). Solution-b adiciona complexidade em código JS (scoring de exemplos, stop-words,
normalização de labels) mas mantém o workflow linear.

**Vencedor por menor complexidade: A < B < C**

---

### Qualidade da resposta

Observações nos 4 casos de teste executados com fluxo real para cada solução:

| Caso | Solution A | Solution B | Solution C |
|------|-----------|-----------|-----------|
| `[TEST] App crashes on login` | `bug / critical / backend` ✓ | `bug / critical / backend` ✓ | `bug / critical / backend` ✓ |
| `[TEST] Add dark mode support` | `feature / low / frontend` ✓ | `feature / low / frontend` ✓ | `feature / low / frontend` ✓ |
| `[TEST] How do I reset my password?` | `question / low / unknown` ✓ | `question / low / unknown` ✓ | `question / low / unknown` ✓ |
| Chave inválida | `n/a — workflow falha no nó HTTP` | `n/a — workflow falha no nó HTTP` | `ai_flagged=true` ✓ |

Os três casos normais produziram classificações idênticas nas três soluções — o modelo
Gemini 2.5 Flash Lite classifica esses exemplos corretamente com ou sem exemplos no
prompt. A vantagem da solution-b (few-shot) seria observável em casos ambíguos onde
o modelo hesita, mas não foi possível medir diferença com os casos de teste padrão
do runbook.

A vantagem mensurável da solution-c: é a única que produz `ai_flagged=true` para
falhas de API, requisito explícito do mission-brief (seção 7) e critério de aceitação
(seção 7, último item). Solutions A e B param o workflow com erro quando a Gemini
retorna 4xx — a falha não chega ao Sheets nem ao Slack.

**Vencedor por qualidade observável: C (único que cobre o caso de falha)**

---

### Riscos

| Risco | Solution A | Solution B | Solution C |
|-------|-----------|-----------|-----------|
| Gemini retorna JSON malformado | Normaliza para `unknown` silenciosamente — roteamento pode errar sem sinalização | Idem A | Detecta via `isValidSchema`, faz retry; se retry também falha, `ai_flagged=true` |
| Rate limit ou chave inválida | Workflow para com erro no nó HTTP — nada chega ao Sheets | Idem A | `continueOnFail=true` permite fluxo continuar até fallback; `ai_flagged=true` no Sheets |
| Knowledge base desatualizada ou enviesada | — | Degrada a qualidade silenciosamente, sem sinal observável | — |
| Latência acima de 30s | Improvável (1 call ~5s) | Improvável (1 call ~7s) | Retry path ~15s — ainda dentro do SLA de 30s do mission-brief |
| Maior número de nós = mais pontos de falha | — | — | IF nodes e Merge nodes são configuração declarativa; risco real está nos Code nodes, dos quais solution-c tem o mesmo número que A |

**Melhor perfil de risco para produção: C**

---

### Manutenibilidade

| | Solution A | Solution B | Solution C |
|---|---|---|---|
| Ajustar o prompt | Editar 1 string em `utils.js` | Editar 1 string + revisar se exemplos ainda são representativos | Editar 1 string em `utils.js` |
| Adicionar novo tipo de issue | Atualizar constantes + prompt | Atualizar constantes + prompt + adicionar exemplos à KB | Atualizar constantes + prompt + atualizar `isValidSchema` |
| Manutenção contínua necessária | Nenhuma | KB precisa ser curada à medida que padrões de issues evoluem | Nenhuma além do código |
| Drift entre artefatos | — | `knowledge-base.json` ↔ inline no workflow — duas fontes de verdade | — |

Solution-b introduz o risco de drift entre a KB em `knowledge-base.json` (usada pelos
testes) e a KB inlinada no Code node do n8n (usada em produção), documentado no ADR-005.
Solution-c não tem artefatos externos além do código.

**Mais manutenível a longo prazo: A ≈ C > B**

---

### Adequação ao problema (mission-brief)

O mission-brief define dois requisitos que distinguem as soluções:

1. *"Retenta a chamada à Gemini API uma vez em caso de falha antes de aplicar fallback"*
   → Apenas a solution-c implementa retry automático.

2. *"Segunda falha aplica defaults e sinaliza `ai_flagged=true` no Sheets"*
   → Apenas a solution-c produz `ai_flagged=true`. Solutions A e B param com erro.

Ambos são critérios de aceitação explícitos (seção 7). Solutions A e B são protótipos
válidos para comparação, mas não atendem integralmente a especificação de produção.

---

## Decisão

**Solução escolhida: Solution C**

A escolha é baseada nos seguintes resultados mensuráveis:

1. **É a única solução que atende todos os critérios de aceitação do mission-brief**,
   incluindo retry automático e `ai_flagged=true` — evidenciado por
   `docs/evidence/solution-c/sheets-ai-flagged.png` e
   `docs/evidence/solution-c/n8n-execution-log-ai-flagged.png`.

2. **No caminho normal (100% dos casos nos testes), a latência é idêntica à
   solution-a** (~5–7s, 1 call à Gemini) — o custo do retry só é pago quando há
   falha real de API, que não ocorreu em nenhuma execução normal.

3. **A complexidade extra do workflow (14 vs 7 nós) é contida e auditável**: os
   dois IF nodes e dois Merge nodes são configuração declarativa no n8n — a lógica
   real reside nos Code nodes, cujo número é idêntico ao das outras soluções.

4. **Sem dependências externas mutáveis**: ao contrário da solution-b, não há
   knowledge base que precise de curadoria contínua. O risco de drift entre artefatos
   é eliminado.

A solution-b permanece como alternativa válida para contextos onde a qualidade de
classificação em casos ambíguos é crítica e há equipe dedicada a manter a KB — mas
esse trade-off não foi evidenciado nos testes realizados, que produziram classificações
idênticas nas três soluções para os casos do runbook.

---

## Consequências

- A solution-c é a implementação de referência para o IssueTriageBot. O
  `merge-readiness-pack.md` descreve o estado desta solução.
- Solutions A e B permanecem em `solutions/` como artefatos do processo de
  comparação — são evidência do framework de "3 soluções descartáveis" exigido
  pelo projeto.
- O ADR não elimina as outras soluções: se os requisitos mudarem (ex: volume alto
  que torna o custo do retry proibitivo), solution-a é a alternativa mais direta.

---

## Evidências

| Artefato | Solução | O que demonstra |
|----------|---------|----------------|
| `docs/evidence/solution-a/jest-output.txt` | A | 49 testes passando |
| `docs/evidence/solution-b/jest-output.txt` | B | 82 testes passando |
| `docs/evidence/solution-c/jest-output.txt` | C | 92 testes passando |
| `docs/evidence/solution-{a,b,c}/github-webhook-delivered.png` | A, B, C | 200 OK nas entregas do GitHub |
| `docs/evidence/solution-{a,b,c}/slack-{incidents,backlog,questions}.png` | A, B, C | Roteamento correto nos 3 canais |
| `docs/evidence/solution-{a,b,c}/sheets-rows.png` | A, B, C | Linhas registradas com todos os campos |
| `docs/evidence/solution-c/sheets-ai-flagged.png` | **C apenas** | `ai_flagged=TRUE` — ausente em A e B |
| `docs/evidence/solution-c/n8n-execution-log-ai-flagged.png` | **C apenas** | Caminho retry → fallback executado |
