# Mentorship Pack — Diretrizes para Triagem de Consumo (CDC)

## Objetivo
Este documento orienta a construção do agente para garantir que ele atue como um analista jurídico rigoroso, priorizando a segurança do consumidor e a conformidade com o Código de Defesa do Consumidor (CDC).

## Princípios de Julgamento
O agente deve priorizar:
- **Segurança Jurídica:** Nunca inventar prazos ou artigos.
- **Proteção ao Vulnerável:** Casos envolvendo serviços essenciais (água, luz, saúde) devem ter prioridade máxima.
- **Estrutura:** A saída deve ser puramente técnica (JSON) para que o n8n não quebre.

## Padrões de Arquitetura
- **Orquestração:** O n8n deve controlar os desvios (Switch) baseado na confiança da IA.
- **Rastreabilidade:** Toda reclamação deve ser salva no Google Sheets antes de qualquer outra ação.
- **Fallback:** Se a IA falhar ou a confiança for < 0.70, o fluxo deve obrigatoriamente encaminhar para um humano.

## Qualidade Esperada
- **Boa resposta:** "categoria: URGENTE, artigo_cdc: Art. 22, confianca: 0.95".
- **Má resposta:** Texto solto como "Acho que o senhor tem direito a reclamar", sem estrutura de dados.

## Orientações para as 3 Soluções
1. **Solution-A (Prompt-only):** Testar a capacidade nativa do Gemini em classificar o CDC.
2. **Solution-B (RAG):** Fornecer o texto integral da Lei 8.078/90 (CDC) para evitar alucinações.
3. **Solution-C (Human-in-the-loop):** Implementar um nó de espera onde um humano revisa casos de alta complexidade.