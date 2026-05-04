# Projeto Individual 3 — Agente de Validação de Entrega Acadêmica

## Identificação

- Aluno: Hian Praxedes de Souza Oliveira - 200019520
- Projeto: Projeto Individual 3 — Automação Inteligente de Processos com n8n e Agentes de IA
- Tema: Agente de Validação de Entrega Acadêmica

## Descrição

Este projeto implementa uma automação no n8n com uso de IA para validar entregas acadêmicas.

O fluxo recebe uma descrição da entrega, utiliza Gemini para classificar o status, identifica pendências, avalia riscos e registra o resultado em Google Sheets.

## Problema abordado

Entregas acadêmicas costumam exigir diversos artefatos obrigatórios, como documentação, workflow exportado, prints, testes e evidências. O agente reduz o risco de submissão incompleta ao realizar uma validação inicial automatizada.

## Solução final

A solução final utiliza um fluxo simplificado no n8n:

Webhook

Validar entrada

Entrada válida?

Se não:
Montar resultado inválido
Registrar auditoria

Se sim:
IA - Validar entrega
Normalizar IA
Precisa de correção?

Se sim:
Montar resultado pendente
Registrar auditoria

Se não:
Montar resultado ok
Registrar auditoria

## Tecnologias utilizadas

- n8n
- Gemini
- Google Sheets
- Webhook
- Markdown
- Git e GitHub

## Integrações

A integração externa usada foi o Google Sheets.

A planilha registra:

- data e hora;
- aluno;
- projeto;
- descrição da entrega;
- status;
- percentual de prontidão;
- itens identificados;
- pendências;
- riscos;
- ação recomendada;
- confiança;
- justificativa;
- rota executada.

## Estrutura do projeto

projeto-4/
├── agent.md
├── README.md
├── relatorio-entrega.md
├── data/
├── docs/
├── solutions/
├── src/
├── tests/
└── workflows/

## Como executar

1. Importar o workflow em workflows/agente-validacao-entrega-academica.json.
2. Configurar a credencial do Gemini no n8n.
3. Configurar a credencial do Google Sheets no n8n.
4. Criar ou importar a planilha de auditoria.
5. Executar o Webhook com os casos de teste.
6. Conferir os registros gerados no Google Sheets.

## Casos de teste

Os casos de teste estão documentados em:

tests/casos-de-teste.md

## Evidências

As evidências estão em:

docs/evidence/

## Decisão arquitetural

A decisão pela Solution C está registrada em:

docs/adr/001-escolha-da-solucao.md

## Resultado

O projeto demonstra uma automação com IA capaz de classificar entregas acadêmicas, tomar decisões condicionais no n8n e registrar os resultados para auditoria.