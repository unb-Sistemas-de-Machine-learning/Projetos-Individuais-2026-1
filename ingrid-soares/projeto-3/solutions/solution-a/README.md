# Solution A: Planejamento Tático Baseado em Prompt

Esta solução é a base de maturidade inicial do nosso framework. O foco aqui não é a execução técnica, mas a capacidade do agente de **raciocinar** e **estruturar** um plano de Red Team de forma ética e profissional.

## Objetivo
Transformar uma entrada simples (alvo/domínio) em um plano de ataque estruturado que siga as melhores práticas de cibersegurança, servindo como uma "bússola" para as etapas subsequentes (B e C).

## Desenho do Fluxo no n8n
1.  **Webhook Trigger:** Recebe o JSON de entrada: `{ "alvo": "exemplo.com", "tipo_teste": "reconhecimento" }`.
2.  **LLM Node (Gemini):** Agente de IA com System Prompt especializado.
3.  **JSON Formatter:** Nó de código para padronizar a saída do LLM.
4.  **HTTP Response:** Retorna o plano formatado.

## System Prompt (O cérebro da Solution A)
```text
Você é um Operador de Red Team Senior.
Sua tarefa é analisar o alvo fornecido e gerar um plano de ataque tático.
O plano deve seguir as fases:
1. Reconhecimento (enumeração passiva e ativa).
2. Validação de Vulnerabilidades (priorizando OWASP Top 10).
3. Relatório de Riscos (severidade esperada e impacto).

Restrições:
- Seja estritamente profissional.
- Não sugira ataques de negação de serviço.
- Justifique tecnicamente cada etapa do plano.
- Saída deve ser um JSON estruturado.
```

## Vantagens
- **Simplicidade:** Implementação rápida e fácil de depurar.
- **Raciocínio:** Valida a capacidade do modelo de seguir diretrizes de cibersegurança.

## Limitações
- **Estático:** Não interage com sistemas reais.
- **Teórico:** O plano gerado pode conter sugestões que não se aplicam ao ambiente real do alvo.
