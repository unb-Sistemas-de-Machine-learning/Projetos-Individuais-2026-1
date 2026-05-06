# Cenários de Teste — Automação de Emissão de Notas Fiscais

> **Projeto:** Automação Inteligente de Emissão de Notas Fiscais
> **Aluno(a):** Guilherme Westphall
> **Workflow testado:** `automation-invoice-two-agent-review-ngrok.json`

---

## Sobre os testes

Os testes descritos neste documento são cenários funcionais que verificam o comportamento do workflow n8n em situações esperadas e de borda. Cada cenário descreve a condição de entrada, os passos executados e o resultado esperado.

Para reproduzir um cenário manualmente no n8n, substitua os dados do nó **Parse Entries** pelos valores indicados em cada caso, usando um nó **Set** ou **Edit Fields** imediatamente antes do Agente Rascunhador. Isso permite simular qualquer situação sem depender de uma chamada real ao Productive.io.

---

## Cenários de teste

### TC-01 — Cálculo de período no dia 1 do mês

**Objetivo:** Verificar que o nó de cálculo de período identifica corretamente o intervalo do ciclo anterior quando executado no início do mês.

**Condição de entrada:**
- Data de execução: qualquer dia entre 1 e 15 do mês atual.
- Nenhum `period_start` ou `period_end` fornecido manualmente.

**Passos:**
1. Executar o workflow manualmente em um dia entre 1 e 15.
2. Observar os valores calculados pelo nó **Set Billing Period**.

**Resultado esperado:**
- `period_start` = dia 16 do mês anterior.
- `period_end` = último dia do mês anterior.

**Exemplo:** execução em 05/05/2026 → `period_start = 2026-04-16`, `period_end = 2026-04-30`.

---

### TC-02 — Cálculo de período no dia 16 do mês

**Objetivo:** Verificar que o nó de cálculo de período identifica corretamente o intervalo da primeira quinzena do mês atual quando executado a partir do dia 16.

**Condição de entrada:**
- Data de execução: qualquer dia entre 16 e o último dia do mês atual.
- Nenhum `period_start` ou `period_end` fornecido manualmente.

**Passos:**
1. Executar o workflow manualmente em um dia entre 16 e o fim do mês.
2. Observar os valores calculados pelo nó **Set Billing Period**.

**Resultado esperado:**
- `period_start` = dia 1 do mês atual.
- `period_end` = dia 15 do mês atual.

**Exemplo:** execução em 20/05/2026 → `period_start = 2026-05-01`, `period_end = 2026-05-15`.

---

### TC-03 — Período informado manualmente

**Objetivo:** Verificar que o workflow respeita `period_start` e `period_end` quando fornecidos explicitamente, ignorando o cálculo automático.

**Condição de entrada:**
- `period_start = 2026-03-01`
- `period_end = 2026-03-15`

**Passos:**
1. Informar os valores no nó de entrada ou via Telegram Trigger.
2. Observar que o HTTP Request ao Productive.io usa os filtros de data exatos fornecidos.

**Resultado esperado:**
- A consulta ao Productive.io usa `filter[date][gt_eq] = 2026-03-01` e `filter[date][lt_eq] = 2026-03-15`.
- O período calculado automaticamente é ignorado.

---

### TC-04 — Caminho feliz com dados válidos

**Objetivo:** Verificar o fluxo completo com dados normais e aprovação direta.

**Condição de entrada:**

```json
{
  "period_start": "2026-04-16",
  "period_end": "2026-04-30",
  "entry_count": 24,
  "total_minutes": 3900,
  "total_hours": 65.0,
  "hourly_rate": 100,
  "currency": "BRL",
  "amount": 6500.00,
  "warnings": [],
  "entries": []
}
```

**Passos:**
1. Injetar os dados acima no nó anterior ao Agente Rascunhador.
2. Observar a resposta dos dois agentes.
3. Verificar a mensagem enviada ao Telegram.
4. Responder com `approve` no Telegram.

**Resultado esperado:**
- Agente Rascunhador retorna `recommended_action: request_approval` com `confidence: high`.
- Agente Revisor retorna `review_status: approved`.
- Mensagem de aprovação é enviada ao Telegram com período, horas, valor e instruções.
- Após `approve`, e-mail é enviado pelo Gmail e rascunho é registrado no Google Drive.

---

### TC-05 — Zero entradas no período

**Objetivo:** Verificar que o workflow não prossegue para aprovação quando não há entradas de tempo registradas.

**Condição de entrada:**

```json
{
  "period_start": "2026-04-16",
  "period_end": "2026-04-30",
  "entry_count": 0,
  "total_minutes": 0,
  "total_hours": 0.0,
  "hourly_rate": 100,
  "currency": "BRL",
  "amount": 0.00,
  "warnings": ["Nenhuma entrada de tempo encontrada para o período."],
  "entries": []
}
```

**Passos:**
1. Injetar os dados acima.
2. Observar a resposta do Agente Rascunhador.
3. Verificar o caminho seguido pelo Switch.

**Resultado esperado:**
- Agente Rascunhador retorna `recommended_action: needs_manual_review` ou `stop`.
- O fluxo não envia mensagem de aprovação padrão.
- O Telegram recebe uma notificação de revisão manual ou o fluxo é encerrado com registro do motivo.
- Nenhum e-mail é enviado pelo Gmail.

---

### TC-06 — Total de horas igual a zero com entradas presentes

