# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Ana Luiza Soares de Carvalho
> **Matrícula:** 231011088
> **Domínio:** Participação Cidadã
> **Função do agente:** Detecção de Anomalias
> **Restrição obrigatória:** Integração com API Externa

---

## 1. Problema e Contexto

O Brasil possui um sistema de dados abertos sobre gastos de deputados federais, porém há uma quantidade massiva de informações que é difícil para cidadãos comuns analisarem manualmente. O problema é: **como detectar automaticamente possíveis irregularidades ou padrões suspeitos nos gastos de deputados federais, cruzando com a legislação brasileira?**

O contexto envolve:
- **Legislação**: Código Penal, Lei de Improbidade Administrativa, Regimento Interno da Câmara dos Deputados
- **Dados**: API de dados abertos da Câmara dos Deputados (dadosabertos.camara.leg.br)
- **Público-alvo**: Cidadãos, jornalistas de investigação, órgãos de fiscalização, movimentos de transparência

A relevância é alta, pois promove **fiscalização participativa** e **combate à corrupção** através da tecnologia.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Cidadãos e contribuintes | Usuários finais | Monitorar gastos públicos e holding de autoridades accountable |
| Jornalistas investigativos | Utilizadores avançados | Identificar histórias de impacto sobre corrupção e má gestão |
| Órgãos de fiscalização (TCU, MP) | Validadores | Usar o sistema para orientar investigações formais |
| Deputados federais | Objetos de auditoria | Potencialmente impactados pelos resultados |
| Câmara dos Deputados | Provedor de dados | Interesse em transparência e legitimidade institucional |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O agente deve buscar dados de despesas de um deputado específico via API | Alta |
| RF02 | O agente deve recuperar trechos relevantes da legislação brasileira (RAG) | Alta |
| RF03 | O agente deve analisar os gastos contra a legislação e identificar anomalias | Alta |
| RF04 | O agente deve gerar um relatório estruturado com indicadores de suspeita | Alta |
| RF05 | O agente deve citar artigos específicos da lei quando encontrar anomalias | Média |
| RF06 | O agente deve aceitar entrada por linha de comando (nome do deputado, mês, ano) | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O sistema deve integrar-se com a API pública de dados da Câmara dos Deputados | Integração |
| RNF02 | O sistema deve processar uma auditoria em menos de 30 segundos | Desempenho |
| RNF03 | Os embeddings devem ser gerados localmente (sem gasto de API) | Eficiência de custo |
| RNF04 | O sistema deve funcionar offline após o setup inicial do RAG | Robustez |
| RNF05 | O código deve ser modular e extensível para novos tipos de análise | Manutenibilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Auditar gastos de um deputado

- **Ator:** Cidadão ou jornalista investigativo
- **Pré-condição:** Sistema iniciado, RAG carregado com leis, API da Câmara acessível
- **Fluxo principal:**
  1. Usuário inicia o programa e insere o nome do deputado, mês e ano
  2. Sistema busca o ID do deputado na API
  3. Sistema recupera os gastos do período especificado
  4. Sistema consulta o RAG com os gastos como contexto
  5. LLM analisa os gastos contra a legislação
  6. Sistema exibe relatório com indicadores de anomalias e artigos citados
- **Pós-condição:** Relatório gerado e exibido ao usuário

### Caso de uso 2: Investigação aprofundada de um padrão de gasto

- **Ator:** Jornalista investigativo
- **Pré-condição:** Resultado da auditoria anterior disponível
- **Fluxo principal:**
  1. Jornalista identifica um padrão suspeito no relatório
  2. Jornalista executa nova auditoria com diferentes períodos
  3. Sistema compara padrões ao longo do tempo
  4. Sistema identifica tendências e correlações
- **Pós-condição:** Dados suficientes para investigação aprofundada

---

## 6. Fluxo do Agente

