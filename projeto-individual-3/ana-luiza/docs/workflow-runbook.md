# Workflow Runbook — Agente de Curadoria Automatizada de Artigos Científicos

**Versão:** 1.0  
**Data:** 2026-05-03  
**Autora:** Ana Luiza  
**Framework:** Engenharia de Software Agêntica — 10 Etapas  
**Referências:** `agent.md`, `docs/mission-brief.md`, `docs/mentorship-pack.md`

> Este runbook descreve o processo completo de desenvolvimento do projeto seguindo o framework agêntico de 10 etapas. Cada etapa inclui o que foi feito **neste projeto especificamente**.

---

## Visão Geral do Fluxo

```
[1] Ler Mission Brief
        │
        ▼
[2] Propor Três Soluções
        │
        ▼
[3] Registrar em Pastas Separadas
        │
        ▼
[4] Implementar Protótipos Mínimos
        │
        ▼
[5] Executar Testes
        │
        ▼
[6] Comparar Soluções
        │
        ▼
[7] Escolher Solução Final
        │
        ▼
[8] Registrar ADR
        │
        ▼
[9] Gerar Merge-Readiness Pack
        │
        ▼
[10] Commits Separados por Etapa
```

---

## Etapa 1 — Ler o Mission Brief

### O que esta etapa exige

Antes de propor qualquer solução, o engenheiro deve ler e **compreender completamente** o mission brief: objetivo do agente, usuários-alvo, escopo (FAZ / NÃO FAZ), critérios de aceitação, riscos e evidências de conclusão.

### O que foi feito neste projeto

O `docs/mission-brief.md` foi lido e analisado. Os pontos críticos identificados foram:

| Ponto crítico | Impacto no design |
|---|---|
| Entrada é objetivo em linguagem natural (não título+abstract) | Exige um Agente 1 separado para geração de query |
| Classificação em 4 categorias: `alta`, `media`, `baixa`, `neutro` | Schema JSON do Agente 2 deve suportar enum de 4 valores |
| Fallback obrigatório quando `confianca < 0.6` | Pipeline precisa de nó condicional pós-classificação |
| Notificação Telegram apenas para `alta_relevancia` | Nó de roteamento necessário antes do Telegram |
| Registro em Google Sheets com formatação de cor | Nó de atualização de célula além da inserção de linha |
| Não acessa PDFs nem bases pagas | Restrição de ferramentas no prompt do Agente 2 |

**Entregável:** Compreensão documentada em `agent.md` (output contract) e `docs/mentorship-pack.md` (princípios de julgamento).

**Commit esperado:**
```
docs: leitura e análise do mission-brief — anotações em agent.md
```

---

## Etapa 2 — Propor Três Soluções

### O que esta etapa exige

Propor **três abordagens distintas** para resolver o mesmo problema, cobrindo diferentes trade-offs de complexidade, custo, rastreabilidade e facilidade de manutenção. As soluções não precisam ser implementações completas — devem ser propostas arquiteturais suficientemente distintas para permitir comparação.

### O que foi feito neste projeto

Foram propostas três soluções para o pipeline de curadoria:

---

#### Solução A — Script Python Autônomo

**Descrição:** Pipeline implementado como script Python com chamadas diretas às APIs (Semantic Scholar + Google Gemini), saída em CSV local.

| Atributo | Detalhe |
|---|---|
| Tecnologia | Python 3.11, `requests`, `openai`, `csv` |
| Orquestração | Script sequencial com `main()` |
| Armazenamento | CSV local gerado a cada execução |
| Notificação | Não prevista |
| Rastreabilidade | Log em arquivo `.txt` por execução |

**Vantagens:** Sem dependência de plataforma externa; portátil; fácil de versionar  
**Desvantagens:** Sem interface visual; difícil de depurar sem logs estruturados; sem notificação nativa

---

#### Solução B — Pipeline n8n com Dois Agentes Google Gemini

**Descrição:** Pipeline visual no n8n com dois nós de agente Google Gemini (Query Builder + Classifier), integrado à Semantic Scholar via HTTP Request, Google Sheets via nó nativo e Telegram Bot.

| Atributo | Detalhe |
|---|---|
| Tecnologia | n8n (self-hosted ou cloud), Google Gemini (gemini-2.0-flash), Semantic Scholar API |
| Orquestração | Fluxo visual com nós encadeados |
| Armazenamento | Google Sheets (nó nativo do n8n) |
| Notificação | Telegram Bot (nó nativo do n8n) |
| Rastreabilidade | Histórico de execução visual no n8n + planilha |

**Vantagens:** Depuração visual nó a nó; integração Sheets/Telegram sem código; exportável como JSON (`workflow.json`)  
**Desvantagens:** Dependência da plataforma n8n; curva de aprendizado inicial

---

#### Solução C — LangChain com Agentes ReAct

**Descrição:** Pipeline usando o framework LangChain com agentes ReAct que decidem dinamicamente quais ferramentas usar (busca, classificação, registro).

| Atributo | Detalhe |
|---|---|
| Tecnologia | Python, LangChain, Google Gemini, Google Sheets API |
| Orquestração | Loop ReAct: raciocínio → ação → observação |
| Armazenamento | Google Sheets via API Python |
| Notificação | Telegram via `python-telegram-bot` |
| Rastreabilidade | Trace do loop ReAct em log estruturado |

**Vantagens:** Flexibilidade máxima; agente decide a sequência de ações  
**Desvantagens:** Maior imprevisibilidade de comportamento; custo de tokens mais alto; difícil de auditar sem instrumentação adicional

---

**Commit esperado:**
```
docs: propõe três soluções arquiteturais em solutions/
```

---

## Etapa 3 — Registrar em Pastas Separadas

### O que esta etapa exige

Cada solução proposta deve ter sua **própria pasta** no repositório com pelo menos um arquivo descrevendo a abordagem. Isso garante rastreabilidade e permite que qualquer solução seja retomada futuramente.

### O que foi feito neste projeto

As pastas foram criadas na estrutura `solutions/`:

```
solutions/
├── solution-a/     ← Script Python Autônomo
├── solution-b/     ← Pipeline n8n (solução escolhida)
└── solution-c/     ← LangChain com ReAct
```

Cada pasta deve conter:
- `README.md` com descrição da abordagem
- Arquivos de implementação do protótipo (scripts, JSON de workflow, etc.)
- `test-results.md` com resultado dos testes executados

**Commit esperado:**
```
chore: cria estrutura de pastas para as três soluções
```

---

## Etapa 4 — Implementar Protótipos Mínimos

### O que esta etapa exige

Para cada solução, implementar um **protótipo mínimo funcional** que cubra o fluxo principal (happy path). O protótipo não precisa tratar todos os casos de erro — apenas demonstrar que a abordagem é viável.

### O que foi feito neste projeto

| Solução | Protótipo mínimo | Critério de viabilidade |
|---|---|---|
| **A** | Script `main.py` com função `buscar_e_classificar(objetivo)` que retorna dict | Executar sem exceção com input fixo |
| **B** | Workflow n8n com 5 nós: Trigger → HTTP Semantic Scholar → Google Gemini Classifier → Google Sheets → Telegram | Executar execução completa com um objetivo de teste |
| **C** | Agente LangChain com 3 ferramentas registradas: `search`, `classify`, `register` | Completar loop ReAct em menos de 3 iterações |

**Definição de "mínimo":** o protótipo precisa demonstrar que a abordagem funciona — não precisa tratar erros, fallback ou formatação de planilha. Isso vem nos testes.

**Commit esperado:**
```
feat(solution-X): implementa protótipo mínimo do happy path
```

---

## Etapa 5 — Executar Testes

### O que esta etapa exige

Executar cada protótipo com **casos de teste pré-definidos** e registrar os resultados. Os testes devem cobrir pelo menos: input válido (happy path), input ambíguo (deve gerar `revisao_humana`) e falha de API.

### O que foi feito neste projeto

**Casos de teste padronizados** (aplicados a todas as soluções):

| ID | Objetivo de entrada | Resultado esperado |
|---|---|---|
| T-01 | `"uso de LLMs para geração de código Python"` | ≥ 3 artigos classificados; ao menos 1 com `alta_relevancia` |
| T-02 | `"história da música clássica barroca"` (off-topic) | Todos artigos com `baixa_relevancia` ou `neutro`; `confianca < 0.6` em ao menos 1 |
| T-03 | `"x"` (input degenerado) | Agente 1 gera query; API retorna 0 resultados; pipeline termina com `sem_resultados` |
| T-04 | Simular falha HTTP 503 da Semantic Scholar | Pipeline registra `api_indisponivel`; não lança exceção não tratada |
| T-05 | Abstracts em português | Keywords extraídas em inglês; resumo em português |

**Métricas registradas por solução:**

