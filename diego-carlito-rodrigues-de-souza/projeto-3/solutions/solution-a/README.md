# Solution A: Abordagem Simples Baseada em Prompt

## Visão Geral
Esta foi a primeira prototipação arquitetural. O objetivo era testar a latência mínima: receber a mensagem e devolver a resposta na mesma execução, usando apenas um nó de LLM.

## Fluxo Lógico (n8n)
1. **Webhook Trigger:** Recebe o payload JSON do aluno.
2. **Basic LLM Chain:** Nó que engloba o Llama-3/Groq. Recebe o input do aluno e um `System Prompt` genérico mandando ele agir como monitor.
3. **Webhook Response:** Devolve a string gerada pelo LLM para o chat do aluno.

## Avaliação Rápida
- **Prós:** Extremamente fácil de implementar. Baixa latência.
- **Contras (O porquê de ser descartada):** Fere a regra vital de "Decidir, não apenas responder". Se o aluno pedir para alterar a nota, o LLM vai tentar dar uma desculpa gerada proceduralmente em vez de parar o fluxo e alertar o professor. Falta governança.

## Status:
❌ Descartada a favor de fluxos condicionais.
