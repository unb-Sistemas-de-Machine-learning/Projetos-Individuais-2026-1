# Workflow Runbook

> **Projeto:** Triagem de suporte técnico (n8n + IA)
> **Aluno(a):** Patricia Helena Macedo da Silva
> **Matrícula:** 221037993

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief em `docs/mission-brief.md`
- [x] Identificar entradas, saídas e restrições
- [x] Anotar dúvidas ou ambiguidades (se houver, perguntar à professora)

### Etapa 2: Propor três soluções possíveis

- [x] **Solution A:** prompt único + classificação + Switch (ver `solutions/solution-a/README.md`)
- [x] **Solution B:** classificação + leitura de FAQ no Google Sheets + segunda chamada contextual (ver `solutions/solution-b/README.md`)
- [x] **Solution C:** duas etapas de IA (classificar depois redigir resposta com validação) (ver `solutions/solution-c/README.md`)

### Etapa 3: Registrar cada solução em pasta separada

- [x] `solutions/solution-a/`
- [x] `solutions/solution-b/`
- [x] `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [x] Workflow JSON referência A: `src/workflows/solution-a-prompt-simples.json`
- [x] Workflow JSON referência B: `src/workflows/solution-b-faq-sheets.json`
- [x] Workflow JSON referência C: `src/workflows/solution-c-multietapas.json`

### Etapa 5: Executar testes

- [x] Criar testes em `tests/`
- [x] Executar testes para cada solução
- [x] Registrar resultados em `docs/evidence/`

### Etapa 6: Comparar as soluções


| Critério                  | Solution A                | Solution B                       | Solution C                      |
| ------------------------- | ------------------------- | -------------------------------- | ------------------------------- |
| **Custo (tokens)**        | Menor                     | Médio                            | Maior                           |
| **Complexidade**          | Baixa                     | Média                            | Alta                            |
| **Qualidade da resposta** | Boa para roteamento       | Melhor UX com FAQ real           | Muito boa, porém mais cara      |
| **Riscos**                | Menos contexto ao usuário | Dependência da planilha FAQ      | Dois pontos de falha LLM        |
| **Manutenibilidade**      | Alta                      | Média (planilha viva)            | Média                           |
| **Adequação ao problema** | Ótima para MVP            | **Ótima para portfólio/entrega** | Ótima se orçamento de tokens ok |


### Etapa 7: Escolher uma solução final

- **Solução escolhida:** **B** (ver `docs/adr/001-escolha-da-solucao.md`)

**Justificativa detalhada:**

1. **Atendimento aos requisitos do projeto:**
   - Integração com base de conhecimento real (FAQ em Google Sheets)
   - IA usada como **decisão**, não apenas resposta (classificação → roteamento)
   - Segunda chamada IA influencia conteúdo, não é apenas decorativa
   - Lógica de decisão com Switch condicionado por urgência/confiança

2. **Balanceamento custo-benefício:**
   - Solução A é simples, mas perde contexto; resposta genérica ao usuário
   - Solução B oferece **melhor experiência UX** (FAQ contextual) com custo moderado (2 chamadas API)
   - Solução C é mais cara (2 LLMs sequenciais sem FAQ nativo) e complexa demais para este escopo

3. **Manutenibilidade e escalabilidade:**
   - FAQ em Sheets é vivo e editável por não-técnico
   - Fácil adicionar novas categorias de perguntas
   - Menos código customizado que Solução C

4. **Demonstração de competência:**
   - RAG leve (padrão da indústria)
   - Integração multi-serviço (Gemini + Sheets)
   - Tratamento de fallback e confiança
   - Auditoria completa em Sheets

5. **Adequação ao portfolio acadêmico:**
   - Solução B é a mais adequada para demonstrar conhecimento de **IA em fluxos reais**
   - Não é trivial como A, nem over-engineered como C

### Etapa 8: Registrar a decisão em ADR

- [x] Criar `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [x] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- Verificar commits conforme orientação da disciplina (mensagens claras + racionalidade)