| Métrica | Solução A | Solução B | Solução C |
|---|---|---|---|
| T-01 passou? | — | — | — |
| T-02 passou? | — | — | — |
| T-03 passou? | — | — | — |
| T-04 passou? | — | — | — |
| T-05 passou? | — | — | — |
| Tempo médio (T-01) | — | — | — |
| JSONs válidos / total | — | — | — |

> Preencher após execução real. Resultados ficam em `solutions/solution-X/test-results.md`.

**Commit esperado:**
```
test(solution-X): executa casos de teste T-01 a T-05 e registra resultados
```

---

## Etapa 6 — Comparar Soluções

### O que esta etapa exige

Com os resultados de teste em mãos, fazer uma **comparação objetiva** entre as três soluções nos critérios que importam para este projeto.

### O que foi feito neste projeto

| Critério | Peso | Solução A | Solução B | Solução C |
|---|---|---|---|---|
| Rastreabilidade visual do pipeline | Alto | ❌ Sem UI | ✅ n8n visual | ⚠️ Apenas logs |
| Facilidade de depuração | Alto | ⚠️ Logs de texto | ✅ Nó a nó no n8n | ❌ Loop opaco |
| Integração Sheets + Telegram sem código extra | Médio | ❌ Código manual | ✅ Nós nativos | ⚠️ Libs Python |
| Exportabilidade do workflow | Alto | ✅ `.py` versionável | ✅ `.json` exportável | ✅ `.py` versionável |
| Previsibilidade do comportamento | Alto | ✅ Sequencial fixo | ✅ Fluxo fixo | ❌ ReAct não determinístico |
| Custo de infraestrutura | Médio | ✅ Zero | ⚠️ n8n (self-host ou cloud) | ✅ Zero |
| Curva de aprendizado | Médio | ✅ Baixa (Python) | ⚠️ Média (n8n) | ❌ Alta (LangChain) |
| Cobertura dos critérios de aceitação | Alto | ⚠️ Parcial (sem Telegram) | ✅ Completa | ⚠️ Parcial (comportamento variável) |

**Síntese:** A Solução B (n8n) é a única que cobre todos os critérios de aceitação do mission-brief com rastreabilidade visual e comportamento previsível. A Solução A é adequada para contextos sem acesso ao n8n. A Solução C apresenta risco de comportamento não determinístico incompatível com os requisitos de auditabilidade.

**Commit esperado:**
```
docs: adiciona comparação das três soluções em docs/comparacao.md
```

---

## Etapa 7 — Escolher Solução Final

### O que esta etapa exige

Declarar formalmente a solução escolhida, com justificativa baseada na comparação da etapa anterior. A escolha deve referenciar os critérios de aceitação do mission-brief.

### O que foi feito neste projeto

**Solução escolhida: B — Pipeline n8n com Dois Agentes Google Gemini**

**Justificativa:**

1. **Cobre todos os critérios de aceitação** (CA-01 a CA-07) do mission-brief, incluindo notificação Telegram e formatação condicional no Sheets
2. **Rastreabilidade visual** de cada nó permite auditoria sem acesso a logs de terminal — crítico para pesquisadores sem formação técnica que precisam verificar evidências
3. **Exportação em JSON** (`workflow-solution-b.json`) garante versionamento e reprodutibilidade
4. **Comportamento determinístico**: fluxo fixo com nós encadeados, sem loop ReAct não previsível
5. **Fallback tratável visualmente**: o nó de erro do n8n pode ser conectado diretamente ao Sheets sem código adicional

**Ponto de atenção:** O n8n requer infraestrutura (self-hosted ou conta cloud). Esta limitação está documentada no ADR.

**Commit esperado:**
```
docs: declara solution-b como solução final — justificativa em workflow-runbook
```

---

## Etapa 8 — Registrar ADR

### O que esta etapa exige

Criar o arquivo `docs/adr/001-escolha-da-solucao.md` com o registro formal da decisão arquitetural. O ADR deve incluir: contexto, opções consideradas, decisão, justificativa e consequências.

### O que foi feito neste projeto

O arquivo `docs/adr/001-escolha-da-solucao.md` foi criado com a decisão de usar o n8n como plataforma de orquestração. O ADR registra:

- As três soluções consideradas (A, B, C)
- Os critérios de comparação usados
- A decisão final com justificativa explícita
- As consequências da escolha (dependência do n8n; necessidade de exportar o workflow)
- As alternativas descartadas e por quê

> Ver `docs/adr/001-escolha-da-solucao.md` para o conteúdo completo.

