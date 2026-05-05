# Solution C — Pipeline multi-etapas com validação de rota

## Visão geral

A Solução C foi desenhada para atender o requisito de abordagem multi-etapas. Em vez de resolver tudo em uma chamada, o fluxo separa a decisão em duas fases independentes: classificação e redação.

Arquivo de referência:

- `src/workflows/solution-c-multietapas.json`

## Como o fluxo funciona

1. **Webhook** recebe o chamado.
2. **Normalize Input** padroniza os campos de entrada.
3. **Input valido?** valida formato mínimo da mensagem.
4. **Gemini Classificacao** executa etapa 1 (triagem estruturada).
5. **Parse Classificacao** normaliza o JSON da etapa 1.
6. **Gemini Redacao** executa etapa 2 (redação da orientação ao usuário).
7. **Parse Etapa 2 + Rota** aplica validação operacional:
  - urgência alta -> `escala`
  - confiança baixa -> `revisao`
  - demais casos -> `auto`
8. **Switch Rota** direciona o comportamento final.
9. **Sheets Log Tickets** grava auditoria.
10. **Respond OK** responde ao webhook.

## Por que esta solução é multi-etapas

Esta solução implementa cadeia de decisão explícita:

- Etapa 1: “o que o caso é?” (classificação).
- Etapa 2: “como responder ao usuário?” (redação condicionada pela etapa 1).
- Pós-processamento: validação e roteamento com regras de negócio.

Com isso, a lógica de triagem e a lógica de comunicação ficam desacopladas.

## Papel da validação no fluxo

Mesmo com saída da IA, o fluxo não executa ação cega. O nó `Parse Etapa 2 + Rota` impõe regras determinísticas para reduzir risco operacional e encaminhar casos sensíveis para revisão.

## Pontos fortes

- Atende claramente o critério de fluxo multi-etapas.
- Melhor separação de responsabilidades entre nós e prompts.
- Facilidade de ajuste fino por etapa (classificação vs. redação).

## Limitações

- Duas chamadas de modelo por execução (maior custo/latência).
- Não utiliza base de conhecimento externa por padrão (diferente da Solução B).
- Sensível a rate limit em ambiente gratuito.

## Configuração mínima no n8n

- Importar `solution-c-multietapas.json`.
- Configurar `x-goog-api-key` nos nós `Gemini Classificacao` e `Gemini Redacao`.
- Configurar credencial Google Sheets no nó `Sheets Log Tickets`.
- Substituir `SUBSTITUA_ID_PLANILHA` pelo ID real da planilha.
- Confirmar cabeçalhos da aba `Tickets` compatíveis com o mapeamento.

## Cenários de teste recomendados

- Chamado com alta urgência para validar rota `escala`.
- Chamado ambíguo para validar rota `revisao`.
- Chamado simples para validar rota `auto`.
- Entrada inválida para validar resposta de erro.

## Critérios de evidência

- Execução com duas etapas de IA concluídas.
- Rota coerente com regras de urgência/confiança.
- Registro da execução em `Tickets`.
- Resposta final do webhook contendo `modo: multietapas`.

## Evidências desta solução

As evidências visuais da solução C estão em [../../docs/evidence/](../../docs/evidence/).
