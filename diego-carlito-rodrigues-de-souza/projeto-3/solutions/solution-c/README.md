# Solution C: Fluxo Agêntico Multi-etapas com Roteamento Híbrido

## Visão Geral
A solução final atende integralmente ao Mission Brief. Ela divide o trabalho: a IA classifica intenções (NLU) e o n8n executa a lógica booleana de roteamento.

## Fluxo Lógico Híbrido (n8n)
1. **Webhook Trigger:** Recebe o input.
2. **LLM Node (Classificador JSON):** Analisa a mensagem e extrai `categoria`, `confianca` e a diretriz `route_to` (ex: `tecnica`, `administrativa`, `excecao`).
3. **Switch Node (n8n):** O cérebro do orquestrador. Lê a chave `route_to` do JSON.
   - **Caminho 1 (Técnica):** Direciona para um segundo LLM instruído apenas para responder usando o Método Socrático.
   - **Caminho 2 (Administrativa):** Direciona para um nó do Google Sheets que salva a mensagem como um "log de secretaria". Responde ao aluno com uma string fixa do n8n: "Seu pedido foi registrado".
   - **Caminho 3 (Exceção/Humano):** Dispara imediatamente um alerta no nó do Slack/Discord do professor com alta prioridade.
4. **Error Trigger (Global):** Intercepta falhas de API e aciona fallback.

## Por que foi a vencedora?
Cumpre a exigência central da disciplina: a IA atua **tomando decisão de fluxo**. A segurança acadêmica é mantida porque pedidos sensíveis sequer chegam na fase de "geração de texto", sendo barrados no nó Switch.

## Status:
✅ **Aprovada para Produção**. O JSON do n8n será exportado a partir desta arquitetura.
