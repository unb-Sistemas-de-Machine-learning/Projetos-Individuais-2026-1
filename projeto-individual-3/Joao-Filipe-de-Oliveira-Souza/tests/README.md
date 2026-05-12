# Testes do Projeto

Este diretorio documenta os testes funcionais manuais utilizados para validar o workflow.

## Escopo

- classificacao por categoria;
- roteamento por urgencia;
- comportamento em baixa confianca;
- persistencia no Data Table;
- envio de email por rota.

## Como executar

1. Importar e ativar o workflow no n8n.
2. Submeter os cenarios descritos em `casos-teste-triagem.csv`.
3. Registrar evidencias em `docs/evidence/evidence-log.md`.

## Resultado esperado

Todos os cenarios devem produzir uma rota de saida valida e registro persistido.
