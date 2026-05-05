# Solution A — Prompt único com roteamento

## Visão geral

A Solução A implementa a abordagem mais simples do projeto: uma única chamada ao modelo Gemini para classificar o chamado e extrair um objeto JSON estruturado. A partir dessa estrutura, o n8n decide a rota do atendimento e registra a execução em planilha.

Arquivo de referência:

- `src/workflows/solution-a-prompt-simples.json`

## Como o fluxo funciona

1. **Webhook** recebe `message` e opcionalmente `email`.
2. **Normalize Input** padroniza os campos de entrada.
3. **Input valido?** bloqueia mensagens vazias ou curtas.
4. **Gemini Triagem** devolve JSON com `categoria`, `urgencia`, `confianca` e `resumo_curto`.
5. **Parse e Rota** valida o JSON e define `rota` (`auto`, `revisao`, `escala`).
6. **Switch Rota** seleciona o caminho de resposta.
7. **Sheets Log Tickets** persiste auditoria em `Tickets`.
8. **Respond OK** retorna a resposta HTTP final.

## Decisão de IA nesta abordagem

A IA afeta diretamente o comportamento do fluxo: os campos `urgencia` e `confianca` influenciam a rota escolhida e o tipo de resposta enviada.

## Pontos fortes

- Menor custo e menor latência (apenas uma chamada de modelo).
- Menor complexidade de operação e manutenção.
- Bom baseline para comparação com soluções mais sofisticadas.

## Limitações

- Não utiliza base de conhecimento externa.
- Menor capacidade de contextualização da orientação ao usuário final.
- Qualquer falha da única chamada de IA impacta a qualidade da triagem.

## Configuração mínima no n8n

- Importar o workflow `solution-a-prompt-simples.json`.
- Configurar `x-goog-api-key` no nó `Gemini Triagem`.
- Configurar credencial Google Sheets no nó `Sheets Log Tickets`.
- Substituir `SUBSTITUA_ID_PLANILHA_TICKETS` pelo ID real da planilha.
- Garantir cabeçalhos da aba `Tickets` compatíveis com o mapeamento do nó.

## Cenários de teste recomendados

- Chamado simples: “Esqueci minha senha”.
- Chamado crítico: “Sistema fora do ar para todos”.
- Entrada inválida: mensagem curta/vazia.

## Critérios de evidência

- Resposta HTTP com `ok: true` em caso válido.
- Linha nova na aba `Tickets` contendo categoria, urgência, confiança e rota.
- Registro de fallback quando houver falha de IA (`error_api`).

## Evidências desta solução

As evidências visuais da execução desta solução estão em [../../docs/evidence/](../../docs/evidence/).



