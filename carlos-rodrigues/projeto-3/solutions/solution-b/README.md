# Solution B - Curadoria com base local de conhecimento

Abordagem intermediária que mantém o objetivo de trazer contexto ao modelo, mas evita dependências externas de vetores/serviços. Em vez disso, usamos uma base de conhecimento local simples e um retriever local para fornecer contexto ao modelo. A notificação final é feita via Telegram Bot em tempo real.

## Ideia

Fornecer contexto recuperado de um acervo local (JSON) usando um retriever simples. Esse contexto é concatenado ao prompt antes de enviar ao modelo. Não requer serviços de embedding externos nem base vetorial.

## Fluxo atualizado

1. Receber artigo.
2. Normalizar entrada.
3. Chamar o retriever local (`src/solution-b-retriever.js`) para obter contextos relevantes a partir de `knowledge.json`.
4. Enviar contexto + artigo ao nó de IA para classificação/extracao.
5. Parsear resposta, decidir rota (store / request_human_review / reject).
6. Notificar decisão via Telegram Bot em tempo real.

## Vantagens

- Evita dependências externas adicionais.
- Fácil de rodar localmente para demonstração e testes.
- Mantém a vantagem do contexto, com baixo custo operacional.

## Limitações

- Recuperação é baseada em correspondência simples (token overlap); não tem equivalência semântica profunda.
- Para uso em produção, recomenda-se migrar para um índice vetorial ou serviço de busca semântica se for necessário maior qualidade de recuperação.

## Como rodar localmente (teste)

1. Inicie o retriever local (requer Node.js 14+):

```bash
# a partir da raiz do projeto
node src/solution-b-retriever.js
```

2. Importe `workflow-solution-b.json` no n8n e garanta que o nó `Local Retriever` aponte para `http://localhost:3000/search`.

3. Envie um payload de teste ao webhook definido no workflow.

4. As decisões serão notificadas via Telegram Bot em tempo real.

## Arquivos relevantes

- `knowledge.json` — base de conhecimento simples (temas, palavras-chave, resumos).
- `src/solution-b-retriever.js` — servidor HTTP local que expõe `/search`.
- `workflow-solution-b.json` — fluxo n8n atualizado para usar o retriever local.
