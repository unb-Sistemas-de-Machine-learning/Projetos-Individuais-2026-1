# ADR-006: Formato do Prompt Few-Shot

## Status
Aceito

## Contexto

Com a decisão de injetar exemplos da KB no prompt (ADR-005), restou definir **como** esses exemplos são formatados e **onde** são inseridos na estrutura do prompt. Essa decisão afeta:

- A clareza da instrução para o Gemini (afeta qualidade da classificação).
- O tamanho do prompt e o orçamento de tokens.
- A compatibilidade com o contrato de saída JSON estrito definido em `agent.md`.
- A manutenibilidade do template em `utils.js` e no Code node do n8n.

A solution-a usa um prompt com issue data no topo, seguida de schema, regras e instrução final. A solution-b precisa reestruturar esse template para comportar exemplos de forma coerente.

## Alternativas consideradas

### Posicionamento do bloco de exemplos

| Opção | Prós | Contras |
|-------|------|---------|
| Exemplos **antes** das regras de classificação | Modelo vê exemplos antes de entender as definições | Pode confundir se o modelo tentar aplicar os exemplos antes de ler as regras |
| Exemplos **depois** das regras e **antes** da issue real (escolhido) | Fluxo lógico: instruções → definições → exemplos → tarefa; exemplos contextualizam as regras antes de aplicá-las | Prompt maior; issue fica no final |
| Exemplos **depois** da issue real | Issue fica no topo como na solution-a | Modelo vê a tarefa antes de ver os exemplos — padrão menos natural para few-shot |

### Formato de serialização dos exemplos

| Opção | Prós | Contras |
|-------|------|---------|
| **JSON pretty-printed sem markdown fence (escolhido)** | Compatível com o contrato de saída (agent.md proíbe markdown ao redor do JSON); legível; sem ambiguidade sobre o que é instrução vs. dado | — |
| JSON em code fence markdown ` ```json ` | Visual | Conflita com a regra "Return ONLY the JSON object" — poderia induzir o Gemini a envolver a saída em code fences |
| YAML | Compacto | Formato diferente do JSON de saída; pode confundir o modelo |
| Texto livre descritivo | Mais legível para humanos | Ambíguo; o modelo pode não extrair os valores corretos |

### Truncamento do corpo dos exemplos

| Opção | Prós | Contras |
|-------|------|---------|
| Sem truncamento | Exemplos completos, preserva contexto | Um único exemplo com corpo de 2000 chars pode estourar o orçamento de tokens com 3 exemplos |
| **Truncar em 300 chars (escolhido)** | Prompt previsível; os primeiros 300 chars capturam a essência da issue na maioria dos casos | Pode perder contexto crítico em issues muito detalhadas |
| Truncar em 150 chars | Mais compacto | Muitas vezes insuficiente para transmitir o contexto do exemplo |

## Decisão

**Bloco de exemplos entre as regras de classificação e a issue a ser classificada; classificação serializada como JSON pretty-printed sem markdown fence; corpo de exemplo truncado em 300 chars.**

Estrutura completa do prompt (solution-b):

```
You are an issue classifier for a software project. Analyze the GitHub issue below
and return a JSON classification.

Return ONLY a valid JSON object with this exact structure:
{ "type": ..., "severity": ..., ... }

Classification rules:
- type=bug: ...
- ...
- component=unknown: ...

Examples of correctly classified issues:

Example 1:
Issue Title: <title do exemplo>
Issue Body: <body truncado em 300 chars>
Labels: <labels>
Classification:
{
  "type": "bug",
  "severity": "critical",
  "component": "backend",
  "summary": "...",
  "reasoning": "..."
}

Example 2:
...

Now classify this issue:

Issue Title: <issue real>
Issue Body: <body da issue real>
Labels: <labels da issue real>
Repository: <repositório>

Return ONLY the JSON object. No markdown code blocks, no prose outside the JSON.
```

Detalhes:
- O bloco de exemplos é omitido completamente quando `examples = []` — o prompt fica identico à chamada sem exemplos (auto-consistência testada em `tests/solution-b/utils.test.js`).
- A classificação de cada exemplo inclui apenas os campos `type`, `severity`, `component`, `summary`, `reasoning` — não inclui `confidence` e `low_confidence` (campos de metadado, não de triagem).
- O símbolo de ellipsis para truncamento é `…` (U+2026) — um único caractere, não `...` (três pontos), para manter consistência visual.
- O tamanho total do prompt com 3 exemplos no pior caso (300 chars de body cada) é validado em teste: `< 8000 chars`.

## Consequências

- **Prompt ~1.5–2 kB maior por chamada** do que na solution-a (com 3 exemplos típicos). Custo de tokens ligeiramente superior, mas dentro dos limites do Gemini Flash Lite free tier.
- **Issue data no final do prompt** (após exemplos), em contraste com a solution-a onde aparecia no topo. Isso é intencional: o padrão few-shot canônico posiciona os exemplos antes da tarefa ("instrução → exemplos → tarefa a resolver").
- **Confidência e low_confidence omitidos dos exemplos** para evitar que o Gemini calibre sua própria confiança baseado nos valores dos exemplos (que são fixos e não refletem a dificuldade da issue atual).
- **Manutenção do template**: qualquer mudança na estrutura do prompt precisa ser refletida tanto em `solutions/solution-b/utils.js` quanto no jsCode do nó "Build Prompt" no n8n — mesma duplicação já existente na solution-a.

## Evidências

- `docs/evidence/solution-b/jest-output.txt` — testes `buildPrompt with examples` validando: header correto, numeração dos exemplos, truncamento, posicionamento antes de "Now classify this issue:", tamanho total < 8000 chars.
- `docs/evidence/solution-b/prompt-sample.txt` — conteúdo real do prompt enviado ao Gemini capturado do execution log do n8n, demonstrando a estrutura escolhida com 3 exemplos injetados.
