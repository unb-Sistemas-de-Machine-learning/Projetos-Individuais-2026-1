# Solution A — Classificação Direta (Sem Contexto Externo)

## Descrição

Abordagem minimalista: o agente recebe **título e abstract** de um artigo, envia diretamente para a IA e retorna a classificação sem consultar nenhuma fonte externa adicional.

O pipeline consiste em uma única chamada ao modelo **Google Gemini**, que realiza ao mesmo tempo a extração de keywords, a geração do resumo e a emissão da recomendação de ação.

---

## Fluxo

```
[Usuário fornece título + abstract]
          │
          ▼
  [Agente → Google Gemini]
  Prompt: classifique este artigo
          │
          ▼
  [JSON com classificação]
          │
          ▼
  [Registro no Google Sheets]
```

## Tecnologias

| Componente | Tecnologia |
|---|---|
| IA | Google Gemini (gemini-2.0-flash) |
| Registro | Google Sheets |
| Orquestração | n8n |
| API externa | Nenhuma além da IA |

---

## Vantagens

- ✅ **Simplicidade máxima** — um único nó de IA no pipeline
- ✅ **Baixa latência** — sem chamadas a APIs externas de busca
- ✅ **Custo mínimo de tokens** — apenas o abstract é enviado
- ✅ **Fácil de depurar** — fluxo linear sem ramificações
- ✅ **Sem dependências externas** além da IA e do Sheets

## Desvantagens

- ❌ **Sem contexto externo** — a IA classifica apenas com o que está no abstract
- ❌ **Classificação menos precisa** em artigos com abstracts curtos ou ambíguos
- ❌ **Sem artigos relacionados** — o pesquisador não recebe sugestões de literatura complementar
- ❌ **Maior taxa de `neutro`** — sem contexto, o modelo tende a expressar menos certeza

---

## Quando usar

Esta solução é adequada quando:
- O pesquisador já tem o título e abstract em mãos (não precisa de busca)
- O volume de artigos é alto e a latência importa mais que a precisão
- A infraestrutura é limitada (sem acesso à Semantic Scholar API)

---

## Limitações desta abordagem

A ausência de contexto externo é a principal limitação. Um artigo com abstract de 2 linhas ou escrito de forma muito técnica pode resultar em `categoria = neutro` simplesmente pela falta de informação — não por falta de relevância.

**Score de confiança esperado:** entre 0.5 e 0.75 na maioria dos casos.  
**Taxa estimada de `revisao_humana`:** ~30% (acima da meta de 20%).
