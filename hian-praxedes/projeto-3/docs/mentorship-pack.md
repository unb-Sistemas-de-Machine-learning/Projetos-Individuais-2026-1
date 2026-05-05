# Mentorship Pack — Diretrizes para Construção do Agente

## Objetivo

Este documento orienta como o agente deve apoiar a construção, validação e documentação do projeto. Ele define critérios de julgamento, padrões de arquitetura, padrões de qualidade e exemplos de respostas adequadas e inadequadas.

## Princípios de julgamento

O agente deve priorizar:

- clareza;
- rastreabilidade;
- simplicidade;
- segurança na decisão;
- evidências verificáveis;
- tratamento explícito de incerteza.

Sempre que houver dúvida, o agente deve preferir classificar a entrega como incompleta ou encaminhar para revisão humana.

## Padrões de arquitetura

A solução deve seguir estes princípios:

- o n8n deve ser o orquestrador principal;
- a IA deve influenciar diretamente a decisão do fluxo;
- a saída da IA deve ser estruturada em JSON;
- o fluxo deve possuir tratamento de erro;
- o fluxo deve possuir pelo menos uma integração externa real;
- as decisões devem ser persistidas em Google Sheets;
- a solução final deve ser demonstrável por prints ou vídeo;
- as decisões arquiteturais devem ser registradas em ADR.

## Padrões de código e configuração

O projeto deve buscar:

- nomes claros para nós do n8n;
- prompts objetivos;
- validação de entrada antes da chamada de IA;
- normalização da resposta da IA;
- fallback para erro de JSON;
- fallback para baixa confiança;
- separação entre documentação, testes, evidências e workflow exportado.

## Padrões de documentação

A documentação deve explicar:

- problema escolhido;
- papel do agente;
- desenho do fluxo;
- decisões de arquitetura;
- limitações;
- riscos;
- instruções de execução;
- evidências de funcionamento.

Cada solução deve registrar sua abordagem, vantagens, limitações e motivo de descarte ou escolha.

## Qualidade esperada

Uma boa resposta do agente:

- identifica pendências específicas;
- justifica o risco;
- recomenda uma ação clara;
- retorna JSON válido;
- não inventa evidências;
- diferencia entrega incompleta de entrega crítica;
- encaminha para revisão humana quando a confiança é baixa.

Uma má resposta do agente:

- aprova entrega sem evidências;
- retorna texto fora do JSON;
- ignora baixa confiança;
- não diferencia pendências críticas de pendências simples;
- inventa arquivos, commits, prints ou workflows;
- dá uma resposta genérica sem ação recomendada.

## Exemplo de boa resposta

{
  "status": "incompleta",
  "percentual_prontidao": 65,
  "itens_identificados": [
    "README",
    "workflow n8n"
  ],
  "pendencias": [
    "workflow exportado em JSON",
    "prints de funcionamento",
    "merge-readiness-pack"
  ],
  "riscos": [
    "ausência de evidências obrigatórias"
  ],
  "acao_recomendada": "solicitar_correcoes",
  "confianca": 0.91,
  "justificativa": "A entrega possui parte da documentação e menciona o fluxo, mas ainda faltam evidências, exportação do workflow e documentação final."
}

## Exemplo de má resposta

Sua entrega parece boa, só falta ajustar algumas coisas.

Essa resposta é inadequada porque:

- não está em JSON;
- não informa pendências específicas;
- não indica confiança;
- não permite roteamento automatizado no n8n;
- não gera rastreabilidade suficiente.

## Orientações de julgamento

O agente deve considerar uma entrega completa somente quando a descrição citar evidências suficientes dos artefatos obrigatórios.

Se o aluno disser apenas que "está tudo pronto", o agente deve considerar a entrada insuficiente, pois não há comprovação dos itens.

Se faltarem prints, workflow exportado ou documentação obrigatória, a entrega não deve ser classificada como completa.

## Orientações para alternativas descartáveis

As três soluções devem ser comparadas com base em:

- custo;
- complexidade;
- qualidade da resposta;
- riscos;
- manutenibilidade;
- adequação ao problema.

A solução escolhida deve ser justificada no ADR.

## Orientações sobre incerteza

O agente não deve esconder incertezas. Quando houver pouca informação, deve reduzir a confiança e recomendar revisão humana.

## Orientações sobre evidências

As evidências devem comprovar:

- entrada recebida;
- IA classificando;
- decisão do IF ou Switch;
- registro no Google Sheets;
- notificação externa;
- tratamento de entrada inválida;
- workflow exportado.