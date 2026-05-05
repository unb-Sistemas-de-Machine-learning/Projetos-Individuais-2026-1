# Testes - Curadoria Automática de Artigos Científicos

## Casos de Teste

Abaixo estão os três curls de teste usados para validar os endpoints dos workflows. Esperado: todos os requests passam pelo fluxo e geram a notificação no Telegram com sucesso.

1) Solution C (fluxo completo com validação DOI)

```bash
curl -X POST http://localhost:5678/webhook-test/article-triage-full \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Array programming with NumPy",
    "abstract": "This paper discusses array programming and the role of NumPy in scientific computing.",
    "doi": "10.1038/s41586-020-2649-2",
    "keywords": ["numpy", "python", "scientific computing"]
  }'
```

2) Solution B (RAG)

```bash
curl -X POST http://localhost:5678/webhook-test/article-triage-rag \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chatbots in Customer Service",
    "abstract": "This study evaluates the impact of AI chatbots on customer experience, focusing on satisfaction, efficiency and consistency in digital environments.",
    "keywords": ["AI", "CX", "chatbots"]
  }'
```

3) Solution A (prompt simples)

```bash
curl -X POST http://localhost:5678/webhook-test/article-triage \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chatbots in Customer Service",
    "abstract": "This study evaluates the impact of AI chatbots on customer experience, focusing on satisfaction, efficiency and consistency in digital environments.",
    "keywords": ["AI", "CX", "chatbots"]
  }'
```

Resultado esperado: todos os três requests percorrem o fluxo correspondente e resultam em notificação de sucesso no Telegram.


### Artigo com Confiança Baixa (Solution C)
```json
{
  "title": "Study About Things",
  "abstract": "This paper discusses various topics in an unclear manner without focusing on a specific problem.",
  "keywords": ["general", "topics"],
  "doi": "10.invalid/format",
  "source": "unknown"
}
```


### Artigo Não Relevante (Solution A/B/C)
```json
{
  "title": "How to Bake a Cake",
  "abstract": "A step-by-step guide for baking chocolate cake at home.",
  "keywords": ["cooking", "recipes"],
  "source": "blog"
}
```