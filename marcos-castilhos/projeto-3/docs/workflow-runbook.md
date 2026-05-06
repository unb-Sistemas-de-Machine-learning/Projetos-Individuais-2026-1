# Workflow Runbook

> **Projeto:** logFinanceiro -Automação Financeira Pessoal com n8n e Agentes de IA
> **Aluno(a):** Marcos Antonio Teles de Castilhos

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief  

- [x] Identificar entradas, saídas e restrições  

- [x] Anotar dúvidas ou ambiguidades

### Etapa 2: Propor três soluções possíveis

- [X] Descrever solution-a (abordagem simples baseada em prompt)
- [X] Descrever solution-b (RAG, ferramenta externa ou base de conhecimento)
- [X] Descrever solution-c (fluxo multi-etapas, validação ou agente com ferramentas)

### Etapa 3: Registrar cada solução em pasta separada

- [X] Criar `solutions/solution-a/`
- [X] Criar `solutions/solution-b/`
- [X] Criar `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [X] Implementar protótipo da solution-a
- [X] Implementar protótipo da solution-b
- [X] Implementar protótipo da solution-c

### Etapa 5: Executar testes

- [X] Criar testes em `tests/`
- [X] Executar testes para cada solução
- [X] Registrar resultados em `docs/evidence/`

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Abordagem | Extração livre | Contextual | Validação estrita (Compilador) |
| Custo | Baixo | Alto | Baixo |
| Complexidade | Baixa | Alta | Média |
| Qualidade da resposta | Inconsistente | Arriscada (Alucinação) | Determinística |
| Riscos | Quebra de integração | Invenção de dados | Falha no pre-parse de áudio |
| Manutenibilidade | Ruim | Péssima | Excelente |
| Adequação ao problema | Baixa | Baixa | Máxima |  Solução escolhida: C  Justificativa: Garantia arquitetural de persistência limpa e tratamento holístico de erros sem complexidade acidental. 

### Etapa 7: Escolher uma solução final

[x] Solução escolhida: Solution C (Fluxo Estruturado via Switch)  

[x] Justificativa: Controle determinístico sob ambiente estocástico.

### Etapa 8: Registrar a decisão em ADR

- [X] Criar `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [X] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [X] Verificar que cada etapa tem pelo menos um commit
- [X] Verificar que cada commit contém racionalidade da decisão
