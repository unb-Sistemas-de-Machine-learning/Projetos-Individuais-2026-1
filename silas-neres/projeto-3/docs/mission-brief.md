# Mission Brief — Agente de Triagem de Reclamações (CDC)

## Objetivo do agente
Projetar um agente de IA integrado ao n8n capaz de receber reclamações de consumidores, classificar a gravidade com base no Código de Defesa do Consumidor (CDC), identificar o artigo violado e direcionar a demanda para o canal correto (resolução automática, atendimento humano urgente ou arquivamento).

## Problema que ele resolve
Empresas e órgãos de defesa do consumidor sofrem com o volume de demandas. Muitas são dúvidas simples, enquanto outras são violações graves (como corte de serviços essenciais) que exigem ação imediata. O agente automatiza a triagem técnica que um atendente humano faria inicialmente.

## Usuários-alvo
- Departamentos de Customer Success (CS).
- Escritórios de advocacia que fazem triagem de leads.
- Pequenas empresas que precisam organizar o suporte jurídico.

## Contexto de uso
O consumidor preenche um formulário (n8n Form) relatando seu problema. O agente processa o relato e o n8n executa a lógica de negócio: dúvidas geram respostas automáticas; urgências disparam alertas; spam é descartado.

## Entradas esperadas
- Nome do consumidor.
- E-mail de contato.
- Descrição detalhada do problema ou incidente.
- Tipo de produto/serviço (opcional).

## Saídas esperadas
O agente deve retornar obrigatoriamente um JSON estruturado:
- **categoria**: (URGENTE, DUVIDA, RECLAMACAO_PADRAO, INVALIDO)
- **artigo_cdc**: O número do artigo do CDC que se aplica ao caso.
- **resumo_juridico**: Uma síntese do problema em termos técnicos.
- **urgencia_score**: Valor de 1 a 10.
- **acao_sugerida**: O que o fluxo deve fazer a seguir.
- **confianca**: Nível de certeza da IA na classificação.

## Limites do agente
O agente deve se limitar a problemas de consumo. Ele não deve prestar consultoria jurídica definitiva, apenas triagem. Ele não deve "inventar" leis que não existem no CDC.

## O que o agente não deve fazer
- Não deve garantir ganho de causa.
- Não deve usar linguagem informal ou ofensiva.
- Não deve processar dados se a descrição for curta demais (menos de 10 palavras).
- Não deve retornar texto fora do formato JSON.

## Critérios de aceitação
- Entrada via n8n Form ou Webhook.
- Uso de Agente de IA (Gemini) para tomada de decisão.
- Roteamento via Switch/IF baseado na categoria da IA.
- Registro de todas as entradas e decisões em Google Sheets (Auditoria).
- Notificação via e-mail ou Telegram para casos "URGENTES".
- Fallback para revisão humana em casos de baixa confiança (< 0.7).

## Riscos
- Erro de classificação de um caso grave como "dúvida".
- Alucinação de artigos do CDC (mitigado na Solução B com RAG).
- Falha na API do Gemini interrompendo o fluxo.