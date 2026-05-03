# Mentorship Pack

> **Projeto:** IssueTriageBot
> **Aluno(a):** Felipe Amorim de Araújo

---

## 1. Orientações de julgamento

_Como o agente deve tomar decisões? Quais valores priorizar?_

- Explicar a decisão técnica antes de implementar qualquer coisa — nunca implementar e justificar depois
- Usar os critérios do mission-brief como referência objetiva ao comparar soluções (latência <30s, custo, manutenibilidade)
- Não pular etapas do workflow-runbook mesmo que a solução pareça óbvia — o processo de comparação é parte obrigatória da entrega
- Não esconder incertezas: se há dúvida sobre a melhor abordagem, registrar explicitamente no commit ou no ADR

---

## 2. Padrões de arquitetura

_Qual estilo de arquitetura o agente deve seguir?_

- n8n roda via Docker Compose — o `docker-compose.yml` deve estar na raiz do projeto e ser commitado
- Pipeline linear no n8n: cada nó tem responsabilidade única (trigger, prompt builder, chamada Gemini, parser, router Slack, logger Sheets)
- Cada solução implementada em pasta isolada (`solutions/solution-a/`, `solutions/solution-b/`, `solutions/solution-c/`) — sem dependências cruzadas entre soluções
- Lógica reutilizável extraída para `utils.js` dentro da pasta de cada solução; Code nodes do n8n chamam essas funções
- Exportar o workflow n8n como `.json` — é evidência obrigatória de cada protótipo

---

## 3. Padrões de código

_Convenções de código que o agente deve respeitar._

- Linguagem: JavaScript (ES2020+, sem TypeScript) — tanto nos Code nodes do n8n quanto nos scripts utilitários
- Estilo: funções puras em `utils.js`, sem side effects; Code nodes retornam sempre `return [{ json: ... }]`; nomes de variáveis descritivos
- Testes: Jest em `tests/<solution>/` por solução, cobrindo os 3 tipos de issue (`bug`, `feature`, `question`) mais casos-limite (entrada vazia, `title` ausente, issue completamente ambígua)

---

## 4. Estilo de documentação

_Como o agente deve documentar seu trabalho?_

- Commits devem registrar a racionalidade da decisão, não apenas o que foi feito (ex: "Implementa solution-a com zero-shot — baseline para comparação" em vez de "adiciona arquivos")
- Decisões arquiteturais relevantes vão em ADRs em `docs/adr/`
- Alternativas descartadas devem ser registradas explicitamente — no ADR da solução final ou no commit da etapa de comparação
- Marcar os checkboxes do workflow-runbook no commit correspondente a cada etapa concluída

---

## 5. Qualidade esperada

_Qual o nível de qualidade mínimo para considerar uma entrega aceitável?_

- Cada solução tem protótipo funcional e resultado de teste documentado antes de ser descartada
- Comparação entre soluções baseada em critérios mensuráveis — não em preferência subjetiva
- Evidências reais (screenshots, exports `.json`, logs) para cada critério de aceitação do mission-brief
- Testes Jest passando para os utilitários de cada solução
- Ao menos um caso `ai_flagged=true` evidenciado (falha da API Gemini após retry)

---

## 6. Exemplos de boas respostas

```
Exemplo 1 — Decisão antes de implementar:
"Antes de partir para a Solution B com base de conhecimento, vou implementar e testar
a Solution A com zero-shot para estabelecer um baseline de qualidade. Só com esse
resultado consigo medir se o custo de manter um knowledge-base.json curado compensa."

Exemplo 2 — Registrando incerteza:
"Não tenho certeza se a validação de schema JSON resolve o problema de saídas
malformadas com frequência suficiente para justificar o retry extra. Vou registrar
esse risco no ADR e evidenciar com os resultados dos testes."
```

---

## 7. Exemplos de más respostas

```
Exemplo 1 — Pular direto para a solução mais complexa:
"Vou implementar a Solution C com validação de schema e retry, é claramente a melhor — não preciso testar as outras."

Por quê é ruim: não há evidência ainda — pula o processo de comparação exigido
pelo runbook e assume uma conclusão sem baseline.

Exemplo 2 — Implementar sem explicar:
[cria arquivos em solutions/solution-b/ sem nenhum commit ou comentário explicando
o que foi feito e por quê]

Por quê é ruim: viola o princípio de registrar decisões; impossível auditar depois.
```

---

## 8. Princípios-guia

```
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas.
O agente deve registrar alternativas descartadas.
O agente não deve pular etapas do workflow-runbook mesmo quando a solução parecer óbvia.
O agente deve marcar os checkboxes do workflow-runbook conforme avança — ao menos um commit por solução implementada.
```
