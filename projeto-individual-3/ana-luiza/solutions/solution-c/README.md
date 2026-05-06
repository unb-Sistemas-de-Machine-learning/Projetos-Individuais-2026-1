# Solution C — Pipeline Multi-Etapas com Validação entre Chamadas

## Descrição

Abordagem de **máxima robustez**: o pipeline encadeia **três chamadas de IA** com validação explícita do score de confiança entre cada etapa. Se uma etapa não atingir o limiar mínimo de confiança, o artigo é escalado para revisão humana antes de prosseguir — sem depender de uma única decisão do modelo.

O pipeline funciona como um processo de revisão em camadas, onde cada estágio pode interromper o fluxo se a certeza for insuficiente.

---

## Fluxo

```
[Usuário fornece objetivo de pesquisa]
          │
          ▼
[ETAPA 1 — Geração de Query]
  Agente 1 → Google Gemini
  Gera query + score de confiança na query
          │
          ▼
  confiança ≥ 0.7?
  ├─ NÃO → flag revisao_humana na query
  └─ SIM → continua
          │
          ▼
[ETAPA 2 — Extração e Enriquecimento]
  Semantic Scholar API → artigos relacionados
  Agente 2 → Google Gemini
  Extrai keywords + categoriza + gera score preliminar
          │
          ▼
  confiança ≥ 0.6?
  ├─ NÃO → artigo vai direto para revisao_humana
  └─ SIM → continua
          │
          ▼
[ETAPA 3 — Classificação Final e Validação]
  Agente 3 → Google Gemini
  Recebe output da Etapa 2 + instrução de validação
  Confirma ou revisa a categoria e o score
          │
          ▼
  Score final consolidado
          │
          ▼
  [Google Sheets + Telegram]
```

## Tecnologias

| Componente | Tecnologia |
|---|---|
| IA | Google Gemini (gemini-2.0-flash) — 3 chamadas por artigo |
| Busca | Semantic Scholar API |
| Registro | Google Sheets |
| Notificação | Telegram Bot |
| Orquestração | n8n com nós condicionais entre etapas |

---

## Vantagens

- ✅ **Mais robusta** — falhas de confiança são detectadas entre etapas, não só no final
- ✅ **Score de confiança mais preciso** — validação cruzada entre Agente 2 e Agente 3
- ✅ **Menor taxa de erro silencioso** — pipeline sinaliza ativamente onde a incerteza surgiu
- ✅ **Auditável por etapa** — cada chamada de IA tem seu próprio output rastreável no n8n

## Desvantagens

- ❌ **Maior latência** — 3 chamadas de IA por artigo vs. 1 nas outras soluções
- ❌ **Custo de tokens 3x maior** — cada artigo consome tokens em três etapas
- ❌ **Complexidade de manutenção** — 3 prompts para manter coerentes entre si
- ❌ **Risco de loop de revisão** — artigos que falham na Etapa 2 nunca chegam à Etapa 3
- ❌ **Difícil de testar isoladamente** — cada etapa depende da saída da anterior

---

## Quando usar

Esta solução é adequada quando:
- A **precisão é crítica** e erros de classificação têm consequências reais (ex: revisão sistemática formal)
- O custo de tokens e a latência são aceitáveis
- A equipe tem capacidade de manter três prompts de IA distintos e alinhados

---

## Comparação com outras soluções

| Critério | Solution A | Solution B | Solution C |
|---|---|---|---|
| Chamadas de IA por artigo | 1 | 2 | 3 |
| Contexto externo (RAG) | ❌ | ✅ | ✅ |
| Validação entre etapas | ❌ | ❌ | ✅ |
| Latência estimada | ~5s | ~12s | ~25s |
| Taxa esperada de `revisao_humana` | ~30% | ~15% | ~10% |
| Complexidade de manutenção | Baixa | Média | Alta |

---

## Limitações desta abordagem

O custo e a latência desta solução são aceitáveis apenas para volumes pequenos (< 20 artigos por execução). Para uso em escala, a Solução B oferece melhor equilíbrio entre qualidade e custo.
