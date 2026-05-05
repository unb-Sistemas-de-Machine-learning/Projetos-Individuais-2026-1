# Casos de Teste — Agente de Validação de Entrega Acadêmica

## Caso 1 — Entrega incompleta

### Entrada

{
  "aluno": "Hian Praxedes",
  "projeto": "Projeto Individual 3",
  "descricao_entrega": "Fiz o README e o workflow no n8n, mas ainda não exportei o JSON nem tirei prints.",
  "link_repositorio": "https://github.com/seu-usuario/seu-repo"
}

### Resultado esperado

- Entrada válida.
- IA classifica como entrega incompleta.
- O fluxo identifica necessidade de correção.
- O resultado é registrado no Google Sheets.
- A rota executada é: Entrega precisa de correções ou revisão humana.

---

## Caso 2 — Entrada inválida

### Entrada

{
  "aluno": "Hian Praxedes",
  "projeto": "Projeto Individual 3",
  "descricao_entrega": "",
  "link_repositorio": "https://github.com/seu-usuario/seu-repo"
}

### Resultado esperado

- Entrada inválida.
- O fluxo não chama a IA.
- O resultado é registrado no Google Sheets.
- A rota executada é: Entrada inválida registrada para revisão humana.

---

## Caso 3 — Entrega completa

### Entrada

{
  "aluno": "Hian Praxedes",
  "projeto": "Projeto Individual 3",
  "descricao_entrega": "Concluí README, agent.md, mission brief, mentorship pack, workflow runbook, três soluções, workflow n8n exportado em JSON, prints, Google Sheets, tratamento de erro, ADR, relatório técnico, merge-readiness-pack, commits e PR.",
  "link_repositorio": "https://github.com/seu-usuario/seu-repo"
}

### Resultado esperado

- Entrada válida.
- IA classifica como entrega completa.
- O fluxo identifica que não há pendências críticas.
- O resultado é registrado no Google Sheets.
- A rota executada é: Entrega validada sem pendências críticas.