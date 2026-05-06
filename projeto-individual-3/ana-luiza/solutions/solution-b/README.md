# Solution B — Pipeline de Curadoria com Gemini 2.5 Flash + Semantic Scholar

## Descrição

Implementação de um pipeline de dois agentes no **n8n** para curadoria automatizada de artigos científicos. O usuário fornece um objetivo em linguagem natural; o pipeline gera uma query booleana em inglês, busca artigos na Semantic Scholar Bulk Search API, filtra resultados sem abstract, classifica cada artigo via LLM e grava os resultados no Google Sheets (abas **Registros** e **Alertas**).

---

## Fluxo Implementado

```
[Manual Trigger]
       │
       ▼
[Edit Fields]
 Define objetivo_pesquisa
       │
       ▼
[Agente 1 — Google Gemini 2.5 Flash]
 Converte objetivo em português
 → query booleana em inglês
 ex: ("smartphone" OR "mobile phone") +school
       │
       ▼
[HTTP Request — Semantic Scholar Bulk Search API]
 GET graph/v1/paper/search/bulk
 ?query=<query_gerada>
 &fields=title,abstract,year,citationCount
 &limit=5
       │
       ▼
[Split Out]  →  [Filter: remove abstract=null]  →  [Limit: máx 5]
       │
       ▼
[Agente 2 — Google Gemini 2.5 Flash]
 Classifica artigo → JSON: titulo, ano,
 relevancia, resumo_pt, decisao
       │
       ▼
[Code in JavaScript]
 JSON.parse da resposta do Agente 2
       │
       ▼
[IF — confianca >= 0.6?]
       │
       ▼
[Switch — decisao: arquivar | revisar | descartar]
       │
       ▼
[Google Sheets — aba Registros]  (todos os artigos)
       │
       Se decisao=revisar OU relevancia>=0.8:
       ▼
[Google Sheets — aba Alertas]
 status = aguardando_revisao
```

---

## Tecnologias

| Componente | Tecnologia |
|---|---|
| IA | Google Gemini 2.5 Flash (`models/gemini-2.5-flash`) |
| Busca | Semantic Scholar Bulk Search API (gratuita) |
| Registro | Google Sheets — aba **Registros** |
| Alertas | Google Sheets — aba **Alertas** |
| Orquestração | n8n |
| Credenciais | Google PaLM API (Gemini) + Google Sheets OAuth2 |

---

## Decisões de Design

| Decisão | Alternativa descartada | Motivo |
|---|---|---|
| Endpoint `/bulk` da Semantic Scholar | Endpoint `/search` padrão | O endpoint padrão sofre rate limit severo sem chave API |
| `limit=5` por execução | `limit=10` | Rate limit da API gratuita impede volumes maiores de forma confiável |
| Nó **Filter** antes do Agente 2 | Deixar o LLM tratar abstract nulo | Evita desperdício de tokens e respostas inconsistentes |
| Nó **Split Out** separando itens individualmente | Agente 2 receber array inteiro | Rastreabilidade individual por artigo no histórico do n8n |
| **Gemini 2.5 Flash** | Gemini 2.0 Flash | Gemini 2.0 Flash foi depreciado durante o desenvolvimento |
| Credencial **Google PaLM API** no n8n | API key direta | Exigência do nó `@n8n/n8n-nodes-langchain.googleGemini` |

---

## Limitações Encontradas e Soluções

| Limitação | Causa | Solução Aplicada |
|---|---|---|
| Artigos com `abstract = null` quebravam o Agente 2 | Semantic Scholar retorna abstract nulo para alguns artigos | Nó **Filter** elimina esses artigos antes da classificação |
| Rate limit sem chave API | API pública tem cota baixa no endpoint `/search` | Migração para `/bulk` + `limit=5` |
| Gemini 2.0 Flash depreciado | Google encerrou suporte ao modelo durante o desenvolvimento | Migração para `models/gemini-2.5-flash` |
| Resposta do Agente 2 com markdown | LLM pode incluir ` ```json ` na resposta | Nó **Code** com `JSON.parse` e strip de backticks antes do parse |

---

## Vantagens

- ✅ Pipeline rastreável — cada artigo passa por nós individuais com log visual no n8n
- ✅ Filtro preventivo — artigos sem abstract removidos antes de consumir tokens
- ✅ Duas abas no Sheets — separação entre todos os registros e os prioritários
- ✅ Sem dependência de chave API paga — funciona com Semantic Scholar gratuita

## Desvantagens

- ❌ Volume limitado — máximo de 5 artigos por execução pelo rate limit
- ❌ Latência por chamada sequencial ao LLM por artigo
- ❌ Dependência externa — falha na Semantic Scholar interrompe o pipeline
- ❌ Sem memória — cada execução é independente

---

## Resultado Esperado

**Artigos processados por execução:** até 5 (após filtro de abstract nulo)  
**Campos gravados (aba Registros):** `titulo`, `ano`, `relevancia`, `resumo_pt`, `decisao`  
**Campos gravados (aba Alertas):** `timestamp`, `titulo`, `relevancia`, `resumo_pt`, `justificativa`, `status`  
**Arquivo de workflow:** `src/workflow-solution-b.json`
