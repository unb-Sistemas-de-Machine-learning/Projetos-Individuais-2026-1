# Solution B: Validação com Regras Externas e Agente de IA

## 1. Resumo

Esta solução combina cálculo determinístico, validações explícitas e agente de IA. Antes ou depois da chamada ao modelo, o n8n aplica regras objetivas para detectar problemas conhecidos, como ausência de período, zero entradas, zero horas, valor ausente, quantidade incomum de horas e resposta malformada da IA.

A IA continua responsável por interpretar o rascunho, resumir a situação, recomendar ação e gerar mensagens, mas sua decisão é limitada por uma camada de regras.

## 2. Fluxo proposto

```text
Schedule Trigger
-> Set Billing Period
-> Fetch Productive.io Time Entries
-> Parse Entries and Calculate Amount
-> Rule-Based Prevalidation
-> AI Validation and Message Draft
-> Normalize AI JSON
-> Rule-Based Decision Guard
-> Switch recommended_action
   -> request_approval: enviar mensagem no Telegram
   -> needs_manual_review: solicitar revisão manual
   -> stop: registrar interrupção
```

## 3. Papel das regras

As regras funcionam como uma política explícita de segurança. Elas não substituem a IA, mas impedem que decisões inseguras avancem.

Regras mínimas:

- Se `period_start` ou `period_end` estiver ausente, recomendar `stop`.
- Se `amount` estiver ausente ou não numérico, recomendar `stop`.
- Se `entry_count` for zero, recomendar `needs_manual_review`.
- Se `total_hours` for zero, recomendar `needs_manual_review`.
- Se houver avisos em `warnings`, recomendar no mínimo `needs_manual_review`, salvo exceção justificada.
- Se a IA retornar JSON inválido, recomendar `needs_manual_review` ou `stop`.
- Se o e-mail contiver termos proibidos, como IA, aprovação, validação, horas, período ou valor total, solicitar revisão manual.

## 4. Papel da IA

A IA deve:

- Validar a completude do rascunho.
- Identificar anomalias práticas não cobertas pelas regras simples.
- Gerar um resumo interno.
- Gerar mensagem de Telegram.
- Gerar e-mail externo simples.

A IA não deve:

- Recalcular valores.
- Ignorar as regras objetivas.
- Aprovar envio externo por conta própria.

## 5. Decisão automatizada

A decisão final resulta da combinação entre regras e IA:

- Se regras críticas falharem, elas prevalecem sobre a IA.
- Se a IA recomendar aprovação, mas uma regra detectar risco, o fluxo vai para revisão manual.
- Se regras e IA indicarem segurança, o fluxo solicita aprovação via Telegram.

Nesta solução, o envio final ainda depende de aprovação humana.

## 6. Vantagens

- Mais robusta que uma solução baseada apenas em prompt.
- Regras são auditáveis e fáceis de testar.
- Reduz dependência de comportamento probabilístico da IA.
- Facilita demonstrar tratamento de erros e limites.
- Mantém arquitetura relativamente simples.

## 7. Limitações

- Exige manutenção das regras.
- Pode bloquear execuções válidas por excesso de cautela.
- Ainda depende da IA para gerar mensagens e resumir casos ambíguos.
- Não automatiza totalmente o envio, pois mantém aprovação humana obrigatória.

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Regra bloquear caso válido. | Registrar motivo e permitir aprovação manual. |
| Regra não cobrir anomalia específica. | Registrar evidências e atualizar política. |
| IA gerar e-mail inadequado. | Validar termos proibidos antes do envio. |
| Aumento de complexidade. | Manter regras curtas, explícitas e documentadas. |

## 9. Evidência mínima esperada

- Exemplo de execução com dados válidos.
- Exemplo de execução com zero entradas.
- Exemplo de resposta inválida da IA e fallback.
- Print ou log das regras alterando ou confirmando a decisão da IA.

## 10. Status

Proposta intermediária. Deve ser prototipada para comparar se a camada de regras aumenta a segurança sem deixar o workflow excessivamente complexo.
