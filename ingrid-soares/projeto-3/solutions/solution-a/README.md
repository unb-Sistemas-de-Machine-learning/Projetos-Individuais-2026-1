# Solution A: Planejamento Tático de Red Team

Esta solução implementa a primeira fase do framework de Red Team automatizado: o **Planejamento Tático**.

## Objetivo
Utilizar o Gemini para gerar um plano de ataque estruturado baseado em um alvo fornecido, dividindo a tarefa em três fases críticas:
1.  `fase_reconhecimento`
2.  `fase_validacao`
3.  `relatorio_riscos`

## Implementação
O fluxo é orquestrado no **n8n** e consiste em:
- **Webhook:** Recebe o payload com o alvo (ex: `{"alvo": "exemplo.com"}`).
- **HTTP Request:** Envia o prompt para a API do Google Gemini (utilizando `gemini-1.5-flash`).
- **Validator Code:** Processa a resposta da LLM, limpando formatações Markdown e validando a presença obrigatória dos campos JSON.

## Como utilizar
1.  Importe o arquivo `workflow.json` no seu n8n.
2.  Ative o workflow para liberar a **Production URL** (`/webhook/redteam-start`).
3.  Envie uma requisição POST com o JSON de alvo para a URL de produção.

## Status
- [x] Implementado
- [x] Testado
- [x] Documentado
