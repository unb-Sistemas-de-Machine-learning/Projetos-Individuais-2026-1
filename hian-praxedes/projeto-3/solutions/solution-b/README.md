# Solution B — Validação com Base de Conhecimento

## Abordagem

A Solution B adiciona uma base de conhecimento simples para orientar a análise do agente.

Diferente da Solution A, que depende apenas de um prompt, esta solução usa uma base de checklist com os itens obrigatórios da entrega. O agente compara a descrição enviada pelo usuário com essa base e retorna um diagnóstico estruturado.

## Problema tratado

O problema tratado é a validação de entregas acadêmicas com base em critérios obrigatórios. O objetivo é reduzir o risco de a IA ignorar algum item importante, como workflow exportado, evidências, documentação ou testes.

## Base de conhecimento usada

A base de conhecimento fica no arquivo:

data/base-checklist-entrega.csv

Ela contém os principais itens esperados na entrega:

- README;
- agent.md;
- mission-brief.md;
- mentorship-pack.md;
- workflow-runbook.md;
- três soluções documentadas;
- workflow n8n exportado em JSON;
- prints ou evidências de funcionamento;
- Google Sheets ou outra forma de persistência;
- tratamento de erro;
- ADR;
- merge-readiness-pack;
- relatório técnico.

## Fluxo proposto

Webhook

Leitura da base de checklist

IA analisa descrição da entrega com apoio da base

Normalização da resposta em JSON

Switch por status ou ação recomendada

Google Sheets registra auditoria

Resposta ou notificação externa

## Entrada esperada

Exemplo de entrada:

{
  "aluno": "Hian Praxedes",
  "projeto": "Projeto Individual 3",
  "descricao_entrega": "Tenho README, agent.md, mission brief e o fluxo no n8n. Ainda falta exportar o workflow e colocar prints."
}

## Prompt usado

Você é um agente de validação de entregas acadêmicas.

Use a base de checklist abaixo como referência obrigatória para avaliar a entrega.

Compare a descrição enviada pelo usuário com os itens esperados.

Não marque um item como presente se ele não for citado explicitamente.

Retorne exclusivamente um JSON válido com os seguintes campos:

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

Regras:

- Não retorne texto fora do JSON.
- Não invente arquivos, commits, prints, testes ou evidências.
- Se a descrição não citar um item, considere-o ausente.
- Se faltarem workflow exportado, prints ou documentação obrigatória, a entrega não deve ser classificada como completa.
- Se a entrada for vaga, use status "invalida".
- Se houver incerteza, reduza a confiança.
- Se a confiança for menor que 0.70, recomende "revisao_humana".

## Exemplo de saída esperada

{
  "status": "incompleta",
  "percentual_prontidao": 65,
  "itens_identificados": [
    "README",
    "agent.md",
    "mission-brief.md",
    "fluxo n8n"
  ],
  "pendencias": [
    "workflow exportado em JSON",
    "prints de funcionamento",
    "merge-readiness-pack",
    "relatório técnico"
  ],
  "riscos": [
    "não comprovar funcionamento do fluxo",
    "entrega sem evidências suficientes"
  ],
  "acao_recomendada": "solicitar_correcoes",
  "confianca": 0.92,
  "justificativa": "A entrega possui documentação relevante e menciona o fluxo, mas ainda faltam evidências, exportação do workflow e documentação final."
}

## Decisão no n8n

O n8n usaria principalmente os campos "status", "acao_recomendada" e "confianca" para decidir a rota.

| Condição | Rota |
|---|---|
| status = completa e confianca >= 0.70 | registrar |
| status = incompleta | solicitar_correcoes |
| status = critica | notificar_responsavel |
| status = invalida | revisao_humana |
| confianca < 0.70 | revisao_humana |

## Pontos positivos

- É mais fiel aos critérios da entrega.
- Reduz o risco de esquecer itens obrigatórios.
- Melhora a explicabilidade da decisão.
- Ajuda o agente a manter consistência entre diferentes entradas.
- Facilita auditoria, pois os critérios estão documentados em uma base.

## Limitações

- Depende da qualidade da base de checklist.
- Ainda usa uma única etapa principal de IA.
- Pode exigir manutenção da base caso o enunciado mude.
- Não resolve totalmente o problema de JSON malformado.
- Ainda precisa de validação extra no n8n para casos de baixa confiança.

## Riscos

- A base pode ficar desatualizada.
- O agente pode interpretar incorretamente um item citado de forma vaga.
- A IA pode retornar um item como identificado mesmo sem evidência suficiente.
- A integração com a base adiciona uma etapa a mais no fluxo.

## Comparação com a Solution A

A Solution B é mais robusta que a Solution A porque adiciona critérios explícitos para orientar a IA.

Enquanto a Solution A depende apenas do prompt, a Solution B usa uma base de checklist para reduzir omissões e melhorar rastreabilidade.

Mesmo assim, ela ainda não é a solução final ideal porque não possui validação multi-etapas completa, fallback estruturado e tratamento robusto de erro.

## Motivo para não ser a solução final

A Solution B melhora a qualidade da análise, mas ainda concentra a decisão em uma única chamada de IA. Para atender melhor ao enunciado, a solução final precisa demonstrar validação de entrada, normalização da saída da IA, verificação de confiança, persistência, roteamento condicional e fallback.

Por isso, a Solution C será usada como solução final.