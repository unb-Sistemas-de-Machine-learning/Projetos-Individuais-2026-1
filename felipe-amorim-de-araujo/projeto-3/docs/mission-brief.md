# Mission Brief — IssueTriageBot

> **Aluno:** Felipe Amorim de Araújo
> **Domínio:** Triagem Inteligente de Issues de Software
> **Matrícula:** 221022275

---

## 1. Objetivo do agente

O **IssueTriageBot** é um agente de automação que monitora a criação de issues em um repositório GitHub e, usando a Gemini API, classifica automaticamente cada issue por tipo, severidade e componente afetado. Com base nessa classificação, o fluxo no n8n roteia a issue para o canal Slack correto e persiste o registro completo no Google Sheets para rastreabilidade.

---

## 2. Problema que ele resolve

Equipes de desenvolvimento perdem tempo triando manualmente issues abertas no GitHub: decidir se é um bug, feature ou dúvida, qual a urgência e qual time deve ser notificado. Esse processo é repetitivo, propenso a inconsistências e gera atraso na resposta a incidentes críticos.

O IssueTriageBot automatiza essa triagem, garantindo que issues críticas cheguem imediatamente ao canal de incidentes enquanto dúvidas e backlog são direcionados aos canais adequados — sem intervenção humana para os casos rotineiros.

---

## 3. Usuários-alvo

- Desenvolvedores que abrem issues no repositório (usuários indiretos — se beneficiam da resposta rápida)
- Tech leads e responsáveis pelo backlog (recebem notificações classificadas no Slack)
- Qualquer pessoa que precise auditar o histórico de triagem (acessa o Google Sheets)

---

## 4. Contexto de uso

O agente opera em background, ativado automaticamente via webhook do GitHub sempre que uma nova issue é criada. Não requer interação humana no fluxo padrão. O ambiente de execução é o n8n self-hosted, integrado à Gemini API, Slack e Google Sheets via credenciais configuradas.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Evento de criação de issue no GitHub (webhook `issues.opened`) |
| **Formato da entrada** | JSON do payload do GitHub contendo `title`, `body`, `url`, `labels` |
| **Saída** | Notificação no canal Slack correspondente + linha registrada no Google Sheets |
| **Formato da saída** | Mensagem Slack formatada com tipo/severidade/componente + linha no Google Sheets via API com todos os campos |

---

## 6. Limites do agente

### O que o agente faz:

- Recebe eventos de criação de issue via webhook do GitHub
- Classifica a issue em tipo (`bug`, `feature`, `question`), severidade (`critical`, `medium`, `low`) e componente (`frontend`, `backend`, `infra`, `unknown`)
- Extrai um resumo de uma linha da issue
- Roteia a notificação para o canal Slack correto com base na classificação
- Persiste o registro completo no Google Sheets
- Retenta a chamada à Gemini API uma vez em caso de falha antes de aplicar fallback

### O que o agente NÃO deve fazer:

- Modificar, fechar ou comentar na issue do GitHub automaticamente
- Tomar decisões além da triagem inicial (ex: atribuir responsáveis, estimar sprints)
- Processar eventos que não sejam `issues.opened` (ex: edições, fechamentos)
- Substituir a revisão humana em casos ambíguos (usa fallback com flag de revisão)

---

## 7. Critérios de aceitação

- [ ] Issue crítica criada no GitHub gera notificação no canal `#incidents` em menos de 30 segundos
- [ ] Issues não-críticas (bug/feature) são enviadas para `#backlog` com tipo, severidade e componente corretos
- [ ] Issues do tipo `question` são roteadas para `#questions`
- [ ] Toda issue processada gera uma linha no Google Sheets com todos os campos preenchidos
- [ ] Falha na Gemini API dispara retry automático; segunda falha aplica defaults e sinaliza `ai_flagged=true` no Sheets

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Classificação incorreta pela IA (ex: bug tratado como feature) | Média | Médio | Prompt estruturado com exemplos; campo `confidence` exposto no Sheets para auditoria |
| Gemini API indisponível ou rate limit excedido (free tier) | Média | Médio | Retry automático uma vez; fallback com defaults e flag de revisão manual |
| Payload do GitHub em formato inesperado | Baixa | Baixo | Validação dos campos obrigatórios (`title`, `body`) antes de chamar a IA |
| Credenciais do Slack ou Sheets expiradas | Baixa | Alto | Tratamento de erro com log no n8n e alerta no próprio Slack se possível |

---

## 9. Evidências necessárias

- [ ] Workflow `.json` exportado do n8n com todos os nós configurados
- [ ] Screenshot ou vídeo do fluxo rodando com ao menos 3 issues de tipos diferentes
- [ ] Google Sheets com registros reais das issues processadas (incluindo ao menos um caso com `ai_flagged=true`)
- [ ] Mensagens Slack nos 3 canais (`#incidents`, `#backlog`, `#questions`) como evidência do roteamento
