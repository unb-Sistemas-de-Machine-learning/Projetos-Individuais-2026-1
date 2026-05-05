# Workflow Runbook

> **Projeto:** Curadoria Automática de Artigos Científicos
> **Aluno(a):** Carlos Eduardo Rodrigues

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief
- [x] Identificar entradas, saídas e restrições
- [x] Anotar dúvidas ou ambiguidades

### Etapa 2: Propor três soluções possíveis

- [x] Descrever solution-a (abordagem simples baseada em prompt)
- [x] Descrever solution-b (RAG, ferramenta externa ou base de conhecimento)
- [x] Descrever solution-c (fluxo multi-etapas, validação ou agente com ferramentas)

### Etapa 3: Registrar cada solução em pasta separada

- [x] Criar `solutions/solution-a/`
- [x] Criar `solutions/solution-b/`
- [x] Criar `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [x] Implementar protótipo da solution-a
- [x] Implementar protótipo da solution-b
- [x] Implementar protótipo da solution-c

### Etapa 5: Executar testes

- [x] Criar testes em `tests/`
- [x] Executar testes para cada solução
- [x] Registrar resultados em `docs/evidence/`

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo | Médio | Médio |
| Complexidade | Baixa | Média | Alta |
| Qualidade da resposta | Boa para triagem simples | Melhor para contexto bibliográfico | Melhor equilíbrio entre robustez e controle |
| Riscos | Alucinação e baixa precisão em casos ambíguos | Dependência da qualidade da base | Maior custo de implementação |
| Manutenibilidade | Alta | Média | Média |
| Adequação ao problema | Parcial | Boa | Excelente |

### Etapa 7: Escolher uma solução final

- [x] Solução escolhida: `solution-c`
- [x] Justificativa: a curadoria cientifica exige validacao, rastreabilidade e fallback humano quando a confianca for baixa

### Etapa 8: Registrar a decisão em ADR

- [x] Criar `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [x] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [x] Verificar que cada etapa tem pelo menos um commit
- [x] Verificar que cada commit contém racionalidade da decisão