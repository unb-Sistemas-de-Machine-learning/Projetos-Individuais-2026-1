# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Lucas Guimarães Borges
> **Matrícula:** 222015159
> **Data de entrega:** 28/03/2026

---

## 1. Resumo do Projeto

O problema tratado é a dificuldade de descobrir, de forma personalizada, **eventos culturais futuros no Distrito Federal**. Foi construído um **agente conversacional de recomendação** que responde em português no terminal, usando exclusivamente dados recuperados de uma base vetorial (RAG), sem inventar eventos ou locais.

O pipeline inclui: coleta automática dos dados (`__NEXT_DATA__` da página Metrópoles), filtragem por janela temporal, geração de embeddings e armazenamento no **Pinecone**, e um **LLM via LangChain** (OpenAI `gpt-5-nano` por padrão) que interpreta a pergunta do usuário e formata recomendações com data, local, faixa etária, gratuidade e links de compra (eventos pagos) quando existirem na base.

O principal resultado é um sistema **funcional de ponta a ponta**: atualização da agenda, indexação semântica e chat interativo alinhado ao domínio Cultura e à restrição de **integração com APIs externas** (OpenAI, Pinecone, site Metrópoles).

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Cultura |
| **Função do agente** | Recomendação |
| **Restrição obrigatória** | Integração com API externa |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

- **Texto livre em linguagem natural**, em português, digitado no terminal após `uv run python main.py chat` (ex.: “eventos gratuitos no fim de semana”, “quero teatro”, “algo para ir com adolescente”).
- **Contexto implícito:** data/hora atuais injetadas no *system prompt* (`{{CURRENT_DATE}}`) para o agente não sugerir eventos passados e respeitar o recorte temporal da base.
- **Dados de apoio (não digitados pelo usuário):** trechos recuperados do Pinecone a cada turno, montados automaticamente a partir da pergunta (embedding da query + busca por similaridade).

### 3.2 Processamento (Pipeline)

1. **(Opcional, fora do chat)** `main.py scrape` — HTTP GET na URL da agenda Metrópoles, extração do JSON embutido `__NEXT_DATA__`, normalização em `events.json` (lista plana de eventos com metadados).
2. **(Opcional, fora do chat)** `main.py sync` — deduplicação por `id`, filtro de eventos cuja data intersecta a janela `[hoje, hoje + N dias]` (default 14), texto para embedding, **OpenAI `text-embedding-3-small`** (512 dimensões), *upsert* no índice Pinecone `events` (após limpeza do namespace).
3. **No chat:** embedding da pergunta → **query** no Pinecone (`top_k` = 15) → montagem de contexto (trechos com título, tipo, datas, local, link, etc.).
4. **LLM (LangChain):** mensagens `SystemMessage` (políticas + data) + turnos anteriores (carregados de `chat_memory.json`, só texto da pergunta e da resposta) + `HumanMessage` do turno atual (contexto RAG + pergunta) → resposta estruturada conforme o prompt.

```
Usuário (pergunta em texto)
    → [Embedding OpenAI] → [Pinecone: similaridade] → [Contexto: trechos da agenda DF]
    → [LangChain ChatModel: system + histórico + pergunta enriquecida]
    → Resposta formatada (Markdown no terminal)
```

### 3.3 Decisão

O “raciocínio” é **híbrido**:

- **Recuperação:** a escolha de *quais* eventos entram no contexto é feita por **similaridade vetorial** entre a pergunta e os documentos indexados (não por regras fixas de palavras-chave).
- **Geração:** o **LLM** ordena e redige a resposta seguindo o arquivo `event_agent_system.md`: prioriza combinação com o pedido, eventos futuros, transparência quando faltar link/classificação, âmbito **somente DF**, e formato com campos por evento (categoria, data, horário, local, gratuito/pago, idade, resumo, link).

O modelo de chat utilizado é a API **OpenAI** via LangChain (`ChatOpenAI`), com nome configurável por variável de ambiente (ex.: `OPENAI_AGENT_MODEL`).

### 3.4 Saída (Output)

