# Solution A: Planejamento Tático de Red Team

Esta solução implementa a fase de **Planejamento Tático** do framework.

## Objetivo
Gerar planos de ataque estruturados (reconhecimento, validação e riscos) utilizando inteligência artificial.

## Evolução Tecnológica
- **Migração:** Inicialmente projetada com Gemini, o fluxo foi migrado para o modelo **Llama-3 via Groq Cloud** para otimizar custos (Free-tier) e performance.

## Implementação
O fluxo no **n8n** utiliza:
- **Webhook:** Entrada de dados (`alvo`).
- **HTTP Request:** Chamada à API de LLM (Groq Cloud) com normalização JSON.

## Próximos Passos
O resultado desta etapa alimenta a **[Solution B: Validação Prática](../solution-b/README.md)**. A integração completa é realizada pelo **[Orquestrador (Solution C)](../solution-c/README.md)**.
