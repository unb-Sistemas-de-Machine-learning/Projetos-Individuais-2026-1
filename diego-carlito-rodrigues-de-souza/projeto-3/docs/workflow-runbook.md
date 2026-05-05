# Workflow Runbook

> **Projeto:** Assistente de Monitoria Universitária Autônomo
> **Aluno(a):** Diego Carlito Rodrigues de Souza

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [ ] Ler e compreender o mission brief
- [ ] Identificar entradas, saídas e restrições
- [ ] Anotar dúvidas ou ambiguidades

### Etapa 2: Propor três soluções possíveis

- [ ] **Descrever solution-a (Abordagem Simples Baseada em Prompt):** Fluxo reativo onde o webhook do n8n recebe a mensagem e repassa para um nó único de LLM responder diretamente.
- [ ] **Descrever solution-b (Integração com Base de Conhecimento - RAG):** O LLM atua extraindo o tema da dúvida. O n8n usa essa extração para buscar a política da disciplina em um Google Sheets/Docs. O LLM formula a resposta com base no documento.
- [ ] **Descrever solution-c (Fluxo Agêntico Multi-etapas com Roteamento Híbrido):** 
  * **Passo 1 (Decisão):** O LLM 1 atua apenas como classificador, gerando um JSON estruturado com a intenção do aluno.
  * **Passo 2 (Orquestração):** O n8n usa um nó `Switch` para ler o JSON e bifurcar o fluxo.
  * **Passo 3 (Ação):** Dúvidas técnicas acionam o LLM 2 (Prompt Socrático). Exceções e burocracias ignoram o LLM 2, salvam a demanda no banco de dados e notificam o professor via Webhook/Email.
### Etapa 3: Registrar cada solução em pasta separada

- [ ] Criar `solutions/solution-a/`
- [ ] Criar `solutions/solution-b/`
- [ ] Criar `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [ ] Implementar protótipo da solution-a
- [ ] Implementar protótipo da solution-b
- [ ] Implementar protótipo da solution-c

### Etapa 5: Executar testes

- [ ] Criar testes em `tests/`
- [ ] Executar testes para cada solução
- [ ] Registrar resultados em `docs/evidence/`

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | | | |
| Complexidade | | | |
| Qualidade da resposta | | | |
| Riscos | | | |
| Manutenibilidade | | | |
| Adequação ao problema | | | |

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
