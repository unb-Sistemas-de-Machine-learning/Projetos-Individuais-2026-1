# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Guilherme Westphall
> **Matrícula:** 211061805
> **Data de entrega:** 05/05/2026

---

## 1. Resumo do Projeto

O projeto automatiza a emissão recorrente de notas fiscais para um prestador de serviços que fatura por hora duas vezes por mês. O fluxo, implementado no n8n, busca automaticamente as horas registradas no Productive.io, calcula o valor da nota de forma determinística e aciona dois agentes de IA: o Rascunhador, que gera o rascunho do e-mail e a mensagem de aprovação interna; e o Revisor, que valida o conteúdo quanto a tom, profissionalismo e ausência de dados internos sigilosos. Após a revisão pelos agentes, o prestador recebe a mensagem no Telegram e decide se aprova, rejeita ou solicita alterações com o comando `edit`. Somente após a aprovação explícita o e-mail é enviado pelo Gmail e o rascunho é registrado no Google Drive. O resultado é um processo auditável, seguro e com aprovação humana obrigatória — adequado para fluxo financeiro recorrente em que o custo de um erro de envio é alto.

---

## 2. Problema Escolhido

O processo manual de emissão de notas fiscais recorrentes envolve múltiplas etapas repetitivas: consultar horas trabalhadas no Productive.io, somar o total do período, calcular o valor com base na taxa horária, preparar um e-mail profissional e enviá-lo ao contratante. Esse processo ocorre duas vezes por mês — nos dias 1 e 16 — e é sujeito a esquecimentos, erros de cálculo e variações na qualidade da comunicação.

A automação resolve o problema ao eliminar as etapas manuais de consulta, cálculo e redação, mantendo o controle humano sobre o momento e o conteúdo do envio. O uso de IA vai além da geração de texto: os agentes influenciam diretamente o caminho seguido pelo fluxo, podendo interromper a execução, solicitar revisão manual ou encaminhar para aprovação.

---

## 3. Desenho do Fluxo

```text
Schedule/Telegram Trigger
→ Calcular período de faturamento (Code)
→ Buscar entradas no Productive.io (HTTP Request)
→ Consolidar horas e calcular valor (Code)
→ Agente Rascunhador (Ollama LLM): gera rascunho do e-mail e mensagem de aprovação
→ Agente Revisor (Ollama LLM): valida tom, conteúdo e ausência de dados internos
→ Normalizar JSON da IA (Code)
→ Switch: recommended_action
   → request_approval → Telegram: enviar rascunho revisado para aprovação humana
   → needs_manual_review → Telegram: solicitar revisão manual
   → stop → encerrar e registrar motivo
→ Aguardar resposta no Telegram (Webhook)
→ Switch: comando do usuário
   → approve → Gmail: enviar e-mail + Google Drive: registrar rascunho
   → reject → registrar rejeição e encerrar
   → edit → Agente Revisor: revisar e reapresentar via Telegram
```

### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Schedule Trigger | Trigger | Aciona o fluxo automaticamente nos dias 1 e 16 de cada mês |
| Telegram Trigger | Trigger | Permite acionamento manual via mensagem no Telegram |
| Set Billing Period | Code | Calcula `period_start` e `period_end` com base na data de execução |
| HTTP Request (Productive.io) | HTTP Request | Busca entradas de tempo via API REST, filtradas por `person_id` e intervalo de datas |
| Parse Entries | Code | Consolida entradas: conta registros, soma minutos e horas, aplica taxa horária e calcula valor total |
| Agente Rascunhador | LLM (Ollama) | Gera rascunho do e-mail, mensagem de aprovação e validação inicial com `recommended_action` |
| Agente Revisor | LLM (Ollama) | Revisa conteúdo, detecta problemas de tom, dados internos ou conteúdo inadequado |
| Normalize AI JSON | Code | Extrai e valida o JSON da resposta do modelo; aciona fallback se malformado |
| Switch (recommended_action) | Switch | Roteia o fluxo com base na recomendação dos agentes |
| Telegram (aprovação) | Telegram | Envia rascunho revisado ao prestador para aprovação humana |
| Webhook (resposta Telegram) | Webhook | Recebe o comando `approve`, `reject` ou `edit` enviado pelo usuário |
| Gmail | Gmail | Envia o e-mail ao contratante após aprovação |
| Google Drive | Google Drive | Registra o rascunho aprovado e o log de execução |

---

## 4. Papel do Agente de IA

- **Modelo/serviço utilizado:** Ollama (execução local), modelo llama3 ou equivalente.
- **Tipo de decisão tomada pela IA:** Validação e roteamento — os agentes retornam `recommended_action`, que determina o caminho seguido pelo fluxo.
- **Como a decisão da IA afeta o fluxo:** O Switch central usa o `recommended_action` retornado pelos agentes para decidir entre aprovação humana, revisão manual ou interrupção da execução.

### Agente Rascunhador

Recebe o JSON consolidado com período, quantidade de entradas, total de horas, taxa horária, valor total e avisos. Retorna:

```json
{
  "confidence": "high | medium | low",
  "recommended_action": "request_approval | needs_manual_review | stop",
  "summary": "Resumo interno da validação.",
  "detected_issues": [],
  "telegram_message": "Mensagem para o prestador no Telegram.",
  "email_subject": "Invoice #018",
  "email_body": "Corpo do e-mail ao contratante."
}
```

### Agente Revisor

Recebe o rascunho do Agente Rascunhador. Retorna:

```json
{
  "review_status": "approved | needs_revision",
  "review_notes": "Observações sobre alterações realizadas ou necessárias.",
  "revised_email_body": "Corpo do e-mail revisado, quando aplicável."
}
```

