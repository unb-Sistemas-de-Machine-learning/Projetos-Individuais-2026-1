# Workflow Runbook

> **Projeto:** Triagem Inteligente de Chamados de Suporte
> **Aluno(a):** Gabryel Nicolas Soares de Sousa

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief
- [x] Identificar entradas, saídas e restrições
- [x] Anotar dúvidas ou ambiguidades

**Resultado:** O sistema deve receber mensagens via webhook, usar IA para classificar por categoria e urgência, e rotear automaticamente entre notificação por email (urgente) e registro no Sheets (demais casos), com fallback para entradas inválidas ou de baixa confiança.

---

### Etapa 2: Propor três soluções possíveis

- [x] Descrever solution-a (abordagem simples baseada em prompt)
- [x] Descrever solution-b (RAG, ferramenta externa ou base de conhecimento)
- [x] Descrever solution-c (fluxo multi-etapas, validação ou agente com ferramentas)

**Resultado:** Três abordagens documentadas em `solutions/` antes de qualquer implementação.

---

### Etapa 3: Registrar cada solução em pasta separada

- [x] Criar `solutions/solution-a/`
- [x] Criar `solutions/solution-b/`
- [x] Criar `solutions/solution-c/`

---

### Etapa 4: Implementar protótipos mínimos

- [x] Implementar protótipo da solution-a (workflow completo no n8n)
- [x] Implementar protótipo da solution-b (descrito e prototipado)
- [x] Implementar protótipo da solution-c (descrito e prototipado)

---

### Etapa 5: Executar testes

- [x] Criar testes em `tests/`
- [x] Executar testes para cada solução
- [x] Registrar resultados em `docs/evidence/`

---

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo (1 chamada/request) | Médio (1 chamada + consulta Sheets) | Alto (até 3 chamadas com retry) |
| Complexidade | Baixa | Média | Alta |
| Qualidade da resposta | Boa | Muito boa | Muito boa |
| Riscos | Depende do prompt | Depende do FAQ atualizado | Maior superfície de falha |
| Manutenibilidade | Alta | Média | Baixa |
| Adequação ao problema | Suficiente | Boa | Excessiva para o escopo |

---

### Etapa 7: Escolher uma solução final

- [x] Solução escolhida: **Solution-A**
- [x] Justificativa: Atende todos os requisitos obrigatórios com menor complexidade e custo. A manutenibilidade alta e o fluxo linear facilitam auditoria e depuração. Os elementos de tratamento de erro foram incorporados da solution-c sem aumentar a complexidade geral.

---

### Etapa 8: Registrar a decisão em ADR

- [x] Criar `docs/adr/001-escolha-da-solucao.md`

---

### Etapa 9: Gerar o Merge-Readiness Pack

- [x] Preencher `docs/merge-readiness-pack.md`

---

### Etapa 10: Fazer commits separados por etapa

- [x] Verificar que cada etapa tem pelo menos um commit
- [x] Verificar que cada commit contém racionalidade da decisão
