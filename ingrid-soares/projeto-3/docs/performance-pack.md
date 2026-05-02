# Performance & Sustentabilidade Financeira

Este documento detalha as métricas de performance e o custo operacional do framework de Red Team, agora otimizado para uma arquitetura determinística.

## 1. Visão Geral da Evolução
O framework migrou de um modelo baseado em IA probabilística para uma arquitetura **Determinística (Rule-based)**. Esta mudança impactou diretamente as métricas de performance e custo, tornando o sistema financeiramente sustentável e tecnicamente mais previsível.

## 2. Estimativas de Custo
A adoção de APIs públicas (como o VirusTotal) em seus tiers gratuitos permitiu a eliminação de custos variáveis.

| Componente | Custo Operacional (Estimado) | Base de Cálculo |
| :--- | :--- | :--- |
| **Orquestração (n8n)** | Zero | Tier gratuito |
| **Inteligência (API VT)** | Zero | Tier gratuito |
| **LLM (Gemini)** | Zero | Abordagem determinística (não usa LLM) |
| **Total** | **$0.00 / mês** | - |

## 3. Performance e Confiabilidade
- **Latência:** Latência reduzida significativamente, pois a inferência de LLM foi removida, restando apenas o tempo de I/O das APIs.
- **Confiabilidade:** 100% de previsibilidade. A lógica baseada em regras elimina o risco de alucinações.
- **Escalabilidade:** Arquitetura altamente escalável, limitada apenas pelos *rate limits* das APIs.

## 4. Práticas de Otimização
Para manter o framework eficiente:
- **Tratamento de Erros:** Uso de retries nativos do n8n para falhas de rede.
- **Processamento Enxuto:** Uso de nós `Code` para normalizar dados apenas no necessário.
- **Auditoria:** Uso da aba "Executions" para monitoramento centralizado.
