# Merge-Readiness Pack

> **Projeto:** Automação Inteligente de Emissão de Notas Fiscais
> **Aluno(a):** Guilherme Westphall
> **Data:** 05/05/2026

---

## 1. Resumo da solução escolhida

A solução final é a **Solution C — dois agentes (Rascunhador e Revisor)**. O fluxo n8n orquestra a busca automática de horas trabalhadas no Productive.io, o cálculo determinístico do valor da nota fiscal, a geração e revisão do rascunho de e-mail por dois agentes de IA independentes, a aprovação humana via Telegram e o envio por Gmail com registro no Google Drive.

O diferencial arquitetural é a separação entre geração (Agente Rascunhador) e validação de conteúdo (Agente Revisor), que reduz o risco de envio de e-mails com tom inadequado ou com dados internos expostos. O comando `edit` no Telegram permite ao usuário solicitar revisão diretamente, sem intervir no fluxo técnico.

Workflow exportado: `automation-invoice-two-agent-review-ngrok.json`

---

## 2. Comparação entre as três alternativas

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| **Abordagem** | Agente único baseado em prompt | Agente com base de conhecimento histórica | Dois agentes: Rascunhador e Revisor |
| **Custo de chamadas ao modelo** | Baixo (1 chamada por execução) | Médio (1 chamada + consulta à base) | Médio (2 chamadas por execução) |
| **Complexidade do workflow** | Baixa | Média | Média |
| **Qualidade do e-mail gerado** | Boa, dependente do prompt | Boa, com referência histórica | Melhor, com revisão dedicada ao conteúdo |
| **Riscos** | E-mail pode passar com problemas sutis | Base vazia nos primeiros ciclos | Custo maior; latência maior |
| **Manutenibilidade** | Alta | Média (exige manutenção da base) | Alta, se responsabilidades documentadas |
| **Adequação ao problema** | Boa | Boa para contexto histórico | Muito boa para qualidade e segurança de conteúdo |
| **Status** | Implementada | Não implementada | Implementada |

**Solução escolhida:** C

**Justificativa:** A Solution C foi escolhida por adicionar uma camada de validação de conteúdo (Agente Revisor) que protege contra problemas sutis no e-mail antes da aprovação humana, e por oferecer ao usuário controle de revisão diretamente pelo Telegram. Ambas as soluções A e C foram implementadas; a C foi adotada como final por ser mais robusta e melhor demonstrar os requisitos do projeto.

---

## 3. Testes executados

| Teste | Descrição | Resultado |
|-------|-----------|-----------|
| Execução com dados reais | Invoice #018, período 16–30/04/2026, 65 horas | Passou — rascunho gerado, revisado e aprovado |
| Comando "edit" no Telegram | Solicitação de revisão do rascunho gerado | Passou — Agente Revisor reformatou e-mail com tom formal |
| Aprovação e envio por Gmail | Comando "approve" após revisão | Passou — e-mail enviado e confirmado pelo Gmail |
| Segunda execução independente | Execução subsequente com aprovação direta | Passou — rascunho gerado, aprovado e enviado sem edição |
| Registro no Google Drive | Log do rascunho após aprovação | Passou — arquivo registrado na pasta Invoices/Draft |

---

## 4. Evidências de funcionamento

| Evidência | Arquivo | Descrição |
|-----------|---------|-----------|
| Mensagem de aprovação inicial | `docs/evidences/evidence1.png` | Telegram com rascunho da Invoice #018, período, horas, valor e instruções de aprovação. |
| Rascunho revisado após "edit" | `docs/evidences/evidence2.png` | Telegram com e-mail reformatado pelo Revisor: tom formal, notas de alteração e campos rastreados. |
| Confirmação de envio | `docs/evidences/evidence3.png` | Telegram confirmando envio bem-sucedido pelo Gmail após aprovação. |
| E-mail enviado (versão inicial) | `docs/evidences/evidence4.png` | Gmail com o primeiro rascunho enviado ao destinatário. |
| E-mail enviado (versão revisada) | `docs/evidences/evidence5.png` | Gmail com o e-mail revisado entregue ao destinatário. |
| Segunda execução aprovada | `docs/evidences/evidence6.png` | Telegram de segunda execução com aprovação e confirmação de envio. |
| Google Drive com rascunhos | `docs/evidences/evidence7.jpeg` | Pasta "Invoices/Draft" com histórico de rascunhos da Invoice-018. |

