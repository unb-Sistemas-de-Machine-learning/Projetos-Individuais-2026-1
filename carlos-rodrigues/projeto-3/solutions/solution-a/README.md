# Solution A - Prompt simples

Abordagem mínima para curadoria automática de artigos científicos.

## Ideia

Usar um único passo de IA para ler título e resumo, classificar relevância e devolver uma saída estruturada com prioridade e justificativa curta.

## Fluxo

1. Receber artigo.
2. Enviar para o modelo com instruções de classificação.
3. Receber JSON com `classification`, `confidence` e `summary`.
4. Se a confiança for alta, notificar aprovação; se for baixa, notificar para revisão humana via Telegram.

## Vantagens

- Fácil de implementar.
- Bom para demonstração inicial.
- Baixo custo de execução.

## Limitações

- Depende fortemente da qualidade do prompt.
- Não valida metadados externos.
- Menos confiável para artigos ambíguos ou de fronteira.