- **Canal:** terminal, com formatação **Rich + Markdown** (títulos, listas, ênfase).
- **Conteúdo:** recomendações em português do Brasil; por evento, quando possível: nome, categoria, data, horário, local, gratuito/pago, faixa etária, resumo curto e link de compra copiado do RAG (ou texto explícito quando ausente).
- **Comportamento conversacional:** vários turnos na mesma execução; entre execuções, o histórico pode ser **persistido** em `chat_memory.json` (lista de `{ "user", "assistant" }` por turno, UTF-8). O ficheiro fica na raiz do projeto por omissão (`CHAT_MEMORY_PATH` para outro caminho; `CHAT_MEMORY_DISABLE=1` para não gravar nem carregar).

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão (mínima em `pyproject.toml`) | Finalidade |
|------------|----------------------------------------|------------|
| Python | `>=3.12` | Linguagem principal |
| OpenAI API | `openai>=2.30.0` | Embeddings (`text-embedding-3-small`, 512 dims) e chat (`gpt-5-nano` padrão) |
| Pinecone | `pinecone>=8.1.0` | Índice vetorial serverless `events` (cosine, dim. 512) |
| LangChain | `langchain-core>=1.2.23`, `langchain-openai>=1.1.12` | Abstração do modelo de chat (`ChatOpenAI`) e mensagens |
| python-dotenv | `>=1.2.2` | Carregamento de `.env` |
| tiktoken | `>=0.12.0` | Truncagem de texto antes do embedding na indexação |
| rich | `>=14.3.3` | UI no terminal (painel, Markdown) |
| urllib (stdlib) | — | Scraper HTTP sem browser |
| uv | (ferramenta no host) | Gestão de dependências e ambiente virtual a partir de `pyproject.toml` / `uv.lock` |
| pytest | grupo `dev` no `pyproject.toml` | Testes unitários (`uv sync --group dev`; `uv run pytest`) |

### 4.2 Estrutura do código

Caminho no repositório da disciplina: `projeto-individual-1/lucas-guimaraes-borges/projeto-1/` (pasta do aluno + `projeto-1/`, conforme o README do curso).

```
projeto-1/
├── main.py                      # CLI: scrape | sync | chat
├── pyproject.toml               # Dependências (e metadados do pacote)
├── uv.lock                      # Lock de versões (uv)
├── .env.example
├── events.json                  # Gerado pelo scrape (pode ir no PR para facilitar revisão)
├── documento-engenharia.md
├── relatorio-entrega.md
├── README.md
├── tests/
│   ├── test_filters.py          # Datas, janela, deduplicação
│   ├── test_memory.py           # JSON de conversa
│   └── test_runner_helpers.py   # Prompt + format_match
└── src/
    ├── scraper.py               # Metrópoles (__NEXT_DATA__)
    ├── utils/
    │   └── paths.py             # Raiz do projeto, .env, caminhos
    ├── rag/
    │   ├── filters.py           # Datas, janela, deduplicação
    │   ├── documents.py         # Texto + metadados para embedding
    │   └── sync.py              # Pipeline Pinecone
    └── agent/
        ├── chat_models.py       # ChatOpenAI (LangChain)
        ├── memory.py            # Load/save de turnos em JSON
        ├── runner.py            # Loop do chat + RAG
        └── prompts/
            └── event_agent_system.md
```

_Validação complementar:_ testes manuais do pipeline (`scrape`, `sync`, `chat`) e **22 testes pytest** em módulos sem I/O de rede (filtros, memória JSON, helpers do runner).

### 4.3 Como executar

_Instruções passo a passo para rodar o projeto:_

```bash
# 0. Entrar na pasta do projeto (onde está main.py)
cd projeto-individual-1/lucas-guimaraes-borges/projeto-1

# 1. Instalar dependências com uv (cria/atualiza .venv a partir do uv.lock)
uv sync

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX=events
# Opcional: OPENAI_AGENT_MODEL, OPENAI_AGENT_TEMPERATURE, AGENT_LLM_PROVIDER=openai

# 3. Atualizar agenda local e índice vetorial
uv run python main.py scrape
uv run python main.py sync

# 4. Agente de recomendação (chat)
uv run python main.py chat
```

Comandos úteis: `uv run python main.py sync --dry-run --skip-scrape` (contar eventos na janela sem gastar API de embedding/Pinecone).

Testes unitários (requer `uv sync --group dev`):

