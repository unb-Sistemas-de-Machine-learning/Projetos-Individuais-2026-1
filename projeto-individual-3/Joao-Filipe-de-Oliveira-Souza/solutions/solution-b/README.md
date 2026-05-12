# Solution B - Prompt + base de conhecimento

## Objetivo

Aprimorar a triagem com suporte de contexto semantico usando uma base de conhecimento com regras e politicas de atendimento para reduzir ambiguidades.

## Como funciona

1. Recebe os dados da demanda.
2. Busca trechos relevantes em uma base de conhecimento (FAQ/politicas).
3. Monta prompt com `contexto da demanda + contexto recuperado`.
4. A IA classifica e sugere acao com justificativa.
5. O fluxo persiste resultado e roteia por urgencia.

## Estrutura minima da base

Arquivo sugerido: `kb/politicas.md`

Exemplo de secoes:

- categorias e exemplos de palavras-chave
- regras de urgencia
- politicas de encaminhamento
- excecoes (casos sensiveis)

Base de conhecimento criada neste projeto:

- `kb/politicas.md`
- `prompt-template.md`

## Prompt sugerido

```text
Use a base de conhecimento abaixo para classificar a demanda.
Se houver conflito entre contexto e base, explique na justificativa.
Retorne APENAS JSON:
{
  "categoria": "...",
  "urgencia": "...",
  "confianca": 0.0,
  "resumo": "...",
  "acao_sugerida": "...",
  "justificativa": "..."
}
Base de conhecimento:
{{contexto_kb}}
Demanda:
Assunto: {{assunto}}
Descricao: {{descricao}}
```

## Fluxo minimo no n8n

```text
Formulario -> Buscar KB -> OpenAI Chat -> Parse JSON -> Persistir -> Switch (urgencia)
```

## Vantagens

- Melhor contextualizacao da classificacao.
- Reduz respostas genericas.
- Facil incorporar politica institucional.

## Desvantagens

- Aumenta custo e complexidade operacional.
- Exige manutencao da base.
- Risco de contexto desatualizado.

## Criterios de avaliacao da alternativa

- Ganho de precisao vs solution-a.
- Qualidade da justificativa.
- Esforco de manutencao da base.

## Status

Prototipo conceitual documentado para comparacao.

## Como demonstrar

1. Carregar `kb/politicas.md` em um no de contexto (Set, File ou Data Store).
2. Injetar `{{contexto_kb}}` no prompt de `prompt-template.md`.
3. Executar os casos T1, T2 e T4.
4. Comparar qualidade da justificativa com a solution-a.