**Objetivo:** Verificar que o workflow detecta a inconsistência entre entradas existentes e total de horas zerado.

**Condição de entrada:**

```json
{
  "period_start": "2026-04-16",
  "period_end": "2026-04-30",
  "entry_count": 5,
  "total_minutes": 0,
  "total_hours": 0.0,
  "hourly_rate": 100,
  "currency": "BRL",
  "amount": 0.00,
  "warnings": ["Total de horas é zero apesar de existirem entradas."],
  "entries": []
}
```

**Passos:**
1. Injetar os dados acima.
2. Observar a resposta dos agentes e o caminho seguido.

**Resultado esperado:**
- O aviso em `warnings` é reconhecido pelo Agente Rascunhador.
- `recommended_action` retornado é `needs_manual_review` ou `stop`.
- Nenhum e-mail é enviado sem aprovação.

---

### TC-07 — Resposta malformada do agente de IA

**Objetivo:** Verificar que o nó de normalização de JSON lida corretamente com respostas do modelo fora do formato esperado.

**Condição simulada:**
- Substituir a saída do Agente Rascunhador por um texto sem JSON válido, como:
  ```
  Aqui está minha análise: os dados parecem corretos e recomendo aprovação.
  ```

**Passos:**
1. Simular a resposta malformada diretamente no nó de normalização ou via nó **Set** antes dele.
2. Observar o comportamento do nó de normalização.

**Resultado esperado:**
- O nó de normalização não consegue extrair um JSON válido.
- O campo `recommended_action` é forçado para `needs_manual_review`.
- O fluxo encaminha para o caminho de revisão manual.
- Nenhum e-mail é enviado.

---

### TC-08 — Comando `edit` no Telegram

**Objetivo:** Verificar que o comando `edit` aciona o Agente Revisor para uma nova rodada de revisão e reapresenta o rascunho no Telegram.

**Condição de entrada:**
- Fluxo em execução normal com rascunho apresentado no Telegram (TC-04).
- Usuário responde com `edit` no Telegram.

**Passos:**
1. Aguardar a mensagem de aprovação no Telegram.
2. Responder com `edit`.
3. Observar se o Agente Revisor é acionado novamente.
4. Verificar se uma nova mensagem com o rascunho revisado é enviada ao Telegram.

**Resultado esperado:**
- O Webhook recebe o comando `edit`.
- O Agente Revisor recebe o rascunho original com instrução de revisão.
- Uma nova mensagem com o rascunho revisado é enviada ao Telegram.
- O e-mail ainda não é enviado.

**Evidência coletada:** `docs/evidences/evidence2.png` — rascunho revisado com tom formal aplicado após comando `edit`.

---

### TC-09 — Comando `approve` no Telegram

**Objetivo:** Verificar que o comando `approve` aciona o envio do e-mail pelo Gmail e o registro no Google Drive.

**Condição de entrada:**
- Rascunho apresentado no Telegram (TC-04 ou após TC-08).
- Usuário responde com `approve`.

**Passos:**
1. Aguardar a mensagem de aprovação no Telegram.
2. Responder com `approve`.
3. Verificar o envio no Gmail.
4. Verificar o registro no Google Drive.

**Resultado esperado:**
- O Webhook recebe o comando `approve`.
- O Gmail envia o e-mail ao contratante.
- O Google Drive registra o rascunho aprovado na pasta `Invoices/Draft`.
- O Telegram recebe a confirmação de envio bem-sucedido.

**Evidências coletadas:**
- `docs/evidences/evidence3.png` — Telegram confirmando envio pelo Gmail.
- `docs/evidences/evidence5.png` — e-mail recebido no Gmail.
- `docs/evidences/evidence7.jpeg` — rascunho registrado no Google Drive.

---

### TC-10 — Comando `reject` no Telegram

**Objetivo:** Verificar que o comando `reject` encerra o fluxo sem enviar e-mail.

**Condição de entrada:**
- Rascunho apresentado no Telegram.
- Usuário responde com `reject`.

**Passos:**
1. Aguardar a mensagem de aprovação no Telegram.
2. Responder com `reject`.
3. Verificar que o Gmail não foi acionado.

**Resultado esperado:**
- O Webhook recebe o comando `reject`.
- O fluxo encerra sem enviar e-mail.
- A rejeição é registrada (log de execução no n8n ou Google Drive).
- Nenhuma mensagem de confirmação de envio é recebida no Telegram.

---

## Resumo dos cenários

| Código | Cenário | Resultado esperado |
|--------|---------|-------------------|
| TC-01 | Período calculado — dias 1 a 15 | `period_start` = dia 16 do mês anterior |
| TC-02 | Período calculado — dias 16 a 31 | `period_start` = dia 1 do mês atual |
| TC-03 | Período informado manualmente | Consulta usa os valores fornecidos |
| TC-04 | Caminho feliz com dados válidos | `request_approval`, mensagem no Telegram, envio após `approve` |
| TC-05 | Zero entradas no período | `needs_manual_review` ou `stop`, sem envio |
| TC-06 | Zero horas com entradas presentes | `needs_manual_review` ou `stop`, sem envio |
| TC-07 | JSON malformado da IA | Fallback para `needs_manual_review`, sem envio |
| TC-08 | Comando `edit` no Telegram | Rascunho revisado reapresentado, sem envio |
| TC-09 | Comando `approve` no Telegram | E-mail enviado, rascunho registrado no Drive |
| TC-10 | Comando `reject` no Telegram | Fluxo encerrado, sem envio |
