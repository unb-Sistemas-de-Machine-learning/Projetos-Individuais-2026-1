# Diretrizes de Resiliência e Observabilidade - Red Team Framework

Este documento estabelece as estratégias de resiliência, validação e auditoria para o sistema híbrido de validação de segurança.

---

## 1. Validação Híbrida (Schema & Fatos)
- **Filtro Determinístico:** Toda consulta externa passa por uma etapa de normalização (`Code` node) que valida a existência dos campos esperados na resposta (ex: `last_analysis_stats` do VirusTotal).
- **Tratamento de Falha:** Caso a API falhe, o nó `HTTP Request` está configurado para o fluxo seguir para um caminho de log de erro, evitando a interrupção da orquestração principal.

## 2. Política de Retry (Resiliência)
Todas as chamadas para APIs externas (Groq, VirusTotal) possuem políticas de retentativa configuradas no n8n:
- **Max Retries:** 3 tentativas.
- **Backoff:** Intervalo crescente (5s, 15s, 30s).

## 3. Auditoria e Rastreabilidade
- **Centralização:** O Workflow C atua como o ponto central. Todas as execuções (A, B e C) são auditadas via aba "Executions" do n8n.
- **Persistência:** Resultados de alto risco são processados para garantir que nenhuma evidência de segurança seja perdida.

## 4. Garantia de Qualidade (QA)
- **Infraestrutura de Testes (Solution D):** A integridade de todo o sistema é validada automaticamente por scripts que simulam requisições de produção e conferem o sucesso das execuções, garantindo um ambiente resiliente e confiável.
