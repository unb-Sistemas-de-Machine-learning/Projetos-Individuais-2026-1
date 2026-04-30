# Performance & Cost Pack: Multi-Agent Red Team Framework

Este documento detalha as métricas de performance, consumo de recursos e estimativas de custo operacional do framework de Red Team.

---

## 1. Estimativa de Consumo de IA (LLM Tokens)
O consumo de tokens é calculado com base no uso do Gemini para análise estratégica (Agente Analista):

| Solution | Tokens Médios/Execução | Estimativa de Custo (aprox.) |
|----------|------------------------|------------------------------|
| A        | 200 - 400              | Baixo                        |
| B        | 500 - 800              | Médio                        |
| C        | 1200 - 2000            | Moderado                     |

## 2. Estratégias de Otimização
Para reduzir custos e latência, adotamos as seguintes práticas:
- **Cache Local:** Resultados de consultas DNS e reputação de IPs são armazenados temporariamente no banco de dados do n8n por 24 horas para evitar chamadas redundantes a APIs pagas (como VirusTotal).
- **Prompt Engineering:** Prompts otimizados para extrair apenas informações essenciais em formato JSON, reduzindo o tamanho do prompt e da resposta.
- **Fail-Fast:** O fluxo de decisão no n8n é estruturado para interromper o teste imediatamente caso uma vulnerabilidade crítica seja confirmada, poupando tokens de análises subsequentes.

## 3. Análise de Latência
- **Latência Total Esperada:** 5 a 15 segundos.
- **Distribuição do Tempo:**
    - ~70% em chamadas de I/O (APIs externas: DNS/VirusTotal).
    - ~25% em inferência de IA.
    - ~5% em processamento interno do n8n.
