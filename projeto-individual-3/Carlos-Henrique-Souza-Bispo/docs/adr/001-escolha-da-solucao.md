# ADR-001: Escolha da solucao final para triagem academica

> **Data:** 25/04/2026
> **Status:** aceita

---

## Contexto

O projeto exige tres abordagens para o mesmo problema de triagem academica e uma decisao final justificada por comparacao tecnica. O sistema precisa equilibrar automacao, confiabilidade, rastreabilidade e facilidade de evolucao.

---

## Alternativas consideradas

### Alternativa A: Prompt simples com classificacao direta

- **Descricao:** unica etapa de classificacao com palavras-chave e regras basicas.
- **Pros:** implementacao rapida, baixo custo e baixa complexidade.
- **Contras:** maior risco de erro em textos ambiguos, pouca explicabilidade.

### Alternativa B: Classificacao com base de conhecimento (RAG simples)

- **Descricao:** recupera politica mais aderente e usa essa referencia para decisao.
- **Pros:** melhor contextualizacao, resposta mais consistente.
- **Contras:** depende da qualidade da base; manutencao da base aumenta custo.

### Alternativa C: Pipeline multi-etapas com validacao e fallback

- **Descricao:** classifica, extrai entidades, valida campos e define proximo passo por confianca.
- **Pros:** maior robustez, rastreabilidade e controle de risco operacional.
- **Contras:** implementacao mais extensa e ligeiro aumento de complexidade.

---

## Decisao

A alternativa escolhida foi a **Alternativa C**.

Motivos principais:

1. melhor qualidade de decisao em entradas incompletas
2. fallback explicito para baixa confianca
3. maior aderencia ao requisito de IA influenciando fluxo e nao apenas respondendo texto
4. melhor base para evolucao e auditoria no n8n

---

## Consequencias

- O projeto ganha robustez e seguranca no roteamento.
- O custo de implementacao inicial e maior que as alternativas A e B.
- A manutencao fica organizada por etapas (classificacao, validacao, decisao), facilitando evolucao.

---

## Referencias

- docs/mission-brief.md
- docs/workflow-runbook.md
- docs/merge-readiness-pack.md
- docs/evidence/comparacao-solucoes.md
