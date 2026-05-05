# Workflow Runbook — Processo de Execução

## Processo Obrigatório
1. **Configuração inicial:** Criar Webhook/Form no n8n para entrada de dados.
2. **Setup da IA:** Configurar nó AI Agent com Google Gemini.
3. **Persistência:** Criar nó Google Sheets para log de auditoria.
4. **Lógica Condicional:** Implementar Switch baseado no campo `categoria` da IA.
5. **Integração:** Configurar envio de e-mail (Gmail) ou alerta (Telegram).

## Fluxo Técnico Esperado
1. **Input:** Recebe `nome` e `descricao_problema`.
2. **Processamento:** O Agente analisa se há violação do CDC e gera o JSON.
3. **Validação:** O n8n verifica se o JSON é válido.
4. **Log:** Grava tudo no Google Sheets (Independente do resultado).
5. **Roteamento:** 
    - `URGENTE` -> Dispara alerta imediato.
    - `DUVIDA` -> Envia resposta automática por e-mail.
    - `INVALIDO/BAIXA CONFIANÇA` -> Move para aba de "Revisão Humana".

## Casos de Teste Mínimos
- **Teste 1 (Urgente):** "Cortaram minha água por conta atrasada faz 1 hora".
- **Teste 2 (Dúvida):** "Qual o prazo para trocar uma camisa que não serviu?".
- **Teste 3 (Inválido):** "Bom dia, gostaria de saber o clima hoje".
- **Teste 4 (Erro):** Enviar um texto vazio e validar se o sistema não trava.