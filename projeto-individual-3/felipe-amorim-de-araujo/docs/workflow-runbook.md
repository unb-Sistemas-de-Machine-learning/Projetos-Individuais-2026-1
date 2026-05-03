# Workflow Runbook

> **Projeto:** IssueTriageBot
> **Aluno(a):** Felipe Amorim de Araújo

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [ ] Ler e compreender o mission brief
- [ ] Identificar entradas, saídas e restrições
- [ ] Anotar dúvidas ou ambiguidades

### Etapa 2: Propor três soluções possíveis

- [ ] Descrever solution-a (zero-shot prompt — enviar dados da issue ao Gemini e pedir JSON direto)
- [ ] Descrever solution-b (base de conhecimento — carregar `knowledge-base.json` com issues classificadas anteriormente e injetar exemplos relevantes no prompt em tempo de execução)
- [ ] Descrever solution-c (multi-etapas com validação — chamar Gemini, validar schema JSON, retry em caso de saída inválida, fallback com `ai_flagged=true`)

### Etapa 3: Registrar cada solução em pasta separada

- [ ] Criar `docker-compose.yml` na raiz do projeto para subir o n8n localmente
- [ ] Criar `solutions/solution-a/`
- [ ] Criar `solutions/solution-b/`
- [ ] Criar `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [ ] Implementar protótipo da solution-a (`solutions/solution-a/utils.js` + workflow n8n exportado)
- [ ] Implementar protótipo da solution-b (`solutions/solution-b/utils.js` + workflow n8n exportado)
- [ ] Implementar protótipo da solution-c (`solutions/solution-c/utils.js` + workflow n8n exportado)

### Etapa 5: Executar testes

- [ ] Criar testes Jest em `tests/solution-a/`, `tests/solution-b/`, `tests/solution-c/`
- [ ] Executar testes para cada solução (`npm test`)
- [ ] Registrar resultados em `docs/evidence/`

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo — 1 call/issue, prompt mínimo | Médio — 1 call/issue com prompt maior + custo de manter a base | Médio — até 2 calls/issue no retry path |
| Complexidade | Baixa — apenas prompt + parse | Média — requer criação e manutenção do `knowledge-base.json` | Alta — validação de schema + retry + fallback |
| Qualidade da resposta | Baseline — depende do modelo sem guia | Melhor — exemplos reais de issues classificadas guiam o modelo | Alta — validação garante JSON sempre válido |
| Riscos | Saída malformada sem validação | Base desatualizada ou enviesada degrada a qualidade | Maior latência no retry path |
| Manutenibilidade | Alta — prompt simples de ajustar | Média — base precisa de curadoria contínua | Baixa — mais código, mais pontos de falha |
| Adequação ao problema | Aceitável para MVP | Boa para consistência de classificação com exemplos reais | Ótima para produção robusta |

### Etapa 7: Escolher uma solução final

- [ ] Solução escolhida: 
- [ ] Justificativa: 

### Etapa 8: Registrar a decisão em ADR

- [ ] Criar `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [ ] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [ ] Verificar que cada etapa tem pelo menos um commit
- [ ] Verificar que cada commit contém racionalidade da decisão
