# Solution A — Validação com Prompt Simples

## Abordagem

A Solution A usa uma única chamada de IA para analisar a descrição da entrega acadêmica e retornar um diagnóstico estruturado em JSON.

Essa abordagem é a versão mais simples do agente. Ela não usa base de conhecimento externa nem validação avançada. O objetivo é testar rapidamente se a IA consegue classificar uma entrega acadêmica com base apenas em um prompt bem definido.

## Problema tratado

O problema tratado é a validação inicial de entregas acadêmicas. O usuário informa o que já foi feito na entrega, e a IA identifica se a entrega está completa, incompleta, crítica ou inválida.

## Fluxo proposto

Webhook

IA com prompt simples

Switch por status

Google Sheets

Resposta ao usuário

## Entrada esperada

Exemplo de entrada:

{
  "aluno": "Hian Praxedes",
  "projeto": "Projeto Individual 3",
  "descricao_entrega": "Fiz o README e o workflow no n8n, mas ainda não exportei o JSON nem tirei prints."
}

## Prompt usado

Você é um agente de validação de entregas acadêmicas.

Analise a descrição enviada pelo usuário e retorne exclusivamente um JSON válido com os seguintes campos:

{
  "status": "completa | incompleta | critica | invalida",
  "percentual_prontidao": 0,
  "itens_identificados": [],
  "pendencias": [],
  "riscos": [],
  "acao_recomendada": "registrar | solicitar_correcoes | notificar_responsavel | revisao_humana",
  "confianca": 0.0,
  "justificativa": ""
}

Critérios:

- Se faltarem evidências, workflow exportado ou documentação obrigatória, a entrega não deve ser considerada completa.
- Se a entrada for vaga, use status "invalida".
- Se houver incerteza, reduza a confiança.
- Não invente arquivos, commits, prints, testes ou evidências.
- Se a confiança for menor que 0.70, recomende revisão humana.

## Saída esperada

Exemplo de saída esperada:

{
  "status": "incompleta",
  "percentual_prontidao": 55,
  "itens_identificados": [
    "README",
    "workflow n8n"
  ],
  "pendencias": [
    "Exportar workflow do n8n em JSON",
    "Adicionar prints de funcionamento",
    "Documentar testes executados"
  ],
  "riscos": [
    "Ausência de evidências obrigatórias",
    "Impossibilidade de comprovar funcionamento do fluxo"
  ],
  "acao_recomendada": "solicitar_correcoes",
  "confianca": 0.91,
  "justificativa": "A entrega possui parte da documentação e menciona o fluxo, mas ainda faltam exportação do workflow, evidências e testes."
}

## Decisão no n8n

O n8n usaria o campo "status" para escolher a rota principal:

| Status | Rota |
|---|---|
| completa | registrar |
| incompleta | solicitar_correcoes |
| critica | notificar_responsavel |
| invalida | revisao_humana |

Também poderia usar o campo "confianca" para encaminhar casos incertos para revisão humana.

## Pontos positivos

- É simples de implementar.
- Tem baixo custo.
- É fácil de demonstrar.
- Exige poucos nós no n8n.
- Permite validar rapidamente o comportamento inicial do agente.

## Limitações

- Não usa base de conhecimento externa.
- Depende muito da qualidade do prompt.
- Pode deixar passar critérios obrigatórios se a descrição for ambígua.
- Possui menor rastreabilidade sobre os critérios usados.
- Não possui validação robusta da saída da IA.

## Riscos

- A IA pode aprovar uma entrega incompleta se o texto do usuário for vago.
- A IA pode retornar JSON malformado.
- A IA pode ignorar algum critério obrigatório.
- A decisão fica concentrada em uma única chamada de IA.

## Motivo para não ser a solução final

Apesar de funcional, a Solution A não foi escolhida como solução final porque é simples demais para os critérios do projeto. Ela atende parcialmente ao uso de IA e ao roteamento, mas não demonstra tão bem tratamento de erro, rastreabilidade e validação multi-etapas.

A solução final escolhida será mais robusta, com validação de entrada, normalização da saída da IA, verificação de confiança, persistência e fallback.