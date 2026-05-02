# Solution C: Fluxo Multi-etapas com Julgamento do Agente e Automação Condicional

## 1. Resumo

Esta solução propõe um workflow mais completo e automatizado. O n8n separa cálculo, validação, decisão, geração de nota fiscal, envio e registro de auditoria. A IA atua como agente de decisão: se os dados estiverem consistentes e a confiança for alta, o fluxo pode seguir automaticamente para geração e envio; se houver dúvida, baixa confiança ou inconsistência, o fluxo solicita revisão humana via Telegram.

Esta alternativa é propositalmente mais automatizada para comparação arquitetural. Ela demonstra um desenho em que o agente tem maior autonomia operacional, mas ainda preserva mecanismos de fallback e rastreabilidade.

## 2. Fluxo proposto

```text
Schedule Trigger
-> Set Billing Period
-> Fetch Productive.io Time Entries
-> Parse Entries and Calculate Amount
-> AI Validation and Decision
-> Normalize AI JSON
-> Switch recommended_action
   -> auto_send: gerar nota fiscal, exportar PDF, enviar Gmail e registrar log
   -> needs_manual_review: solicitar revisão via Telegram
   -> stop: registrar interrupção
```

Versão com aprovação humana opcional:

```text
needs_manual_review
-> Telegram Approval Request
-> IF approved
   -> gerar nota fiscal
   -> exportar PDF
   -> enviar Gmail
   -> registrar log
-> IF rejected
   -> registrar rejeição
```

## 3. Papel da IA

A IA decide se o caso pode seguir automaticamente ou se precisa de intervenção humana.

Ela deve avaliar:

- Completude do período.
- Existência de entradas.
- Total de horas.
- Valor total.
- Avisos do fluxo.
- Coerência geral do rascunho.
- Risco de envio inadequado.
- Adequação do e-mail externo.

## 4. Ações recomendadas

Esta proposta usa uma extensão do schema para permitir automação direta:

```json
{
  "confidence": "high | medium | low",
  "recommended_action": "auto_send | needs_manual_review | stop",
  "summary": "Resumo da decisão.",
  "detected_issues": [],
  "telegram_message": "Mensagem para revisão humana quando necessária.",
  "email_subject": "Assunto do e-mail ao contratante.",
  "email_body": "Corpo do e-mail ao contratante."
}
```

Regras:

- `auto_send`: permitido apenas quando a confiança for alta, não houver problemas detectados e os dados essenciais estiverem presentes.
- `needs_manual_review`: usado quando houver ambiguidade, aviso, confiança média/baixa ou e-mail potencialmente inadequado.
- `stop`: usado quando faltarem dados essenciais ou houver risco crítico.

## 5. Decisão automatizada

Esta alternativa permite que o workflow envie a nota fiscal sem aprovação humana explícita quando a IA indicar `auto_send`.

Critérios para `auto_send`:

- `confidence` igual a `high`.
- `detected_issues` vazio.
- `entry_count` maior que zero.
- `total_hours` maior que zero.
- `amount` presente e numérico.
- `period_start` e `period_end` presentes.
- Sem avisos críticos em `warnings`.
- E-mail externo sem detalhes internos proibidos.

Se qualquer critério falhar, o fluxo não envia automaticamente e solicita revisão humana.

## 6. Vantagens

- Maior automação do processo.
- Reduz intervenção humana em casos rotineiros.
- Demonstra uso mais forte da IA como componente de decisão.
- Expõe claramente o trade-off entre autonomia e segurança.
- Mantém rastreabilidade se todos os inputs, outputs e decisões forem registrados.

## 7. Limitações

- Risco maior que as soluções com aprovação humana obrigatória.
- Depende mais do julgamento da IA.
- Exige validação forte da saída do modelo.
- Pode ser inadequada para uso real sem critérios de confiança muito bem testados.
- Requer logs detalhados para justificar envios automáticos.

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Envio automático incorreto. | Exigir confiança alta, zero problemas detectados e validações determinísticas antes do envio. |
| IA classificar caso arriscado como seguro. | Aplicar guardrails determinísticos depois da IA. |
| E-mail externo conter dados internos. | Validar termos proibidos antes de Gmail. |
| Auditoria insuficiente. | Registrar input, decisão, output, e-mail, arquivo gerado e status do envio. |
| Credenciais expostas. | Usar credenciais n8n e remover tokens do JSON exportado. |

## 9. Evidência mínima esperada

- Execução com `auto_send` em dados simulados válidos.
- Execução com `needs_manual_review` em dados suspeitos.
- Execução com `stop` em dados inválidos.
- Log mostrando decisão da IA e validações determinísticas.
- Evidência de envio ou simulação de envio.
- Evidência de revisão humana quando a confiança não for alta.

## 10. Status

Proposta avançada. É útil para comparação porque maximiza automação e demonstra autonomia do agente, mas provavelmente exige mais testes e guardrails para ser considerada segura em uso real.
