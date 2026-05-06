# Solution B — Classificação com RAG via Semantic Scholar

## Descrição

Abordagem com **Retrieval-Augmented Generation (RAG)**: antes de classificar, o agente busca até **5 artigos relacionados** na Semantic Scholar API e os inclui como contexto no prompt. A IA decide com mais informação — não apenas sobre o artigo em si, mas sobre o espaço de literatura ao redor dele.

O pipeline usa **dois agentes** em sequência: o primeiro gera a query de busca; o segundo classifica com base no abstract original + os abstracts dos artigos relacionados encontrados.

---

## Fluxo

```
[Usuário fornece objetivo de pesquisa]
          │
          ▼
  [Agente 1 → Google Gemini]
  Gera query técnica em inglês
          │
          ▼
  [Semantic Scholar API]
  Retorna até 10 artigos
          │
          ▼
  [Para cada artigo:]
  [Agente 2 → Google Gemini]
  Recebe abstract + 5 artigos relacionados como contexto
          │
          ▼
  [JSON com classificação enriquecida]
          │
          ▼
  [Google Sheets — aba Registros (todos os artigos)]
  [Google Sheets — aba Alertas (acao=revisar ou score>=0.8)]
```

## Tecnologias

| Componente | Tecnologia |
|---|---|
| IA | Google Gemini (gemini-2.0-flash) |
| Busca | Semantic Scholar API |
| Registro | Google Sheets (aba **Registros**) |
| Alertas | Google Sheets (aba **Alertas**) |
| Orquestração | n8n |

---

## Vantagens

- ✅ **Melhor qualidade de classificação** — a IA decide com contexto de literatura real
- ✅ **Menor taxa de `neutro`** — contexto reduz ambiguidade em abstracts curtos
- ✅ **Artigos relacionados como subproduto** — o pesquisador recebe sugestões de leitura
- ✅ **Score de confiança mais calibrado** — o modelo tem mais base para estimar certeza
- ✅ **Rastreabilidade completa** via n8n (histórico visual de execução)

## Desvantagens

- ❌ **Dependência da Semantic Scholar API** — falha externa impacta o pipeline
- ❌ **Maior latência** — chamada à API de busca antes de cada classificação
- ❌ **Maior consumo de tokens** — contexto de 5 artigos aumenta o tamanho do prompt
- ❌ **Rate limit** — uso intenso pode atingir limites da API gratuita

---

## Quando usar

Esta é a **solução recomendada** para o caso de uso principal:
- Pesquisadores que querem descobrir artigos relevantes a partir de um objetivo
- Contextos em que a qualidade da classificação supera a preocupação com latência
- Uso com acesso estável à internet e à Semantic Scholar API

---

## Resultado esperado

**Score de confiança médio:** entre 0.70 e 0.90  
**Taxa estimada de `revisao_humana`:** ~15% (dentro da meta de < 20%)  
**Artigos relacionados retornados por execução:** 5 a 10
