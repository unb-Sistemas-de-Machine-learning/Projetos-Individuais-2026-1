# Mission Brief — Agente de Validação de Entrega Acadêmica

## Objetivo do agente

Projetar um agente de IA integrado a um fluxo n8n capaz de validar o status de uma entrega acadêmica, identificar pendências, avaliar risco e recomendar a próxima ação.

## Problema que ele resolve

Em entregas acadêmicas com muitos artefatos obrigatórios, é comum que estudantes esqueçam arquivos, evidências, documentação, testes, commits ou instruções de execução. O agente ajuda a revisar a entrega antes da submissão final.

## Usuários-alvo

- Estudantes que precisam validar uma entrega acadêmica.
- Professores, monitores ou avaliadores que desejam uma triagem inicial.
- Equipes de projeto que precisam conferir artefatos antes de abrir um Pull Request.

## Contexto de uso

O usuário envia uma descrição da entrega, informando o que já foi feito e, opcionalmente, o link do repositório. O agente analisa a descrição com base em critérios obrigatórios e retorna um diagnóstico estruturado.

## Entradas esperadas

- Nome do aluno.
- Nome do projeto.
- Descrição da entrega.
- Link do repositório, se houver.
- Lista textual de artefatos já produzidos.

## Saídas esperadas

O agente deve retornar exclusivamente um JSON contendo:

- status da entrega;
- percentual de prontidão;
- itens identificados;
- pendências;
- riscos;
- ação recomendada;
- nível de confiança;
- justificativa.

## Limites do agente

O agente não deve afirmar que uma entrega está completa se não houver evidências suficientes. Ele também não deve inventar arquivos, prints, commits, testes ou workflows que não foram mencionados pelo usuário.

## O que o agente não deve fazer

- Não deve garantir nota.
- Não deve substituir a avaliação humana.
- Não deve inventar evidências.
- Não deve aprovar entregas com informações insuficientes.
- Não deve retornar texto fora do formato JSON esperado.

## Critérios de aceitação

A missão será considerada concluída se:

- o fluxo n8n receber uma entrada via Webhook;
- o agente de IA classificar a entrega;
- o fluxo tomar decisões com IF ou Switch;
- as decisões forem registradas em Google Sheets;
- houver ao menos uma notificação externa;
- entradas inválidas forem tratadas;
- casos de baixa confiança forem encaminhados para revisão humana;
- existirem evidências de funcionamento;
- o workflow for exportado em JSON.

## Riscos

- A IA pode classificar uma entrega incompleta como completa.
- A descrição enviada pelo usuário pode ser vaga.
- O JSON retornado pela IA pode vir malformado.
- O serviço externo de IA pode falhar.
- A automação pode registrar dados incorretos se não houver validação.

## Evidências necessárias

- Print do workflow no n8n.
- Print da entrada enviada ao Webhook.
- Print da resposta da IA.
- Print do IF/Switch tomando decisão.
- Print do registro no Google Sheets.
- Print da notificação enviada.
- Print ou log de caso com baixa confiança.
- Workflow exportado em JSON.