# Workflow Runbook

> **Projeto:** Triagem Inteligente de Demandas Academicas
> **Aluno(a):** Carlos Henrique Souza Bispo

---

## Processo obrigatorio de execucao

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief
- [x] Identificar entradas, saidas e restricoes
- [x] Anotar duvidas ou ambiguidades

### Etapa 2: Propor tres solucoes possiveis

- [x] Descrever solution-a (abordagem simples baseada em prompt)
- [x] Descrever solution-b (RAG, ferramenta externa ou base de conhecimento)
- [x] Descrever solution-c (fluxo multi-etapas, validacao ou agente com ferramentas)

### Etapa 3: Registrar cada solucao em pasta separada

- [x] Criar `solutions/solution-a/`
- [x] Criar `solutions/solution-b/`
- [x] Criar `solutions/solution-c/`

### Etapa 4: Implementar prototipos minimos

- [x] Implementar prototipo da solution-a
- [x] Implementar prototipo da solution-b
- [x] Implementar prototipo da solution-c

### Etapa 5: Executar testes

- [x] Criar testes em `tests/`
- [x] Executar testes para cada solucao
- [x] Registrar resultados em `docs/evidence/`

### Etapa 6: Comparar as solucoes

| Criterio | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo | Medio | Medio |
| Complexidade | Baixa | Media | Media/Alta |
| Qualidade da resposta | Media | Boa | Muito boa |
| Riscos | Ambiguidade | Dependencia da base | Maior esforco de implementacao |
| Manutenibilidade | Alta | Media | Alta |
| Adequacao ao problema | Media | Boa | Muito boa |

### Etapa 7: Escolher uma solucao final

- [x] Solucao escolhida: Solution C
- [x] Justificativa: melhor equilibrio entre qualidade, seguranca e rastreabilidade

### Etapa 8: Registrar a decisao em ADR

- [x] Criar `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [x] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [ ] Verificar que cada etapa tem pelo menos um commit
- [ ] Verificar que cada commit contem racionalidade da decisao

#### Sugestao de sequencia de commits

1. `docs: cria mission brief inicial`
2. `docs: adiciona agent md com regras de comportamento`
3. `docs: cria mentorship pack e workflow runbook`
4. `feat(solution-a): implementa prototipo prompt-based`
5. `feat(solution-b): implementa prototipo com base de conhecimento`
6. `feat(solution-c): implementa pipeline multi-etapas`
7. `test: adiciona testes e evidencia de execucao`
8. `docs(adr): registra escolha da solution c`
9. `docs: adiciona merge-readiness pack`
10. `chore: consolida entrega final e README`