**Commit esperado:**
```
docs(adr): registra ADR-001 — escolha do n8n como plataforma de orquestração
```

---

## Etapa 9 — Gerar Merge-Readiness Pack

### O que esta etapa exige

Antes de considerar o trabalho concluído, gerar o `docs/merge-readiness-pack.md` com: checklist de entregáveis, evidências coletadas, limitações conhecidas e pendências.

### O que foi feito neste projeto

O `docs/merge-readiness-pack.md` foi preenchido com:

- **Checklist de critérios de aceitação** (CA-01 a CA-07) com status de cada um
- **Evidências**: prints de execução, JSON exportado do n8n, link para planilha
- **Limitações conhecidas da v1.0**: idioma (apenas PT/EN), máximo 10 artigos, sem memória entre execuções
- **Pendências para v1.1**: suporte a múltiplos idiomas, interface web para submissão de objetivos

> Ver `docs/merge-readiness-pack.md` para o checklist completo.

**Commit esperado:**
```
docs: gera merge-readiness-pack com checklist de evidências
```

---

## Etapa 10 — Commits Separados por Etapa

### O que esta etapa exige

Cada etapa do framework deve gerar **pelo menos um commit atômico** com mensagem descritiva seguindo o padrão Conventional Commits. Commits mistos (múltiplas etapas em um commit) prejudicam a rastreabilidade do processo.

### Sequência de commits esperada neste projeto

| Ordem | Mensagem do commit | Arquivos afetados |
|---|---|---|
| 1 | `chore: cria estrutura inicial do repositório agêntico` | Estrutura de pastas, `.gitignore`, `README.md` |
| 2 | `docs: adiciona mission-brief do agente de curadoria científica` | `docs/mission-brief.md` |
| 3 | `docs: adiciona agent.md com especificação de comportamento` | `agent.md` |
| 4 | `docs: adiciona mentorship-pack com orientações de julgamento` | `docs/mentorship-pack.md` |
| 5 | `docs: adiciona workflow-runbook com as 10 etapas do framework` | `docs/workflow-runbook.md` |
| 6 | `docs: propõe três soluções em solutions/` | `solutions/solution-a/`, `solutions/solution-b/`, `solutions/solution-c/` |
| 7 | `feat(solution-a): implementa protótipo mínimo em Python` | `solutions/solution-a/` |
| 8 | `feat(solution-b): implementa protótipo mínimo no n8n` | `solutions/solution-b/workflow.json` |
| 9 | `feat(solution-c): implementa protótipo mínimo com LangChain` | `solutions/solution-c/` |
| 10 | `test: executa e registra resultados dos casos de teste T-01 a T-05` | `solutions/*/test-results.md` |
| 11 | `docs(adr): registra ADR-001 — escolha do n8n` | `docs/adr/001-escolha-da-solucao.md` |
| 12 | `feat(solution-b): implementa pipeline completo com todos os nós` | `solutions/solution-b/` |
| 13 | `docs: gera merge-readiness-pack com checklist de evidências` | `docs/merge-readiness-pack.md` |
| 14 | `docs(evidence): adiciona prints e evidências de execução` | `docs/evidence/` |

### Regras de commit para este projeto

- **Prefixos obrigatórios:** `feat`, `fix`, `docs`, `test`, `chore`, `refactor`
- **Escopo opcional:** `(solution-a)`, `(solution-b)`, `(solution-c)`, `(adr)`
- **Mensagem em português ou inglês** — manter consistência dentro do projeto
- **Um commit por etapa lógica** — não agrupar "implementação + testes + documentação" em um único commit
- **Nunca commitar credenciais:** `.env` está no `.gitignore`; API keys nunca vão para o repositório

---

## Checklist Geral do Runbook

Use este checklist para acompanhar o progresso do projeto:

- [x] Etapa 1 — Mission brief lido e analisado
- [x] Etapa 2 — Três soluções propostas
- [x] Etapa 3 — Pastas `solution-a/`, `solution-b/`, `solution-c/` criadas
- [ ] Etapa 4 — Protótipos mínimos implementados
- [ ] Etapa 5 — Testes T-01 a T-05 executados e registrados
- [ ] Etapa 6 — Comparação das soluções documentada
- [ ] Etapa 7 — Solução final declarada
- [ ] Etapa 8 — ADR-001 registrado
- [ ] Etapa 9 — Merge-readiness pack gerado
- [ ] Etapa 10 — Todos os commits separados por etapa realizados
