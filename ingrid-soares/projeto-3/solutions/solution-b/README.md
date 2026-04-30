# Solution B: Validação com Ferramentas e APIs Externas

Esta solução eleva a maturidade do framework ao introduzir a **validação prática**. O agente não apenas planeja, mas utiliza fontes de dados externas para confirmar suas hipóteses sobre o alvo.

## Objetivo
Validar hipóteses de vulnerabilidade através da integração com ferramentas de segurança e APIs, permitindo que a tomada de decisão da IA seja baseada em evidências reais (ex: reputação de domínio, registros DNS, dados públicos de segurança).

## Desenho do Fluxo no n8n
1.  **Webhook Trigger:** Recebe o JSON de entrada: `{ "alvo": "exemplo.com" }`.
2.  **Agente de IA (Planner):** Analisa o alvo e decide quais verificações técnicas são necessárias.
3.  **Tool Nodes (HTTP Requests):** O n8n executa as chamadas de API necessárias (ex: `whois`, `DNS lookup`, `VirusTotal API` para reputação de domínio).
4.  **Agente de IA (Analista):** Recebe o resultado bruto das ferramentas, processa os dados e sintetiza um parecer técnico.
5.  **HTTP Response:** Retorna o relatório validado com as evidências coletadas.

## Diferencial Técnico
- **Baseado em evidências:** A decisão final é ancorada em dados externos (não apenas no conhecimento prévio do modelo).
- **Orquestração de Ferramentas:** Demonstra a capacidade do n8n de conectar o agente de IA a um "ecossistema" de ferramentas de segurança.

## Exemplo de Lógica de Decisão
- "Agente Analista": *Recebi o resultado da ferramenta X. O score de reputação é 0 (Malicioso). Decisão: O alvo apresenta alto risco. Ação: Adicionar ao alerta de incidente.*

## Vantagens
- **Validação:** Reduz a taxa de falsos positivos da Solution A.
- **Automação:** Elimina a consulta manual de analistas em diversas ferramentas.

## Limitações
- **Dependência:** O fluxo depende da disponibilidade e dos limites de chamadas (rate limits) das APIs de terceiros.
- **Custos:** O uso frequente de APIs de segurança pode gerar custos ou exigir chaves de API específicas.