```bash
uv run pytest
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Cobertura do pipeline | Scrape → JSON → sync → Pinecone sem erro | OK em ambiente com chaves válidas e índice criado (dim. 512) |
| Adequação ao domínio | Respostas só com fatos presentes nos trechos recuperados | Qualitativo: segue regras do system prompt; depende da qualidade do *top_k* |
| Usabilidade do chat | Perguntas de seguimento com histórico (sessão + JSON opcional) | OK: LangChain + `chat_memory.json` |
| Latência percebida | Tempo até resposta completa | Depende de rede, tamanho do contexto e modelo; não medido formalmente neste relatório |
| Testes unitários (pytest) | Filtros, memória JSON, prompt e `format_match` | 22 testes, todos passando (`uv run pytest`) |
| Demonstração gravada | Vídeo: `scrape` → `sync` (Pinecone) → `chat` pedindo próximos eventos | [YouTube](https://youtu.be/i3IxOos8NFI) (secção 5.3) |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:** `uv run python main.py scrape` (com rede e URL da agenda acessível).
- **Saída esperada:** arquivo `events.json` atualizado e mensagem no stderr com contagem de eventos.
- **Saída obtida:** gravação em disco e contagem coerente com a agenda publicada.
- **Resultado:** Sucesso

#### Teste 2

- **Pré-condição:** o RAG só funciona com vetores no Pinecone. Após o Teste 1 (ou com `events.json` válido), é obrigatório executar `uv run python main.py sync`, que aplica **embeddings** (OpenAI) aos textos dos eventos e faz *upsert* no índice. Sem esse passo, a consulta semântica no chat não tem base recuperável.
- **Entrada:** `uv run python main.py chat`; em seguida a pergunta: “Quero eventos de comédia ou stand-up esta semana no DF.”
- **Saída esperada:** lista de eventos alinhados ao tipo, com datas futuras e links de pagamentos de ingressos apenas se existirem nos trechos recuperados pelo RAG.
- **Saída obtida:** recomendações em Markdown com campos por evento; eventos fora do DF não são inventados.
- **Resultado:** Sucesso (qualitativo)

### 5.3 Demonstração gravada (teste de execução real)

Existe um **teste gravado em vídeo** (captura de ecrã do terminal) que documenta a execução completa do protótipo, na ordem abaixo:

1. **`uv run python main.py scrape`** — obtenção da agenda Metrópoles, normalização e gravação de `events.json`, com saída no terminal (contagem / confirmação de sucesso).
2. **`uv run python main.py sync`** — leitura dos eventos na janela temporal, geração de **embeddings** (OpenAI), limpeza do *namespace* e **carga dos vetores no Pinecone** (*upsert* no índice configurado, dimensão 512).
3. **`uv run python main.py chat`** — sessão interativa em que se pede, em linguagem natural, **informações sobre próximos eventos** culturais no DF (eventos futuros na agenda); o assistente responde com recomendações em Markdown, ancoradas nos trechos recuperados pelo RAG.

**Link do vídeo:** [Demonstração — scrape, sync, Pinecone e chat (próximos eventos)](https://youtu.be/i3IxOos8NFI)  
URL direto: https://youtu.be/i3IxOos8NFI

A gravação serve de evidência qualitativa do pipeline **dados → índice vetorial → conversação**, além dos testes automatizados em `pytest`.

### 5.4 Análise dos resultados

O agente **atinge o objetivo** de recomendação cultural restrita ao DF e ancorada na agenda indexada. **Pontos fortes:** arquitetura clara (scraper + RAG + LLM), uso de APIs externas explícito, prompt detalhado para reduzir alucinação de fatos, ajuste do modelo de chat OpenAI por variável de ambiente, memória de conversa persistida em JSON entre execuções, **testes pytest** nas partes determinísticas do código. **Pontos fracos:** dependência do layout do site (quebra se o Metrópoles mudar `__NEXT_DATA__`); custo e quota das APIs; integração RAG/chat sem testes automatizados e2e (há **demonstração gravada** e testes manuais; mocks ou *staging* ficam para evolução); métricas quantitativas de relevância (NDCG, etc.) não aplicadas; ficheiro de memória contém texto do utilizador (cuidados com partilha e LGPD).

---

## 6. Diferenciais implementados

_Marque os diferenciais que foram implementados:_

- [x] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [x] Memória persistente (`chat_memory.json`)
- [x] Explicabilidade (saída estruturada por evento; ausências indicadas explicitamente no prompt)
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

**Limitações:** (1) escopo geográfico e de conteúdo limitados ao que a agenda Metrópoles publica; (2) janela temporal do índice (ex.: 14 dias) pode omitir eventos mais distantes; (3) metadado `gratuito` deriva da presença de `purchase_link` na indexação — casos limite (pago sem URL) podem ser mal classificados; (4) primeiro `delete_all` no Pinecone em namespace vazio pode retornar 404 tratado no código, mas operações em escala exigem monitoramento.

**Trabalhos futuros:** agendamento (cron) para `sync` diário; testes do scraper com HTTP mockado; testes e2e do chat com APIs mockadas; avaliação com usuários ou métricas IR; interface web; limite/rotação de turnos no JSON ou resumo semântico para conversas longas; enriquecimento com outras fontes oficiais do DF; uso de *tools* (ex.: abrir URL apenas sob confirmação).

---

## 8. Referências

1. OpenAI. *Embeddings e modelos de chat* — documentação em https://platform.openai.com/docs  
2. Pinecone. *Documentação do índice e API de dados* — https://docs.pinecone.io  
3. LangChain. *Integração OpenAI (ChatOpenAI)* — https://python.langchain.com  
4. Metrópoles. *Agenda cultural* — https://www.metropoles.com/agenda-cultural (fonte dos dados brutos)

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Demonstração gravada (scrape → sync/Pinecone → chat sobre próximos eventos) anexada ou enviada conforme regras da disciplina
- [ ] Pull Request aberto _(preencher pelo aluno após envio ao repositório remoto)_
