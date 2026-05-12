# Solution A - Prompt unico

## Objetivo

Implementar a triagem de demandas com uma abordagem minima baseada em um unico prompt de classificacao, sem base de conhecimento externa e com poucas regras de pos-processamento.

## Como funciona

1. Recebe `nome`, `email`, `assunto` e `descricao`.
2. Envia tudo para um modelo de IA com um prompt unico.
3. A IA retorna JSON com `categoria`, `urgencia`, `confianca`, `resumo` e `acao_sugerida`.
4. O fluxo encaminha por urgencia com base direta na resposta.

## Prompt sugerido

```text
Voce e um assistente de triagem. Classifique a demanda em: suporte_tecnico, financeiro, comercial ou outro.
Tambem classifique urgencia em: baixa, media, alta.
Retorne APENAS JSON no formato:
{
  "categoria": "...",
  "urgencia": "...",
  "confianca": 0.0,
  "resumo": "...",
  "acao_sugerida": "..."
}
Contexto:
Assunto: {{assunto}}
Descricao: {{descricao}}
Solicitante: {{nome}} ({{email}})
```

## Fluxo minimo no n8n

```text
Formulario -> OpenAI Chat -> Parse JSON -> Switch (urgencia) -> Email/registro
```

## Artefatos desta solucao

- `prompt-template.md`: prompt base para classificacao unica.

## Vantagens

- Implementacao rapida.
- Baixo custo inicial.
- Facil de explicar.

## Desvantagens

- Menor previsibilidade em casos ambiguos.
- Maior variacao de resposta conforme prompt.
- Menos robusta para auditoria e fallback.

## Criterios de avaliacao da alternativa

- Taxa de classificacao valida em 10 casos manuais.
- Consistencia de urgencia em casos semelhantes.
- Tempo medio de resposta por execucao.

## Status

Prototipo conceitual documentado para comparacao.

## Como demonstrar

1. Configurar no n8n um fluxo minimo com os nos descritos.
2. Aplicar o prompt de `prompt-template.md`.
3. Executar os casos T1 a T3 de `tests/casos-teste-triagem.csv`.
4. Registrar observacoes no log de evidencias.
