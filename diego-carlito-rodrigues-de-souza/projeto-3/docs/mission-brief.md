# Mission Brief

> **Aluno(a):** Diego Carlito Rodrigues de Souza
> **Matrícula:** 221007690
> **Domínio:** Agente para suporte educacional

---

## 1. Objetivo do agente
Analisar dúvidas enviadas por alunos, classificar a intenção da mensagem (dúvida técnica, questão administrativa ou solicitação de exceção) e decidir autonomamente o fluxo de resolução utilizando o n8n para responder, registrar ou escalar.

---

## 2. Problema que ele resolve
Professores e monitores perdem horas preciosas triando mensagens repetitivas de alunos (ex: datas de entrega, formato de arquivos) misturadas com dúvidas técnicas reais de código ou teoria. O agente elimina esse gargalo fazendo o roteamento inteligente, garantindo que o professor só atue onde a intervenção humana é estritamente necessária.

---

## 3. Usuários-alvo
- **Alunos:** Que buscam respostas rápidas para dúvidas da disciplina a qualquer hora do dia.
- **Professores e Monitores:** Que precisam de uma caixa de entrada limpa, recebendo apenas questões complexas ou administrativas críticas.

---

## 4. Contexto de uso
O agente atua de forma assíncrona e 24/7. Ele é acionado via Webhook/Chatbot (ex: Telegram/Discord) sempre que um aluno envia uma nova pergunta.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Mensagem de texto natural enviada pelo aluno. |
| **Formato da entrada** | JSON: `{"aluno": "string", "mensagem": "string", "id_turma": "string"}` |
| **Saída** | Decisão de roteamento da IA, categoria da dúvida e (se aplicável) a resposta técnica gerada. |
| **Formato da saída** | JSON estruturado (ex: `{"categoria": "tecnica", "route_to": "llm_reply", "justificativa": "Dúvida sobre linguagem de programação"}`) |

---

## 6. Limites do agente

### O que o agente faz:
- Lê a pergunta e classifica a intenção em três vias: `tecnica`, `administrativa`, `excecao`.
- Gera respostas conceituais para dúvidas técnicas.

### O que o agente NÃO deve fazer:
- Dar a resposta pronta ou o código final de trabalhos avaliativos (deve guiar o aluno, não resolver por ele).
- Alterar notas, prazos ou conceder exceções (faltas médicas, atrasos). Isso é estritamente papel do professor.
- Prometer que o professor vai responder em um tempo específico.

---

## 7. Critérios de aceitação
- [ ] O fluxo no n8n recebe a entrada corretamente.
- [ ] O Agente LLM classifica a mensagem extraindo um JSON válido.
- [ ] O n8n utiliza o campo `route_to` num nó "Switch" para ramificar o fluxo de automação.
- [ ] Dúvidas administrativas e solicitações de exceção são salvas em uma planilha (Google Sheets) ou alertadas (Slack/Email) sem resposta automática do LLM.

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Alucinação em Respostas Técnicas | Média | Alto | Inserir no prompt que o agente deve declarar incerteza se não souber, roteando para o professor. |
| Resolução de Trabalhos (Trapaça) | Alta | Médio | Regra estrita no prompt (System Message) para atuar com método socrático (fazer perguntas) em vez de dar código pronto. |

---

## 9. Evidências necessárias
- [ ] Print do workflow funcional no n8n.
- [ ] JSON exportado do workflow (`workflow.json`).
- [ ] Logs de testes mostrando pelo menos um fluxo de cada ramificação (uma dúvida técnica respondida e uma solicitação de exceção escalada).
