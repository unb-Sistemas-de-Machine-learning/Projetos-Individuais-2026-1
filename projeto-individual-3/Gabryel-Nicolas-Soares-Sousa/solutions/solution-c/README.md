# Solution-C — Fluxo Multi-etapas com Validação

**Abordagem:** Fluxo em cadeia com validação explícita do JSON retornado pela IA e retry automático quando `confianca` for `"baixa"`. Inclui todos os elementos da solution-b.

## Fluxo

```
Webhook → Validar entrada → OpenAI (classificar) → Validar JSON →
  ├── JSON inválido → Retry (até 2x) → Fallback se persistir
  └── JSON válido → Switch (urgência + confiança) →
        ├── Alta urgência + confiança alta → Email + Sheets
        ├── Baixa urgência → FAQ → Resposta + Sheets
        └── Confiança baixa → Fila revisão manual + Sheets
```

## Vantagens
- Mais robusto: valida o output da IA antes de usar
- Retry reduz falsos fallbacks por resposta malformada
- Melhor rastreabilidade por etapa

## Desvantagens
- Mais nós no fluxo (mais difícil de manter)
- Maior custo de tokens (retry = chamadas extras)
- Complexidade desnecessária para volume baixo

## Adequação
Ideal para produção em alto volume. **Descartada por complexidade excessiva para o escopo.**
