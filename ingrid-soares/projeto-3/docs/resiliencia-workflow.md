# Diretrizes de Resiliência e Observabilidade - Red Team Framework

Este documento estabelece as estratégias de resiliência, validação e auditoria para o sistema de triagem e teste de segurança automatizado.

---

## 1. Validação de Schema (JSON)
Para evitar que o sistema processe saídas malformadas do LLM, toda resposta de IA será submetida a uma etapa de validação:
- **Implementação no n8n:** Adicionar nó "Code" após o nó de IA para executar um `JSON.parse()`.
- **Ação em Falha:** Se o parse falhar, o fluxo entra em um caminho de erro (Fallback), acionando uma nova tentativa com um prompt mais restritivo ou enviando alerta ao analista.

## 2. Política de Retry (Resiliência)
Todas as chamadas para APIs externas (LLM e Ferramentas de Segurança) devem ter políticas de retentativa configuradas:
- **Max Retries:** 3 tentativas.
- **Backoff:** Intervalo crescente entre tentativas (5s, 15s, 30s) para evitar sobrecarga em APIs externas.

## 3. Logs de Auditoria (Persistência)
Para garantir a rastreabilidade exigida pelo projeto:
- **Armazenamento:** Cada execução deve salvar no banco de dados/planilha:
    - `timestamp`
    - `input_json` (payload original)
    - `ia_raw_response` (resposta bruta do modelo)
    - `decision_log` (motivação do agente)
    - `status` (success/error)

## 4. Tratamento de Erros e Fallback
- **Caminhos de Erro:** Todo nó de integração deve possuir uma conexão "Error Trigger" no n8n.
- **Intervenção Humana:** Caso a IA não consiga classificar a severidade (confiança < 70%), o sistema deve pausar e enviar uma notificação ao canal de suporte humano.
