# Solution B: Validação com Base de Conhecimento de Notas Anteriores

## 1. Resumo

Esta solução acrescenta uma camada de memória histórica ao fluxo. Além dos dados calculados deterministicamente pelo n8n, o agente de IA recebe como contexto registros de notas fiscais e e-mails anteriores recuperados de uma base de conhecimento. Com essa referência, o agente pode comparar o rascunho atual com padrões históricos e identificar anomalias que uma análise isolada não detectaria, como uma queda brusca de horas em relação à média dos últimos ciclos ou uma variação incomum no valor faturado.

## 2. Fluxo proposto

```text
Schedule Trigger
→ Calcular período de faturamento
→ Buscar entradas no Productive.io (HTTP Request)
→ Consolidar horas e calcular valor (Code)
→ Consultar base de conhecimento histórica (HTTP Request / Sheets)
→ Agente de IA (com contexto histórico): validar, comparar e redigir rascunho
→ Normalizar JSON da IA (Code)
→ Switch: recommended_action
   → request_approval: enviar rascunho ao Telegram para aprovação
   → needs_manual_review: solicitar revisão manual
   → stop: registrar interrupção
```

## 3. Papel da base de conhecimento

A base de conhecimento armazena dados de execuções anteriores:

- Número da nota fiscal, período, total de horas e valor de faturamentos anteriores.
- Corpo e assunto dos e-mails aprovados e enviados em ciclos anteriores.
- Registros de revisões manuais e motivos de rejeição.

Antes de acionar o modelo, o n8n consulta essa base e recupera os registros mais relevantes para o período atual — por exemplo, os últimos dois ou três ciclos de faturamento. Esses dados são incluídos no prompt como contexto histórico.

## 4. Papel da IA

Com o histórico disponível como contexto, o agente pode:

- Comparar o total de horas atual com a média histórica e sinalizar desvios relevantes.
- Verificar se o valor calculado está dentro da faixa esperada para o contratante.
- Usar os e-mails aprovados anteriormente como referência de estilo e tom.
- Detectar inconsistências que só fazem sentido em comparação com o histórico, como queda brusca de horas sem registro de ausência ou aumento anormal do valor.

## 5. Implementação possível

A base de conhecimento poderia ser implementada de três formas:

| Abordagem | Descrição | Complexidade |
|-----------|-----------|-------------|
| Google Sheets | Registro estruturado de notas anteriores; consulta via HTTP Request | Baixa |
| Google Drive (documentos) | Armazenamento de PDFs e e-mails aprovados; busca por nome ou data | Média |
| Vector store (ex.: Chroma, Qdrant) | Busca semântica por similaridade; recuperação mais inteligente | Alta |

## 6. Vantagens

- Detecção de anomalias que dependem de contexto histórico.
- Estilo de e-mail mais consistente com o histórico aprovado.
- Base para implementação de memória de longo prazo no agente.
- Reduz dependência exclusiva do prompt para definir o comportamento esperado.

## 7. Limitações

- Exige estruturação e manutenção da base de conhecimento.
- A consulta ao histórico adiciona latência ao fluxo.
- A qualidade depende da completude e consistência dos registros anteriores.
- Nos primeiros ciclos, a base está vazia e o benefício é mínimo.

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| Base vazia nos primeiros ciclos. | Aceitar ausência de histórico e degradar para o comportamento da Solution A. |
| Dados históricos inconsistentes. | Validar entradas antes de armazenar na base. |
| Custo de consulta a vector store. | Preferir abordagem simples (Sheets) inicialmente. |
| Privacidade dos dados históricos. | Armazenar apenas campos não sensíveis ou com acesso restrito. |

## 9. Evidência mínima esperada

- Exemplo de consulta à base retornando registros de ciclos anteriores.
- Exemplo de resposta da IA com referência ao histórico.
- Evidência de anomalia detectada via comparação histórica.

## 10. Status

Proposta não implementada. Representa uma evolução natural da Solution A, com ganho de auditabilidade e detecção de anomalias históricas. A implementação foi descartada para este ciclo por exigir infraestrutura adicional e por não ser necessária para o problema imediato. Pode ser adicionada como extensão futura usando o Google Sheets já integrado ao fluxo como destino de log.
