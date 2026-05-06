# ADR-005: Estratégia de Seleção de Exemplos para o Prompt Few-Shot

## Status
Aceito

## Contexto

A solution-b implementa um prompt few-shot no qual exemplos de issues previamente classificadas são injetados em tempo de execução antes da issue a ser analisada. O runbook define a solução como: "carregar `knowledge-base.json` com issues classificadas anteriormente e injetar **exemplos relevantes** no prompt em tempo de execução."

A palavra "relevantes" impõe uma escolha de design real: como selecionar, dentre os N exemplos da KB, os K mais adequados para a issue recebida? Essa decisão impacta diretamente a qualidade das classificações geradas pelo Gemini, o tamanho do prompt, e a manutenibilidade do código.

Restrições relevantes:
- O Code node do n8n executa em sandbox VM e não pode `require()` arquivos externos — toda lógica precisa ser inlinada.
- A KB tem 7 entradas (curadas manualmente). Não há embeddings, índice vetorial, nem chamadas adicionais à API.
- Custo: a solution-b deve manter 1 call/issue (o retry da Gemini é responsabilidade da solution-c).
- Latência: a seleção ocorre em memória, deve ser sub-milissegundo.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| **Sempre incluir todos os exemplos (estático)** | Determinístico, zero código de seleção, sem risco de selecionar mal | Prompt sempre maior (todos 7 exemplos); descaracteriza "exemplos relevantes em runtime" — a solução seria apenas um prompt zero-shot mais longo, não uma base de conhecimento |
| **Estratificado por tipo (1 por tipo, fixo)** | Determinístico, cobertura de tipo garantida, trivial de implementar | Ignora qualquer sinal de relevância da issue recebida; selecionar sempre os mesmos 3 exemplos independentemente da issue não diferencia solution-b da abordagem estática |
| **Overlap ponderado de tokens e labels (escolhido)** | Reusa labels (sinal forte — o próprio valor que estamos predizendo); determinístico; sem infraestrutura extra; testável | Pesos `3-2-1` são arbitrários; instável em títulos de 2-3 tokens sem stop-words; pode retornar exemplos não-ideais para issues muito genéricas |
| **TF-IDF** | Mais robusto que overlap raw, pondera raridade dos tokens | Requer contagem de frequência em corpus; overengineering para 7 entradas; adiciona código sem ganho mensurável em KB pequena |
| **Embeddings / similaridade semântica** | Melhor relevância semântica, não literal | Exige modelo de embedding (outra chamada de API) e cache; adiciona latência e custo; não compatível com o Code node sem dependência externa |

## Decisão

**Overlap ponderado de tokens e labels, top-K=3, com fallback determinístico.**

Algoritmo de scoring por entrada da KB:

```
score = LABEL_WEIGHT (3) × |labels_inter|
      + TITLE_WEIGHT (2) × |title_token_inter|
      + BODY_WEIGHT  (1) × |body_token_inter|
```

Detalhes de implementação:
- Tokenização: `text.toLowerCase().match(/[a-z0-9]+/g)`, tokens de comprimento < 2 descartados.
- Stop-words filtradas: `{the, is, a, an, on, in, to, of, and, or, for, with, when, this, that, it, my, i, be, but, not}`.
- Ordenação: `(score DESC, kbIndex ASC)` — tiebreak determinístico por índice original.
- Fallback: se `top_score == 0`, retorna `kb.slice(0, 3)` — a KB é curada de modo que os 3 primeiros exemplos cubram os 3 tipos (`bug`, `feature`, `question`), garantindo fallback útil.

Racional dos pesos:
- `label=3`: um label como `bug` ou `feature` é literalmente um dos valores que estamos predizendo no campo `type` — é o sinal mais direto disponível.
- `title=2`: títulos tendem a conter palavras-chave discriminantes (ex: "crash", "add dark mode", "how do I") com pouco ruído.
- `body=1`: corpos são mais verbosos e ruidosos; contribuem com sinal mas mais fraco.

## Consequências

- **Drift entre arquivo e Code node**: a KB existe em duas formas — `knowledge-base.json` (canônico, usado pelos testes) e inlinada como literal JS no nó "Build Prompt" do n8n (usada em produção). Editar uma sem a outra cria divergência silenciosa. Mitigação: ao atualizar a KB, sempre rodar `npm run test:solution-b` E re-exportar o workflow do n8n. A invariante de cobertura é validada automaticamente pelos testes.
- **Pesos `3-2-1` são constantes nomeadas**: `LABEL_WEIGHT`, `TITLE_WEIGHT`, `BODY_WEIGHT` — explicitamente documentados e ajustáveis sem risco de silenciar a lógica.
- **Curadoria contínua**: a KB precisa ser mantida atualizada com exemplos representativos. Entradas desatualizadas ou enviesadas degradam a qualidade silenciosamente. O campo `_rationale` em cada entrada documenta por que ela existe.
- **Primeiro 3 exemplos são invariante**: `examples[0]` = bug, `examples[1]` = feature, `examples[2]` = question — validado por teste em `tests/solution-b/knowledge-base.test.js`. Inserir novas entradas antes do índice 2 quebra o fallback.

## Evidências

- `docs/evidence/solution-b/jest-output.txt` — saída completa do Jest incluindo os 12 testes de `selectExamples` que validam scoring, determinismo, fallback e case-insensitivity.
- `docs/evidence/solution-b/n8n-execution-log-bug.png` — execution log mostrando `meta.examples_used: 3` no nó "Build Prompt".
- `docs/evidence/solution-b/prompt-sample.txt` — conteúdo do campo `prompt` capturado do execution log, confirmando os 3 exemplos injetados e o bloco "Examples of correctly classified issues:".