```
Entrada: (Nome_Deputado, Mês, Ano)
  ↓
[Buscar ID do Deputado] → API da Câmara
  ↓
[Recuperar Gastos] → API da Câmara
  ↓
[Formatar Relatório de Gastos] → String estruturada
  ↓
[Carregar RAG - Contexto Legal] → ChromaDB com Leis
  ↓
[Construir Prompt Analítico] → Template com contexto + gastos
  ↓
[Enviar para Gemini 2.5 Flash] → LLM
  ↓
[Analisar e Gerar Relatório] → Indicadores + Artigos citados
  ↓
Saída: Relatório de Auditoria com indicadores
```

---

## 7. Arquitetura do Sistema

**Tipo de agente:** RAG (Retrieval-Augmented Generation) + Tool-Using

**LLM utilizado:** Google Gemini 2.5 Flash (modelo disponível via API)

**Componentes principais:**
- ✅ **Módulo de entrada**: Terminal CLI que recebe nome, mês, ano
- ✅ **Módulo de ferramentas (Tools)**: `get_deputado_id()` e `get_gastos_deputado()` (integração com API)
- ✅ **Módulo RAG**: ChromaDB + HuggingFace Embeddings (all-MiniLM-L6-v2) com PDFs de leis
- ✅ **Processamento / LLM**: ChatGoogleGenerativeAI (Gemini) com PromptTemplate e RunnableChain
- ✅ **Módulo de saída**: Relatório estruturado em texto

**Diagrama de arquitetura:**

```
┌─────────────────────┐
│   Usuário (CLI)     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────────────────┐
│     AuditorAgente (Orquestrador) │
└──────┬──────────────┬────────────┘
       │              │
       ↓              ↓
┌─────────────────┐  ┌──────────────────────┐
│  API Tools      │  │  RAG (ChromaDB)      │
│  - get_deputado │  │  + Embeddings HF     │
│  - get_gastos   │  │  (Leis Brasileiras)  │
└────────┬────────┘  └──────────┬───────────┘
         │                      │
         ↓                      ↓
    ╔════════════════════╗
    ║   Gemini 2.5 Flash  ║  (LLM Core)
    ║   (via LangChain)   ║
    ╚═════════┬═══════════╝
              │
              ↓
    ┌──────────────────┐
    │  Relatório Final  │
    │  (Análise + Leis) │
    └──────────────────┘
```

---

## 8. Estratégia de Avaliação

**Métricas definidas:**
- **Precisão de detecção**: % de anomalias detectadas que são realmente relevantes (verificadas manualmente)
- **Recall**: % de anomalias reais que o sistema consegue detectar
- **Latência**: Tempo médio para processar uma auditoria (alvo: < 30s)
- **Custo de API**: Custo por auditoria (otimizado com embeddings local)
- **Relevância contextual**: Se as leis citadas são realmente aplicáveis ao caso

**Conjunto de testes:**
- 10-15 deputados com padrões variados de gasto
- Dados de 2-3 meses diferentes para cada deputado
- Gastos conhecidos como suspeitos (validados manualmente ou por órgãos de controle)

**Método de avaliação:**
- Manual: Revisão de 5-10 casos para validar se as análises fazem sentido
- Comparativo: Verificar se o sistema identifica os mesmos padrões que análises manuais prévias
- Qualitativo: Avaliar clareza e utilidade do relatório para jornalistas

---

## 9. Referências

1. **Câmara dos Deputados - API de Dados Abertos**: https://dadosabertos.camara.leg.br/swagger/index.html
2. **Código Penal Brasileiro** - Lei n.º 40, de 21 de outubro de 1940
3. **Lei de Improbidade Administrativa** - Lei n.º 8.429, de 2 de junho de 1992
4. **Regimento Interno da Câmara dos Deputados** - Resolução n.º 17, de 1989
5. **LangChain Documentation**: https://python.langchain.com
6. **ChromaDB Vector Database**: https://docs.trychroma.com
7. **HuggingFace Embeddings**: https://huggingface.co/sentence-transformers
8. **Google Gemini API**: https://ai.google.dev