---

## 5. Lógica de Decisão

- **Condição 1: `recommended_action` (retornado pelos agentes)**
  - `request_approval` → envia rascunho revisado ao Telegram para aprovação humana.
  - `needs_manual_review` → envia mensagem de alerta ao Telegram; a execução aguarda intervenção.
  - `stop` → o fluxo encerra e registra o motivo.

- **Condição 2: comando recebido no Telegram**
  - `approve` → Gmail envia o e-mail; Google Drive registra o rascunho aprovado.
  - `reject` → a execução é encerrada; a rejeição é registrada.
  - `edit` → o Agente Revisor recebe o rascunho com solicitação de melhoria; o resultado revisado é reapresentado no Telegram.

- **Condição 3: `review_status` do Agente Revisor**
  - `approved` → o fluxo prossegue para aprovação humana via Telegram.
  - `needs_revision` → o fluxo retorna para revisão ou encaminha para revisão manual.

---

## 6. Integrações

| Serviço | Finalidade |
|---------|-----------|
| Productive.io | Fonte das entradas de tempo trabalhadas, consultadas via API REST com filtro por `person_id` e intervalo de datas |
| Ollama (local) | Modelo de linguagem para os dois agentes de IA (Rascunhador e Revisor) |
| Telegram | Envio da mensagem de aprovação ao prestador e recepção do comando de decisão |
| Gmail | Envio do e-mail com a nota fiscal ao contratante após aprovação |
| Google Drive | Registro dos rascunhos aprovados e log de auditoria de cada execução |
| Google Sheets | Edição do template de invoice |

---

## 7. Persistência e Rastreabilidade

A rastreabilidade é garantida por três mecanismos complementares:

1. **Google Drive**: cada execução bem-sucedida registra o rascunho aprovado com metadados de data, período, horas e valor. A pasta `Invoices/Draft` armazena o histórico de todas as execuções, conforme evidenciado em `docs/evidences/evidence7.jpeg`.

2. **Telegram**: o histórico de mensagens registra o rascunho apresentado, o comando do usuário (`approve`, `reject` ou `edit`) e a confirmação de envio, formando um log natural e imutável da aprovação humana.

3. **n8n Execution Log**: o histórico de execuções do n8n registra os inputs e outputs de cada nó, permitindo auditoria técnica completa de cada etapa do fluxo.

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** O nó de normalização de JSON tenta extrair o JSON da resposta do modelo mesmo quando há texto extra ao redor. Se a extração falhar, o campo `recommended_action` é forçado para `needs_manual_review` e o fluxo solicita intervenção humana.

- **Entradas inválidas:** Se o Productive.io retornar zero entradas ou o total de horas for zero, o nó de consolidação adiciona um aviso em `warnings`. O Agente Rascunhador recebe esse aviso e deve recomendar `needs_manual_review` ou `stop`.

- **Fallback de baixa confiança:** Se o agente retornar `confidence: low`, o fluxo trata a situação como `needs_manual_review`, independentemente do `recommended_action` informado.

- **Credenciais e segredos:** Todos os tokens (Productive.io, Telegram, Gmail, Google Drive) são armazenados nas credenciais do n8n e não estão presentes no JSON exportado do workflow.

---

## 9. Diferenciais implementados

- [ ] Memória de contexto
- [ ] Multi-step reasoning
- [ ] Integração com base de conhecimento
- [x] **Fluxo multi-etapas com dois agentes de IA** (Rascunhador e Revisor)

O fluxo com dois agentes representa um diferencial de separação de responsabilidades dentro do processo de IA. O Agente Revisor atua como camada de validação de conteúdo antes da aprovação humana, detectando problemas que um único agente poderia deixar passar.

---

## 10. Limitações e Riscos

**Limitações:**

- O modelo de linguagem é executado localmente via Ollama, exigindo que o serviço esteja em execução nos horários do agendamento.
- A qualidade da revisão depende do modelo disponível. Modelos menores podem não detectar todos os problemas de conteúdo.
- O loop de edição via Telegram não tem limite de iterações definido no workflow atual. Em uso real, recomenda-se limitar a 2–3 revisões antes de escalar para revisão manual.
- O fluxo depende de um webhook ativo (ngrok ou equivalente) para receber comandos do Telegram.

**Riscos:**

| Risco | Mitigação |
|-------|-----------|
| IA retornar JSON malformado | Nó de normalização + fallback para `needs_manual_review` |
| Envio de e-mail sem aprovação humana | Bloqueio condicional obrigatório via confirmação no Telegram |
| Ollama indisponível | Tratamento de erro HTTP + alerta de revisão manual |
| E-mail com dados internos expostos | Agente Revisor valida ausência de dados sigilosos antes do Telegram |
| Credencial exposta no JSON | Credenciais armazenadas no n8n, não incluídas no JSON exportado |

---

## 11. Como executar

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
7. Executar manualmente (botão "Execute Workflow") ou aguardar o agendamento automático.
8. Verificar a mensagem no Telegram e responder com approve, reject ou edit.
```

---

## 12. Referências

1. [n8n Documentation](https://docs.n8n.io)
2. [Productive.io API Reference](https://developer.productive.io)
3. [Ollama — Local LLM Runtime](https://ollama.com)

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (`.json`) — `automation-invoice-two-agent-review-ngrok.json`
- [x] Workflow baseline exportado do n8n (`.json`) — `automation-invoice-complete-ngrok.json`
- [x] Demonstração do fluxo (prints em `docs/evidences/`)
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto
