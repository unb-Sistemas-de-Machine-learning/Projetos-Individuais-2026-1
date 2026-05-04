# Workflow Runbook — Processo de Execução

## Objetivo

Este documento descreve o processo obrigatório de execução do projeto, desde a leitura do Mission Brief até a consolidação da solução final e abertura do Pull Request.

## Processo obrigatório

1. Ler o Mission Brief.
2. Definir o comportamento do agente no agent.md.
3. Criar o Mentorship Pack com padrões de qualidade.
4. Propor três soluções possíveis para o mesmo problema.
5. Registrar cada solução em uma pasta separada.
6. Implementar ou prototipar cada solução.
7. Executar testes com entradas completas, incompletas e inválidas.
8. Comparar custo, complexidade, qualidade, risco e manutenibilidade.
9. Escolher a solução final.
10. Registrar a decisão em ADR.
11. Gerar o Merge-Readiness Pack.
12. Fazer commits separados por etapa.
13. Exportar o workflow do n8n.
14. Adicionar evidências de funcionamento.
15. Abrir Pull Request para submissão.

## Execução da solução final

A solução final deve ser executada na seguinte ordem:

1. Enviar entrada para o Webhook do n8n.
2. Validar se a descrição da entrega possui conteúdo mínimo.
3. Enviar a descrição para o agente de IA.
4. Receber uma resposta estruturada em JSON.
5. Normalizar e validar a saída da IA.
6. Registrar o resultado no Google Sheets.
7. Decidir a rota com base em status, risco e confiança.
8. Enviar notificação quando necessário.
9. Retornar resposta ao usuário pelo Webhook.
10. Salvar evidências da execução.

## Fluxo esperado

Webhook
↓
Validação de entrada
↓
Agente de IA
↓
Normalização do JSON
↓
Google Sheets
↓
Switch de decisão
↓
Notificação externa
↓
Respond to Webhook

## Regras de decisão

| Condição | Rota |
|---|---|
| Entrada vazia ou insuficiente | revisao_humana |
| Confiança menor que 0.70 | revisao_humana |
| Status completa | registrar |
| Status incompleta | solicitar_correcoes |
| Status critica | notificar_responsavel |
| Status invalida | revisao_humana |

## Casos de teste mínimos

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Entrega completa | Usuário informa README, agent.md, documentação, workflow exportado, evidências, testes, ADR e PR | status completa |
| Entrega incompleta | Usuário informa README e fluxo, mas faltam prints e JSON exportado | status incompleta |
| Entrega crítica | Usuário informa que quase nada foi feito | status critica |
| Entrada inválida | Mensagem vazia ou genérica | status invalida |
| Baixa confiança | Informação ambígua ou insuficiente | ação revisao_humana |

## Evidências obrigatórias

As evidências devem ser salvas em docs/evidence/.

Sugestão de nomes:

- 01-webhook-configurado.png
- 02-prompt-ia.png
- 03-execucao-entrega-incompleta.png
- 04-google-sheets-registro.png
- 05-email-notificacao.png
- 06-execucao-entrada-invalida.png
- 07-workflow-completo.png
- 08-workflow-exportado-json.png

## Critérios para escolher a solução final

A solução escolhida deve ser a que melhor atende aos seguintes critérios:

- usa n8n como orquestrador;
- usa IA para decisão, não apenas resposta;
- possui lógica condicional;
- possui integração externa real;
- possui persistência e rastreabilidade;
- possui tratamento de erro;
- é demonstrável por prints ou vídeo;
- é documentada de forma clara.

## Ordem de commits

A sequência mínima de commits deve ser:

1. Cria mission brief inicial
2. Adiciona agent.md com regras de comportamento
3. Cria mentorship pack e workflow runbook
4. Implementa solution-a
5. Implementa solution-b
6. Implementa solution-c
7. Adiciona testes e evidências
8. Registra ADR com comparação das soluções
9. Adiciona merge-readiness pack
10. Consolida solução final

## Observações

Cada commit deve ter uma mensagem clara e uma racionalidade no corpo da mensagem.

O projeto deve demonstrar não apenas o agente funcionando, mas também o processo de construção auditável com IA.