# Solution B: Validação Prática de Red Team

Esta solução implementa a fase de **Validação Prática** (Camada Determinística).

## Objetivo
Validar ativos de forma automatizada e factual, sem dependência de probabilidade.

## Implementação
- **Motor:** Integração via API VirusTotal (v3).
- **Lógica:** Consulta de reputação de domínios/IPs com normalização de dados via nó `Code` no n8n.
- **Autenticação:** Header seguro `x-apikey`.

## Integração
Este workflow é disparado paralelamente à Solution A pelo **[Orquestrador (Solution C)](../solution-c/README.md)**. A validação retorna um resumo de segurança factual que, em conjunto com o planejamento (A), compõe o parecer final.
