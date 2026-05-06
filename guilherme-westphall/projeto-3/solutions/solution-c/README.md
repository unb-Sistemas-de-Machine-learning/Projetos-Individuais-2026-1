# Solution C: Fluxo com Dois Agentes — Rascunhador e Revisor

## 1. Resumo

Esta solução introduz dois agentes de IA independentes no fluxo de aprovação da nota fiscal. O primeiro agente, o **Rascunhador**, recebe os dados consolidados da nota e gera o rascunho do e-mail ao contratante e a mensagem interna de aprovação para o Telegram. O segundo agente, o **Revisor**, recebe o rascunho e valida seu conteúdo quanto a tom, profissionalismo, ausência de dados internos confidenciais e ausência de conteúdo inadequado ou ofensivo. A aprovação humana via Telegram permanece obrigatória antes do envio final.

## 2. Fluxo proposto

```text
Schedule/Telegram Trigger
→ Calcular período de faturamento (Code)
→ Buscar entradas no Productive.io (HTTP Request)
→ Consolidar horas e calcular valor (Code)
→ Agente Rascunhador (Ollama LLM): gera rascunho do e-mail e mensagem de aprovação
→ Agente Revisor (Ollama LLM): valida tom, conteúdo e conformidade
→ Normalizar JSON da IA (Code)
→ Switch: recommended_action
   → request_approval: enviar rascunho revisado ao Telegram
   → needs_manual_review: solicitar revisão manual via Telegram
   → stop: registrar interrupção e encerrar
→ Telegram: aprovação humana (approve / reject / edit)
   → edit: Agente Revisor revisa e reapresenta no Telegram
   → approve: enviar e-mail via Gmail + registrar no Google Drive
   → reject: registrar rejeição e encerrar
```

## 3. Papel de cada agente

### Agente Rascunhador

Recebe o JSON consolidado com os dados da nota fiscal e é responsável por:

- Gerar o rascunho do e-mail externo ao contratante (breve, profissional, sem dados internos).
- Gerar a mensagem de aprovação interna para o Telegram (com detalhes do período, horas, valor e confiança).
- Indicar o nível de confiança e eventuais problemas detectados nos dados.
- Recomendar a ação: `request_approval`, `needs_manual_review` ou `stop`.

Formato de saída esperado:

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

Recebe o rascunho produzido pelo Agente Rascunhador e é responsável por:

- Verificar se o e-mail tem tom profissional e adequado para comunicação externa.
- Confirmar que o e-mail não contém dados internos (horas trabalhadas, valor, período, aprovação, automação, IA).
- Verificar ausência de conteúdo ofensivo ou inadequado.
- Avaliar se o e-mail é coerente com o estilo esperado para comunicação ao contratante.
- Aprovar o rascunho ou solicitar revisões específicas com notas explicativas.

Formato de saída esperado:

```json
{
  "review_status": "approved | needs_revision",
  "review_notes": "Observações sobre alterações realizadas ou necessárias.",
  "revised_email_body": "Corpo do e-mail revisado, quando aplicável."
}
```

## 4. Decisão automatizada

A decisão de prosseguir para aprovação humana depende do resultado combinado dos dois agentes:

- Se o Agente Revisor aprovar (`review_status: approved`) e o Rascunhador recomendar `request_approval`: o fluxo envia o rascunho revisado ao Telegram para aprovação humana.
- Se o Agente Revisor solicitar revisão (`needs_revision`): o fluxo pode iterar ou encaminhar para revisão manual dependendo do contexto.
- Se o Rascunhador recomendar `needs_manual_review` ou `stop`: o fluxo segue esses caminhos independentemente do resultado da revisão.

O usuário também pode solicitar revisão diretamente pelo Telegram com o comando `edit`. O fluxo encaminha o rascunho ao Agente Revisor com a solicitação explícita de melhoria e reapresenta o resultado no Telegram.

## 5. Vantagens

- Separação de responsabilidades: geração e revisão são etapas distintas com critérios diferentes.
- Camada adicional de validação de conteúdo antes da aprovação humana.
- Detecção de problemas de tom, adequação ou vazamento de dados que o Rascunhador pode introduzir inadvertidamente.
- O loop de edição via Telegram dá mais controle ao usuário sem exigir intervenção técnica no fluxo.
- Mais robusto que a Solution A para casos onde o e-mail pode conter problemas sutis.

## 6. Limitações

- Maior número de chamadas ao modelo de linguagem por execução.
- Latência maior em comparação à Solution A.
- Dependência de modelos com bom desempenho para a etapa de revisão.
- Maior complexidade no workflow n8n.
- O loop de edição não tem limite de iterações definido, podendo exigir saída manual em casos extremos.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Agente Revisor aprovar rascunho com problemas. | Aprovação humana obrigatória como última barreira antes do envio. |
| Loop de revisão sem fim. | Limitar iterações e encaminhar para revisão manual após limite atingido. |
| Modelos locais de menor capacidade. | Usar Ollama com modelo de melhor desempenho disponível; testar antes de ativar. |
| Conflito entre decisões dos dois agentes. | Definir hierarquia: Revisor prevalece sobre Rascunhador no conteúdo do e-mail. |

## 8. Evidências coletadas

| Evidência | Arquivo | Descrição |
|-----------|---------|-----------|
| Mensagem de aprovação inicial | `docs/evidences/evidence1.png` | Telegram com rascunho da Invoice #018, período 16–30 de abril, 65 horas, com instruções de aprovação. |
| Rascunho revisado após "edit" | `docs/evidences/evidence2.png` | Telegram com e-mail reformatado pelo Revisor: tom formal, notas de alteração e campos rastreados. |
| Confirmação de envio | `docs/evidences/evidence3.png` | Telegram confirmando que o e-mail foi enviado com sucesso pelo Gmail. |
| E-mail enviado (revisado) | `docs/evidences/evidence5.png` | Gmail mostrando o e-mail revisado entregue ao destinatário. |
| Google Drive com rascunhos | `docs/evidences/evidence7.jpeg` | Pasta "Invoices/Draft" com histórico de rascunhos da Invoice-018 gerados pelo fluxo. |

## 9. Status

Implementada. Workflow exportado em `automation-invoice-two-agent-review-ngrok.json`. Fluxo testado de ponta a ponta: geração pelo Rascunhador, revisão pelo Revisor, aprovação via Telegram com uso do comando `edit`, e envio por Gmail com registro no Google Drive.
