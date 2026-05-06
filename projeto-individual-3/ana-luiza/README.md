# Projeto Individual 3 — Ana Luiza

Agente de curadoria automatizada de artigos científicos construído com **n8n**, **Google Gemini 2.5 Flash** e **Semantic Scholar Bulk Search API**.

---

## O que o agente faz

Dado um objetivo de pesquisa em linguagem natural, o agente:
1. Gera uma query booleana em inglês (ex: `("smartphone" OR "mobile phone") +school +learning`)
2. Busca até 5 artigos na Semantic Scholar Bulk Search API
3. Filtra artigos sem abstract
4. Classifica cada artigo com score de relevância, resumo em português e decisão de ação
5. Grava os resultados no Google Sheets (aba **Registros**)
6. Registra artigos prioritários na aba **Alertas** (`decisao = revisar` ou `relevancia >= 0.8`)

---

## Arquitetura do Pipeline (n8n)

```
Manual Trigger
  └─► Edit Fields (objetivo_pesquisa)
        └─► Agente 1 — Gemini 2.5 Flash  →  query booleana em inglês
              └─► HTTP Request — Semantic Scholar Bulk Search API (limit=5)
                    └─► Split Out  →  Filter (remove abstract nulo)  →  Limit
                          └─► Agente 2 — Gemini 2.5 Flash  →  JSON classificado
                                └─► Code (JSON.parse)
                                      └─► IF (confianca >= 0.6)
                                            └─► Switch (arquivar / revisar / descartar)
                                                  ├─► Google Sheets — aba Registros
                                                  └─► Google Sheets — aba Alertas
                                                      (se revisar ou relevancia >= 0.8)
```

---

## Ferramentas e Credenciais

| Ferramenta | Detalhes |
|---|---|
| **n8n** | Orquestrador do pipeline (self-hosted ou cloud) |
| **Google Gemini 2.5 Flash** | `models/gemini-2.5-flash` via credencial **Google PaLM API** no n8n |
| **Semantic Scholar Bulk Search API** | `graph/v1/paper/search/bulk` — gratuita, sem chave de API |
| **Google Sheets** | Credencial **Google Sheets OAuth2** no n8n |

---

## Como Executar

### Pré-requisitos

- Instância do n8n (v1.x ou superior)
- Conta Google com acesso ao Google Sheets
- Credencial **Google PaLM API** configurada no n8n (para o Gemini)
- Credencial **Google Sheets OAuth2** configurada no n8n

### Passos

1. **Importe o workflow** no n8n:
   - Vá em *Workflows → Import from file*
   - Selecione `src/workflow-solution-b.json`

2. **Configure as credenciais** nos nós:
   - Nos dois nós **Message a model** (Agente 1 e Agente 2): selecione sua credencial **Google PaLM API**
   - No nó **Append or update row in sheet**: selecione sua credencial **Google Sheets OAuth2**

3. **Configure a planilha** no nó Google Sheets:
   - Aponte para sua planilha do Google Sheets
   - Crie as abas **Registros** e **Alertas** com os cabeçalhos correspondentes

4. **Ajuste o objetivo de pesquisa** no nó **Edit Fields** (campo `objetivo_pesquisa`)

5. **Execute** clicando em *Execute workflow*

---

## Estrutura do Repositório

```
projeto-individual-3/ana-luiza/
├── README.md                          # Este arquivo
├── agent.md                           # Agent Card: comportamento, ferramentas, output contract
├── docs/
│   ├── mission-brief.md               # Requisitos, limites e critérios de aceitação
│   ├── workflow-runbook.md            # Guia operacional do pipeline n8n
│   ├── mentorship-pack.md             # Reflexões e decisões de design
│   └── adr/                           # Architecture Decision Records
├── solutions/
│   ├── solution-a/                    # Abordagem alternativa A
│   ├── solution-b/                    # ← Solução implementada (este projeto)
│   │   └── README.md                  # Fluxo detalhado, decisões e limitações
│   └── solution-c/                    # Abordagem alternativa C
├── src/
│   └── workflow-solution-b.json       # Workflow n8n exportado (importar para executar)
└── tests/                             # Evidências de execução (prints, logs)
```

---

## Saídas do Agente 2 (por artigo)

| Campo | Tipo | Descrição |
|---|---|---|
| `titulo` | string | Título exato retornado pela Semantic Scholar |
| `ano` | integer \| null | Ano de publicação |
| `relevancia` | float (0–1) | Score de relevância ao objetivo |
| `resumo_pt` | string | Resumo em até 30 palavras em português |
| `decisao` | enum | `arquivar` ou `descartar` |

Artigos com `decisao = revisar` ou `relevancia >= 0.8` recebem adicionalmente um registro na aba **Alertas** com `status = aguardando_revisao`.
