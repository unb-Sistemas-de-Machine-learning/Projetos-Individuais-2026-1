# Projeto 4 — Triagem Inteligente de Chamados de Suporte

**Aluno:** Gabryel Nicolas Soares de Sousa  
**Matrícula:** 221022570  
**Disciplina:** Engenharia de Software Agêntica

---

## Visão Geral

Sistema de triagem automática de chamados de suporte construído com **n8n** como orquestrador e **OpenAI GPT-3.5-turbo** como agente de classificação. A IA classifica cada chamado recebido e o n8n roteia automaticamente para o caminho correto: notificação por email (urgente) ou registro no Google Sheets (demais casos).

## Fluxo resumido

```
Webhook → Validar entrada → IA classifica → Switch de urgência
                                                ├── Alta urgência → Email + Sheets
                                                ├── Baixa/média → Sheets
                                                └── Baixa confiança → Fallback + Sheets
```

## Estrutura do Repositório

```
projeto-4/
├── agent.md                        # Especificação do agente de IA
├── docs/
│   ├── mission-brief.md            # Contrato do agente
│   ├── mentorship-pack.md          # Guia de estilo e julgamento
│   ├── workflow-runbook.md         # Processo de execução
│   ├── merge-readiness-pack.md     # Evidências de prontidão
│   ├── relatorio-entrega.md        # Relatório técnico
│   ├── adr/
│   │   └── 001-escolha-da-solucao.md
│   └── evidence/
│       └── (prints das execuções)
├── solutions/
│   ├── solution-a/README.md        # Prompt simples (escolhida)
│   ├── solution-b/README.md        # Com base de conhecimento
│   └── solution-c/README.md        # Fluxo multi-etapas
├── src/
│   └── workflow.json               # Workflow exportado do n8n
├── tests/
│   └── test-cases.md               # Casos de teste documentados
└── README.md
```

## Como executar

1. Importe `src/workflow.json` no seu n8n
2. Configure as credenciais: OpenAI API Key, Gmail OAuth2, Google Sheets OAuth2
3. Atualize o ID da planilha no nó "Registrar no Sheets"
4. Ative o workflow
5. Envie um POST para o webhook:

```bash
curl -X POST https://seu-n8n.app.n8n.cloud/webhook/triagem \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Meu acesso não funciona", "nome": "Teste", "email": "teste@email.com"}'
```

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Orquestrador | n8n |
| Agente de IA | OpenAI GPT-3.5-turbo |
| Persistência | Google Sheets |
| Notificação | Gmail |
| Entrada | Webhook HTTP |

## Sequência de Commits

| # | Commit |
|---|---|
| 1 | `feat: cria mission brief inicial` |
| 2 | `feat: adiciona agent.md com regras de comportamento` |
| 3 | `feat: cria mentorship pack e workflow runbook` |
| 4 | `feat: implementa solution-a (prompt simples)` |
| 5 | `feat: implementa solution-b (com base de conhecimento)` |
| 6 | `feat: implementa solution-c (fluxo multi-etapas)` |
| 7 | `test: adiciona testes e evidências das três soluções` |
| 8 | `docs: registra ADR com comparação das soluções` |
| 9 | `docs: adiciona merge-readiness pack` |
| 10 | `feat: consolida solução final e atualiza README` |
