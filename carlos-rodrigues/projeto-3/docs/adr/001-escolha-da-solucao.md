# ADR-001: Escolha da solução para curadoria automática de artigos científicos

> **Data:** 03/05/2026
> **Status:** aceita

---

## Contexto

O projeto precisa automatizar a triagem de artigos científicos com uso de IA, garantindo classificação útil, extração de metadados e rastreabilidade das decisões. Como o domínio envolve conteúdo técnico e possíveis ambiguidades bibliográficas, a solução precisa lidar bem com incerteza e revisão humana.

---

## Alternativas consideradas

### Alternativa A: Prompt simples

- **Descrição:** um único passo de IA classifica o artigo e produz um resumo estruturado.
- **Prós:** baixa complexidade, rápida de implementar, fácil de demonstrar.
- **Contras:** menor robustez, pouca validação e maior risco de erro em casos ambíguos.

### Alternativa B: RAG / base de conhecimento

- **Descrição:** a IA consulta uma base com critérios de curadoria, tópicos prioritários e histórico de decisões.
- **Prós:** melhor contexto, maior consistência, facilita padronização.
- **Contras:** depende da qualidade e manutenção da base, maior esforço de integração.

### Alternativa C: Fluxo multi-etapas com validação

- **Descrição:** o artigo passa por normalização, classificação, validação de metadados, cálculo de confiança e escalonamento humano quando necessário.
- **Prós:** mais rastreável, mais seguro, melhor aderência ao problema.
- **Contras:** implementação mais longa e com mais nós no fluxo.

---

## Decisão

A alternativa escolhida é a **Alternativa C**.

Ela oferece o melhor equilíbrio entre qualidade da curadoria, controle de incerteza e auditabilidade. Para artigos científicos, não basta classificar bem em média; a solução também precisa manter consistência nas validações e no registro das decisões.

---

## Consequências

- O fluxo terá mais etapas, mas também maior confiabilidade.
- Haverá dependência explícita de revisão humana para casos de baixa confiança.
- As decisões ficarão mais fáceis de auditar em evidências e logs.

---

## Referências

1. Requisitos do projeto individual 3.
2. Documentação oficial do N8N: https://docs.n8n.io/

