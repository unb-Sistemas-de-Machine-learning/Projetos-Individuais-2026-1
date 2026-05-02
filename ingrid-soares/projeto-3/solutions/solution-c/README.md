# Solution C: Orquestrador Inteligente

Esta solução atua como o **cérebro central** do framework, integrando as fases de planejamento (Solution A) e validação (Solution B).

## Objetivo
Orquestrar a execução paralela das etapas de reconhecimento e validação, garantindo que o sistema funcione de forma assíncrona e performática.

## Implementação
- **Orquestração Assíncrona:** Utiliza um webhook com `responseMode: onReceived` para responder imediatamente ao usuário, processando as tarefas em segundo plano.
- **Execução Paralela:** Dispara as Solutions A e B simultaneamente via requisições HTTP.

## Integração e Testes
- A integridade do workflow orquestrado é validada pela **[Solution D: Infraestrutura de Testes](../solution-d/README.md)**, que automatiza o disparo e a validação do ciclo.

## Procedimento de Teste (ReqBin)
Para validar a integração manualmente:
1. **Método:** POST
2. **URL:** `https://ingrdsoares.app.n8n.cloud/webhook/redteam-orchestrator`
3. **Payload (JSON):** `{"alvo": "exemplo.com"}`
4. **Resultado:** Resposta imediata `{"message": "Workflow was started"}`.

## Status
- [x] Implementado
- [x] Testado
- [x] Documentado
