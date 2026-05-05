# Merge-Readiness Pack

> **Projeto:** Triagem Inteligente de Chamados de Suporte
> **Aluno(a):** Gabryel Nicolas Soares de Sousa
> **Data:** 05/05/2025

---

## 1. Resumo da solução escolhida

Sistema de triagem automática de chamados de suporte implementado no n8n. Recebe mensagens via webhook, usa a API da OpenAI (GPT-3.5-turbo) para classificar a demanda em categoria e urgência, e roteia automaticamente: chamados urgentes geram notificação por email e são registrados no Google Sheets; demais chamados são apenas registrados; entradas inválidas ou de baixa confiança ativam um caminho de fallback com registro para revisão manual.

---

## 2. Comparação entre as três alternativas

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| **Abordagem** | Prompt simples, 1 chamada à IA | IA + consulta a FAQ no Sheets | IA + validação + retry automático |
| **Custo** | Baixo | Médio | Alto |
| **Complexidade** | Baixa | Média | Alta |
| **Qualidade da resposta** | Boa | Muito boa | Muito boa |
| **Riscos** | Depende do prompt | FAQ desatualizado | Maior superfície de falha |
| **Manutenibilidade** | Alta | Média | Baixa |
| **Adequação ao problema** | Suficiente | Boa | Excessiva |

**Solução escolhida:** A

**Justificativa:** A solution-a atende todos os requisitos obrigatórios com menor complexidade e custo. O tratamento de erro explícito foi incorporado da solution-c, eliminando o principal risco sem aumentar a complexidade geral. As demais soluções foram descartadas por adicionar dependências e complexidade desnecessárias para o escopo do projeto.

---

## 3. Testes executados

| Teste | Descrição | Resultado |
|-------|-----------|-----------|
| T1 — Alta urgência | Mensagem: "Meu acesso não funciona, urgente" | Passou |
| T2 — Baixa urgência | Mensagem: "Quero saber o valor da minha fatura" | Passou |
| T3 — Entrada inválida | Mensagem: "oi" | Passou |
| T4 — Categoria financeira | Mensagem: "Não recebi meu reembolso" | Passou |
| T5 — Campo ausente | JSON sem campo `mensagem` | Passou |

---

## 4. Evidências de funcionamento

Prints disponíveis em `docs/evidence/`:

- `01-workflow-n8n.png` — workflow completo no n8n
- `02-teste-alta-urgencia.png` — execução T1 com email enviado
- `03-teste-baixa-urgencia.png` — execução T2 apenas com registro no Sheets
- `04-teste-fallback.png` — execução T3 com fallback ativado
- `05-google-sheets.png` — planilha com registros dos chamados

---

## 5. Limitações conhecidas

- O sistema não tem memória de contexto: cada chamado é processado de forma independente
- A qualidade da classificação depende do prompt — mensagens muito ambíguas podem ser mal classificadas
- Não há interface de revisão: chamados de baixa confiança precisam ser verificados manualmente no Sheets
- A credencial OAuth do Gmail pode expirar e exigir reautenticação manual

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Erro de classificação de urgência | Média | Alto | Fallback para revisão manual quando confiança for baixa |
| Indisponibilidade da API da OpenAI | Baixa | Alto | Nó onError captura e registra no Sheets |
| Expiração do OAuth Gmail | Baixa | Médio | Monitoramento periódico das credenciais |

---

## 7. Decisões arquiteturais

- ADR-001: Escolha da solution-a como base, com incorporação do tratamento de erro da solution-c. Ver `docs/adr/001-escolha-da-solucao.md`.

---

## 8. Instruções de execução

```bash
# 1. Importar o workflow no n8n
# Acesse seu n8n → Workflows → Import from file → selecione src/workflow.json

# 2. Configurar credenciais no n8n
# - OpenAI: Settings → Credentials → New → Header Auth → nome: Authorization, valor: Bearer SUA_API_KEY
# - Gmail: Settings → Credentials → New → Gmail OAuth2 → autenticar com Google
# - Google Sheets: Settings → Credentials → New → Google Sheets OAuth2 → autenticar

# 3. Criar planilha no Google Sheets com as colunas:
# Timestamp | Nome | Email | Mensagem | Categoria | Urgência | Resumo | Confiança | Caminho

# 4. Atualizar o ID da planilha nos três nós do Google Sheets no workflow

# 5. Ativar o workflow (toggle "Active" no canto superior direito)

# 6. Testar com curl:
curl -X POST https://seu-n8n.app.n8n.cloud/webhook/triagem \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Meu acesso não funciona", "nome": "Teste", "email": "teste@email.com"}'
```

---

## 9. Checklist de revisão

- [ ] Mission brief atendido
- [ ] Três soluções implementadas/prototipadas
- [ ] Testes executados e documentados
- [ ] Evidências registradas em `docs/evidence/`
- [ ] ADR registrado em `docs/adr/`
- [ ] Commits com mensagens claras e racionalidade
- [ ] Código funcional em `src/`
- [ ] Agent.md preenchido
- [ ] Mentorship Pack preenchido
- [ ] Workflow Runbook seguido

---

## 10. Justificativa para merge

O projeto cumpre todos os requisitos obrigatórios do enunciado: workflow no n8n com múltiplos nós nomeados, agente de IA influenciando o roteamento do fluxo (não apenas gerando texto), lógica de decisão com Switch e caminhos condicionais, integração com Google Sheets e Gmail, persistência e rastreabilidade via Sheets, tratamento de erros e fallback implementados. A documentação está completa e coerente com o que foi implementado, com três soluções comparadas e decisão arquitetural justificada em ADR.
