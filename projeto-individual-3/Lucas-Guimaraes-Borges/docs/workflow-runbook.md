# Workflow Runbook

> **Projeto:** Triagem Inteligente de Emails da Codzz

## Processo obrigatório de execução

### Etapa 1: Ler Mission Brief

- [x] Objetivo, limites e critérios compreendidos

### Etapa 2: Propor três soluções

- [x] `solution-a`: prompt/rules simples
- [x] `solution-b`: classificação com base de conhecimento
- [x] `solution-c`: pipeline multi-etapas com validação

### Etapa 3: Registrar em pastas separadas

- [x] `solutions/solution-a/`
- [x] `solutions/solution-b/`
- [x] `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [x] Prototipos executaveis via CLI

### Etapa 5: Executar testes

- [x] Testes em `tests/test_solutions.py`
- [x] Resultados registrados em `docs/evidence/test-results.md`

### Etapa 6: Comparar soluções

| Criterio | Solution A | Solution B | Solution C |
|----------|------------|------------|------------|
| Custo | Baixo | Médio | Médio |
| Complexidade | Baixa | Media | Media |
| Qualidade da resposta | Média | Média-alta | Alta |
| Riscos | Ambiguidade | Drift da base | Maior manutenção |
| Manutenibilidade | Alta | Média | Alta |
| Adequação ao problema | Média | Alta | Alta |

### Etapa 7: Escolher solução final

- [x] Escolhida: **Solution C**
- [x] Justificativa: melhor controle de qualidade e fallback

### Etapa 8: Registrar ADR

- [x] `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar Merge-Readiness Pack

- [x] `docs/merge-readiness-pack.md`

### Etapa 10: Planejar commits por etapa

- [x] Plano em `docs/evidence/plano-de-commits.md`

