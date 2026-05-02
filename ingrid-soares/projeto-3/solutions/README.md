# Framework de Soluções: Red Team Framework

Este diretório contém a implementação modular do framework de segurança automatizado, estruturado em três soluções que operam de forma integrada.

## Estrutura das Soluções

O framework foi desenhado em uma arquitetura **Híbrida (Determinística + LLM)** para garantir precisão técnica, previsibilidade de custos e inteligência contextual.

### [Solution A: Planejamento Tático](./solution-a/README.md)
- **Foco:** Reconhecimento e definição do plano de ataque.
- **Tecnologia:** Inicialmente projetado com Gemini, o fluxo foi migrado para o modelo **Llama-3 via Groq Cloud** para viabilizar a arquitetura de custo zero (Free-tier).
- **Status:** Implementado e documentado.

### [Solution B: Validação Prática](./solution-b/README.md)
- **Foco:** Validação determinística de ativos.
- **Tecnologia:** API VirusTotal (Determinístico).
- **Status:** Implementado e documentado.

### [Solution C: Orquestrador Inteligente](./solution-c/README.md)
- **Foco:** Integração assíncrona e orquestração.
- **Tecnologia:** n8n (Orquestração de fluxos).
- **Status:** Implementado e documentado.

## Fluxo de Integração
1. O **Orquestrador (C)** recebe o alvo via Webhook.
2. Dispara simultaneamente a **Solution A** (análise estratégica via LLM híbrido) e a **Solution B** (validação técnica determinística).
3. Os resultados são integrados, garantindo uma resposta de segurança precisa e estruturada.

## Como começar
Recomendamos a leitura do [Relatório Técnico](../relatorio-entrega.md) para uma visão geral da arquitetura e as diretrizes de performance no [Performance Pack](../docs/performance-pack.md).
