# Solution A: Validação Simples Baseada em Prompt

## 1. Resumo

Esta solução usa uma abordagem simples: o n8n calcula o período de faturamento, busca entradas de tempo no Productive.io, consolida horas e valor total em nós determinísticos e envia esse resumo para um agente de IA em uma única chamada.

O agente analisa os dados consolidados, identifica problemas evidentes, recomenda o próximo passo e gera a mensagem interna de aprovação e o e-mail ao contratante.

## 2. Fluxo proposto

```text
Schedule Trigger
-> Set Billing Period
-> Fetch Productive.io Time Entries
-> Parse Entries and Calculate Amount
-> AI Validation and Message Draft
-> IF recommended_action
   -> request_approval: enviar mensagem no Telegram
   -> needs_manual_review: solicitar revisão manual
   -> stop: registrar interrupção
```

## 3. Papel da IA

A IA recebe um JSON consolidado com:

- Período de faturamento.
- Quantidade de entradas.
- Total de minutos.
- Total de horas.
- Valor por hora.
- Moeda.
- Valor total.
- Avisos.
- Lista resumida de entradas.

A IA deve retornar:

- Nível de confiança.
- Ação recomendada.
- Problemas detectados.
- Resumo interno.
- Mensagem para Telegram.
- Assunto e corpo do e-mail.

## 4. Decisão automatizada

A decisão da IA influencia diretamente o caminho do workflow:

- `request_approval`: o fluxo solicita aprovação humana via Telegram.
- `needs_manual_review`: o fluxo solicita revisão manual antes de continuar.
- `stop`: o fluxo interrompe a execução e registra o motivo.

Nesta proposta, o envio final ainda depende de aprovação humana. A solução serve como baseline simples para avaliar se uma única chamada de IA é suficiente.

## 5. Vantagens

- Simples de implementar.
- Baixo custo operacional.
- Poucos nós no n8n.
- Fácil de explicar e demonstrar.
- Boa opção para protótipo inicial.

## 6. Limitações

- Depende fortemente da qualidade do prompt.
- Menor robustez contra JSON inválido ou resposta ambígua.
- Pouca separação entre validação, redação e decisão.
- Pode gerar falsos positivos de aprovação se o prompt não cobrir bem os casos de risco.
- Não demonstra uma arquitetura tão forte quanto as alternativas com validação adicional ou múltiplas etapas.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| IA retornar JSON inválido. | Adicionar nó simples de parsing e fallback para revisão manual. |
| IA ignorar algum aviso do fluxo. | Incluir `warnings` explicitamente no prompt. |
| IA gerar e-mail com detalhes internos. | Definir regras rígidas no prompt e testar exemplos negativos. |
| Baixa auditabilidade. | Registrar input, output da IA e decisão tomada. |

## 8. Evidência mínima esperada

- Exemplo de input JSON consolidado.
- Exemplo de output JSON válido da IA.
- Print do workflow com a chamada única ao modelo.
- Print ou log do caminho condicional escolhido.

## 9. Status

Proposta inicial. Deve ser implementada como baseline para comparação com as demais soluções.
