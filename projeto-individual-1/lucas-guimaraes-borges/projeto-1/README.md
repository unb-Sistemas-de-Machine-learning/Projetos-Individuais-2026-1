# Projeto Individual 1 — Agenda cultural DF (agente de recomendação)

Agente conversacional em terminal que recomenda eventos culturais no **Distrito Federal** a partir da agenda Metrópoles, com **RAG** (Pinecone + embeddings OpenAI) e **LLM** (LangChain / OpenAI).

Documentação de requisitos e arquitetura: [`documento-engenharia.md`](documento-engenharia.md).  
Relatório de entrega, modelagem e testes: [`relatorio-entrega.md`](relatorio-entrega.md).

## Pré-requisitos

Este projeto usa **exclusivamente o [uv](https://docs.astral.sh/uv/)** para instalar dependências e criar o ambiente virtual a partir de `pyproject.toml` e `uv.lock`. **É obrigatório ter o `uv` instalado** no sistema antes de rodar qualquer comando abaixo.

Instalação rápida do uv: ver a [documentação oficial](https://docs.astral.sh/uv/getting-started/installation/) (por exemplo, `curl -LsSf https://astral.sh/uv/install.sh | sh` no Linux/macOS).

## Execução rápida

```bash
uv sync
cp .env.example .env   # preencher chaves
uv run python main.py scrape
uv run python main.py sync
uv run python main.py chat
```

Depois de `uv sync`, pode ativar `.venv` e usar `python main.py …` se preferir.

## Testes automatizados

```bash
uv sync --group dev
uv run pytest
```

Cobrem `rag/filters`, `agent/memory` e funções puras do `runner` (prompt, formatação de trechos RAG), sem chamadas a APIs externas.

Há ainda uma **demonstração gravada** (vídeo do terminal) descrita no relatório: execução de `scrape`, `sync` com envio dos vetores ao **Pinecone** e conversa de exemplo pedindo **próximos eventos** culturais no DF — ver secção **5.3** de [`relatorio-entrega.md`](relatorio-entrega.md).

**Link do vídeo:** [YouTube — demonstração do projeto](https://youtu.be/i3IxOos8NFI) (`https://youtu.be/i3IxOos8NFI`).

## Variáveis de ambiente

Ver `.env.example`. É necessário índice Pinecone com dimensão **512** e métrica **cosine**, nome configurável em `PINECONE_INDEX`.

O histórico de conversa (pergunta + resposta por turno) é guardado em **`chat_memory.json`** na raiz do projeto (ficheiro no `.gitignore`). Use `CHAT_MEMORY_DISABLE=1` para desativar ou `CHAT_MEMORY_PATH` para outro caminho.
