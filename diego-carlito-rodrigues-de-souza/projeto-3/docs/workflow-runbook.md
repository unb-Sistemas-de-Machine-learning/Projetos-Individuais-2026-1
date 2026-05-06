# Workflow Runbook

> **Projeto:** Assistente de Monitoria Universitária Autônomo
> **Aluno(a):** Diego Carlito Rodrigues de Souza

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief
- [x] Identificar entradas, saídas e restrições
- [x] Anotar dúvidas ou ambiguidades

### Etapa 2: Propor três soluções possíveis

- [x] **Descrever solution-a (Abordagem Simples Baseada em Prompt):** Fluxo reativo onde o webhook do n8n recebe a mensagem e repassa para um nó único de LLM responder diretamente.
- [x] **Descrever solution-b (Integração com Base de Conhecimento - RAG):** O LLM atua extraindo o tema da dúvida. O n8n usa essa extração para buscar a política da disciplina em um Google Sheets/Docs. O LLM formula a resposta com base no documento.
- [x] **Descrever solution-c (Fluxo Agêntico Multi-etapas com Roteamento Híbrido):** 
  * **Passo 1 (Decisão):** O LLM 1 atua apenas como classificador, gerando um JSON estruturado com a intenção do aluno.
  * **Passo 2 (Orquestração):** O n8n usa um nó `Switch` para ler o JSON e bifurcar o fluxo.
  * **Passo 3 (Ação):** Dúvidas técnicas acionam o LLM 2 (Prompt Socrático). Exceções e burocracias ignoram o LLM 2, salvam a demanda no banco de dados e notificam o professor via Webhook/Email.
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

| Critério | Solution A (Reativa) | Solution B (RAG) | Solution C (Agente Híbrido) |
|----------|-----------|-----------|-----------|
| **Custo** | Baixo | Médio (2 requisições LLM por vez) | Baixo (Spam e Admin morrem no Switch, sem gastar token extra) |
| **Complexidade** | Baixa | Alta (Sincronizar base de conhecimento) | Média (Exige parser JSON no n8n) |
| **Qualidade da resposta** | Baixa (Risco de alucinar prazos) | Média (Respostas engessadas) | Alta (Respostas segmentadas e Método Socrático) |
| **Riscos** | Alto (Quebra segurança acadêmica) | Médio | Baixo (Escalonamento Humano é determinístico) |
| **Manutenibilidade** | Alta (1 nó) | Baixa (Dependência de planilhas) | Alta (Fluxo visual modular) |
| **Adequação ao problema** | Inadequada | Parcialmente Adequada | **Totalmente Adequada** |

### Etapa 7: Escolher uma solução final

- [x] Solução escolhida: **Solution C (Agente Híbrido com Roteamento)**
- [x] Justificativa: É a única arquitetura que respeita a restrição de não entregar código pronto e de não assumir o papel do professor em burocracias. O LLM é usado inteligentemente para *decidir* o roteamento, e o n8n garante que exceções sejam isoladas do gerador de texto.

### Etapa 8: Registrar a decisão em ADR

- [x] Criar `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [x] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [x] Verificar que cada etapa tem pelo menos um commit
- [x] Verificar que cada commit contém racionalidade da decisão
