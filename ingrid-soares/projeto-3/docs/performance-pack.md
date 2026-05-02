# Performance & Sustentabilidade Financeira

Este documento detalha as métricas de performance e o custo operacional do framework de Red Team, agora otimizado para uma **arquitetura híbrida**.

## 1. Visão Geral da Evolução
O framework evoluiu para um modelo **Híbrido**, que combina a precisão de uma camada determinística (baseada em regras) com a inteligência contextual de LLMs via APIs de tier gratuito. Esta mudança otimiza a performance sem incorrer em custos operacionais.

## 2. Estimativas de Custo
A adoção de serviços gratuitos de alta capacidade (VirusTotal API e Groq Cloud API) permitiu a eliminação total de custos variáveis.

| Componente | Custo Operacional (Estimado) | Base de Cálculo |
| :--- | :--- | :--- |
| **Orquestração (n8n)** | Zero | Tier gratuito |
| **Inteligência (API VT)** | Zero | Tier gratuito |
| **IA (Groq/Llama-3)** | Zero | Tier gratuito (Free-tier ilimitado) |
| **Total** | **$0.00 / mês** | - |

## 3. Performance e Confiabilidade
- **Latência:** Otimizada através da execução condicional da IA. A IA é acionada apenas quando o motor determinístico detecta ameaças, economizando tempo e recursos.
- **Confiabilidade:** Alta. A validação binária inicial garante que apenas dados relevantes e precisos sejam submetidos à análise estratégica da IA.
- **Escalabilidade:** Arquitetura pronta para alta demanda, limitada apenas pelos *rate limits* dos serviços gratuitos utilizados.

## 4. Práticas de Otimização
Para manter o framework eficiente:
- **Execução Condicional:** A IA só é invocada se o filtro determinístico (VT) detectar indicadores de risco.
- **Tratamento de Erros:** Uso de retries nativos do n8n para falhas de rede.
- **Processamento Enxuto:** Uso de nós `Code` para normalizar dados antes do envio para a camada de IA.
