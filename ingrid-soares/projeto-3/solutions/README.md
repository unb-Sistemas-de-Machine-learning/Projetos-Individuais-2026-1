# Framework de Soluções: Red Team Framework

Este diretório contém a implementação modular do framework de segurança automatizado, estruturado em quatro soluções que operam de forma integrada.

## Estrutura das Soluções

O framework foi desenhado em uma arquitetura **Híbrida (Determinística + LLM)** para garantir precisão técnica, previsibilidade de custos e inteligência contextual.

### [Solution A: Planejamento Tático](./solution-a/README.md)
- **Foco:** Reconhecimento e definição do plano de ataque.
- **Tecnologia:** LLM (Groq Cloud/Llama-3).

### [Solution B: Validação Prática](./solution-b/README.md)
- **Foco:** Validação determinística de ativos.
- **Tecnologia:** API VirusTotal (Determinístico).

### [Solution C: Orquestrador Inteligente](./solution-c/README.md)
- **Foco:** Integração assíncrona e orquestração.
- **Tecnologia:** n8n (Orquestração de fluxos).

### [Solution D: Infraestrutura de Testes](./solution-d/README.md)
- **Foco:** Qualidade e garantia de integração.
- **Tecnologia:** Python (Pytest/Requests) para testes automatizados.

## Fluxo de Integração
1. O **Orquestrador (C)** recebe o alvo via Webhook.
2. Dispara simultaneamente a **Solution A** (análise estratégica via LLM) e a **Solution B** (validação técnica determinística).
3. A **Solution D** valida a integridade do ciclo completo.

## Como começar
Recomendamos a leitura do [Relatório Técnico](../relatorio-entrega.md) para uma visão geral da arquitetura e as diretrizes de performance no [Performance Pack](../docs/performance-pack.md).