---

## 5. Limitações conhecidas

- O modelo de linguagem é executado localmente via Ollama, exigindo que o serviço esteja em execução nos horários do agendamento.
- A qualidade da revisão depende do modelo disponível. Modelos menores podem não detectar todos os problemas de conteúdo.
- O comando `edit` no Telegram não tem limite de iterações definido no workflow atual. Em uso real, recomenda-se limitar a 2–3 revisões antes de escalar para revisão manual.
- O fluxo depende de um webhook ativo (ngrok ou equivalente) para receber comandos do Telegram.
- Quem importar o workflow precisa reconfigurar todas as credenciais no n8n, pois elas não estão no JSON exportado.

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Agente retornar JSON malformado | Média | Médio | Nó de normalização de JSON + fallback para `needs_manual_review` |
| Envio de e-mail sem aprovação humana | Baixa | Alto | Bloqueio condicional obrigatório via confirmação no Telegram |
| Ollama indisponível durante execução | Média | Alto | Tratamento de erro HTTP + encaminhamento para revisão manual |
| E-mail com dados internos expostos | Baixa | Médio | Agente Revisor valida ausência de dados sigilosos antes do Telegram |
| Credencial exposta no JSON exportado | Baixa | Alto | Credenciais armazenadas no n8n, não incluídas no JSON |

---

## 7. Decisões arquiteturais

- **ADR-001**: Dois agentes (Rascunhador e Revisor) escolhidos como solução final. Ver [`docs/adr/001-escolha-da-solucao.md`](adr/001-escolha-da-solucao.md).
- Cálculos financeiros são determinísticos e feitos em nós de código, completamente fora do modelo de IA.
- O agente de IA nunca aciona serviços externos diretamente — retorna apenas JSON que o n8n interpreta e roteia.
- Aprovação humana via Telegram é obrigatória antes de qualquer envio externo.
- Tokens e credenciais são armazenados nas credenciais do n8n e não estão presentes no JSON exportado.

---

## 8. Instruções de execução

```text
1. Instalar e iniciar o Ollama com o modelo desejado (ex.: ollama run llama3).
2. Importar automation-invoice-two-agent-review-ngrok.json no n8n.
3. Configurar credenciais no n8n:
   - Telegram Bot Token
   - Gmail OAuth2
   - Google Drive OAuth2
   - Productive.io (X-Auth-Token e X-Organization-Id via HTTP Header Auth)
4. Ajustar as variáveis no nó de configuração:
   - PRODUCTIVE_PERSON_ID
   - HOURLY_RATE
   - CURRENCY
5. Ativar o ngrok (ou expor o webhook por outro meio) para receber respostas do Telegram.
6. Ativar o workflow no n8n.
7. Executar manualmente (botão "Execute Workflow") ou aguardar o agendamento.
8. Verificar a mensagem no Telegram e responder com approve, reject ou edit.
```

---

## 9. Checklist de revisão

- [x] Mission brief atendido
- [x] Três soluções documentadas (A implementada, B proposta, C implementada)
- [x] Testes executados e documentados
- [x] Evidências registradas em `docs/evidences/`
- [x] ADR registrado em `docs/adr/001-escolha-da-solucao.md`
- [x] Commits com mensagens claras por etapa
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido
- [x] Workflow exportado em JSON (`automation-invoice-two-agent-review-ngrok.json`)

---

## 10. Justificativa para merge

O projeto entrega um fluxo de automação completo e funcional que atende a todos os requisitos obrigatórios: n8n como orquestrador, IA influenciando decisões via `recommended_action` (não apenas gerando texto), lógica condicional com múltiplos caminhos, integração com serviços externos reais (Productive.io, Telegram, Gmail, Google Drive), tratamento de erros e fallbacks, e rastreabilidade por meio de logs no Google Drive e aprovação humana explícita via Telegram.

A Solution C (dois agentes) foi testada de ponta a ponta e as evidências estão documentadas. A Solution A (agente único) permanece como baseline implementado. O processo de construção é auditável: mission brief, agent.md, mentorship pack, workflow runbook, três propostas de solução, ADR e evidências foram produzidos na sequência exigida pelo framework de Engenharia de Software Agêntica.
