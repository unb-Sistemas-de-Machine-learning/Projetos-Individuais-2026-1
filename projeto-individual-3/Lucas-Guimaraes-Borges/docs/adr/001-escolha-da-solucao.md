# ADR-001: Escolha da solução final de triagem

> **Data:** 05/05/2026  
> **Status:** aceita

## Contexto

Era necessário escolher uma abordagem de triagem de e-mails que fosse executável, rastreável e segura para operação real.

## Alternativas consideradas

### Alternativa A: Prompt/regras simples

- **Pros:** baixa complexidade e manutenção rápida.
- **Contras:** menor robustez para ambiguidades.

### Alternativa B: Base de conhecimento local

- **Pros:** melhora consistência por políticas mapeadas.
- **Contras:** exige curadoria contínua da KB.

### Alternativa C: Pipeline multi-etapas com validação

- **Pros:** melhor controle de confiança, fallback claro, maior auditabilidade.
- **Contras:** implementação mais extensa.

## Decisao

Escolher a **Alternativa C** como base final da entrega.

## Consequencias

- Melhor qualidade operacional em casos críticos.
- Maior segurança para evitar roteamento incorreto.
- Aumento moderado do custo de manutenção.

## Referencias

- `docs/evidence/comparacao-solucoes.md`
- `docs/merge-readiness-pack.md`

