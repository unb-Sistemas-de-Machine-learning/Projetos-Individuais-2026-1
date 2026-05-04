# Merge-Readiness Pack — Agente de Validação de Entrega Acadêmica

## Resumo da solução escolhida

A solução final escolhida foi a Solution C, baseada em um fluxo multi-etapas simplificado no n8n.

O fluxo recebe uma descrição de entrega acadêmica via Webhook, valida a entrada, chama um agente de IA com Gemini, normaliza a resposta, decide o caminho com IF e registra o resultado no Google Sheets.

## Fluxo final

Webhook

Validar entrada

Entrada válida?

Se não:
Montar resultado inválido
Registrar auditoria no Google Sheets

Se sim:
IA - Validar entrega
Normalizar IA
Precisa de correção?

Se sim:
Montar resultado pendente
Registrar auditoria no Google Sheets

Se não:
Montar resultado ok
Registrar auditoria no Google Sheets

## Comparação entre alternativas

| Critério | Solution A | Solution B | Solution C |
|---|---|---|---|
| Abordagem | Prompt simples | Checklist/base de conhecimento | Multi-etapas simplificado |
| Complexidade | Baixa | Média | Média |
| Qualidade da decisão | Média | Boa | Alta |
| Tratamento de erro | Baixo | Médio | Alto |
| Rastreabilidade | Baixa | Média | Alta |
| Solução final | Não | Não | Sim |

## Testes executados

### Teste 1 — Entrega incompleta

Entrada usada:

Aluno informa que fez README e workflow no n8n, mas ainda não exportou o JSON nem tirou prints.

Resultado esperado:

- entrada válida;
- IA classifica como incompleta;
- fluxo identifica necessidade de correção;
- resultado é registrado no Google Sheets.

### Teste 2 — Entrada inválida

Entrada usada:

Descrição vazia.

Resultado esperado:

- entrada inválida;
- fluxo não chama a IA;
- resultado é registrado no Google Sheets;
- rota indica revisão humana.

### Teste 3 — Entrega completa

Entrada usada:

Aluno informa que concluiu README, agent.md, mission brief, mentorship pack, workflow runbook, três soluções, workflow exportado, prints, Google Sheets, tratamento de erro, ADR, relatório técnico, merge-readiness-pack, commits e PR.

Resultado esperado:

- entrada válida;
- IA classifica como completa;
- fluxo identifica ausência de pendências críticas;
- resultado é registrado no Google Sheets.

## Evidências de funcionamento

As evidências estão na pasta:

docs/evidence/

E incluem:

- print do workflow completo;
- print do Webhook;
- print da validação de entrada;
- print do IF de entrada válida;
- print do nó de IA;
- print da normalização da IA;
- print do IF de necessidade de correção;
- print do Google Sheets com registros;
- prints dos testes executados.

## Limitações conhecidas

- A solução depende da qualidade da descrição enviada pelo usuário.
- A IA pode classificar incorretamente uma entrega ambígua.
- O resultado não substitui avaliação humana final.
- O fluxo depende das credenciais do Gemini e do Google Sheets.
- A solução não envia notificações externas por e-mail ou Telegram.

## Riscos

- Erro de classificação da IA.
- Resposta da IA fora do formato JSON.
- Falha de integração com Google Sheets.
- Usuário omitir informações importantes.
- Checklist incompleto ou desatualizado.

## Decisões arquiteturais

- Usar n8n como orquestrador.
- Usar Gemini como componente de IA.
- Usar Webhook como entrada.
- Usar IF para lógica condicional.
- Usar Google Sheets como integração externa e persistência.
- Simplificar o fluxo removendo e-mail, Telegram, Switch complexo e Respond to Webhook.

## Instruções de execução

1. Importar o workflow localizado em workflows/agente-validacao-entrega-academica.json.
2. Configurar credencial do Gemini.
3. Configurar credencial do Google Sheets.
4. Garantir que a planilha de auditoria possui as colunas esperadas.
5. Executar os casos de teste documentados em tests/casos-de-teste.md.
6. Conferir os registros gerados no Google Sheets.

## Checklist de revisão

- [x] Mission Brief criado.
- [x] agent.md criado.
- [x] Mentorship Pack criado.
- [x] Workflow Runbook criado.
- [x] Solution A documentada.
- [x] Solution B documentada.
- [x] Solution C documentada.
- [x] ADR criada.
- [x] Workflow n8n implementado.
- [x] Workflow n8n exportado.
- [x] Google Sheets usado como persistência.
- [x] Testes documentados.
- [x] Evidências adicionadas.
- [x] Merge-Readiness Pack criado.

## Justificativa para merge

A solução está pronta para revisão porque implementa uma automação funcional com n8n e IA, usa lógica condicional para tomada de decisão, registra os resultados em Google Sheets, trata entrada inválida e apresenta evidências de funcionamento.