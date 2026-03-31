# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Diego Carlito Rodrigues de Souza
> **Matrícula:** 221007690
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

O projeto consiste em um **Agente Tutor de Concursos de TI**, projetado para resolver o problema da generalização em plataformas de estudo. Candidatos a certames de alto nível (como TCDF e Câmara dos Deputados) necessitam de direcionamento específico por banca examinadora (CESPE, FGV, FCC). 

Para solucionar isso, foi construído um sistema de múltiplos agentes baseados em LLM (Google Gemini), integrado a um pipeline de RAG (Retrieval-Augmented Generation) com resumos e questões reais. O principal resultado obtido é uma aplicação web interativa em Streamlit que realiza um diagnóstico dinâmico do usuário, recomenda uma trilha de estudos rigorosamente justificada (garantindo o requisito de Explicabilidade) e atua como tutor particular, gerando questões inéditas no estilo da banca e avaliando o raciocínio do candidato com foco na identificação de lacunas de conhecimento.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Educação |
| **Função do agente** | Recomendação |
| **Restrição obrigatória** | Explicabilidade obrigatória |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O sistema recebe entradas textuais interativas através da interface web:
* **Parâmetros iniciais:** Matéria (ex: Big Data, Redes), Banca (ex: CESPE, FCC) e Concurso-alvo.
* **Interações:** Respostas do usuário às questões (Certo/Errado ou Múltipla Escolha) e comandos em linguagem natural (ex: "praticar").

### 3.2 Processamento (Pipeline)

A aplicação gerencia o estado da sessão (`st.session_state`) em um fluxo governado por quatro agentes especializados:

```text
Entrada (Usuário) → [Agente Diagnóstico] → [Base RAG] → [Agente Recomendador] → [Agente Gerador] → [Agente Avaliador] → Saída (Interface e Logs JSON)
```

### 3.3 Decisão

A lógica de decisão orquestrada pelo LangChain baseia-se em *System Prompts* rigorosos. O Agente Recomendador "pensa" consultando o banco vetorial (ChromaDB) para entender as prioridades da banca. Ele é instruído a não alucinar ordens de estudo (ex: exigir o estudo de armazenamento HDFS antes do processamento com Apache Spark). Os agentes são forçados a formatar suas avaliações estritamente em JSON, permitindo que a aplicação faça o *parsing* estruturado para renderizar a interface e tomar decisões de roteamento da máquina de estados.

### 3.4 Saída (Output)

A saída ocorre em duas frentes:
1. **Visual (Front-end):** Trilha de estudos interativa na barra lateral, *feedbacks* pedagógicos estruturados (✅ Correto / ❌ Incorreto) e explicações detalhadas (Explicabilidade).
2. **Dados (Back-end):** Um arquivo JSON salvo no diretório `logs/` no encerramento da sessão, contendo a auditoria completa da performance do usuário para rastreabilidade.

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.12 | Linguagem principal do projeto. |
| LangChain | 1.2.13 | Orquestração de prompts, chains e abstração do modelo de linguagem. |
| Google Gemini API | 1.69.0 | LLM para inferência lógica e geração (modelo `gemini-2.5-flash-lite`). |
| ChromaDB | 1.5.5 | Banco de dados vetorial para armazenar os embeddings do RAG. |
| Streamlit | 1.55.0 | Construção da interface web interativa e gerenciamento de estado. |

### 4.2 Estrutura do código

```text
projeto-1/
├── data/
│   ├── chroma_db/     # Banco de dados vetorial persistido
├── docs/
│   ├── documento-engenharia.md
│   └── relatorio-entrega.md
├── logs/              # Arquivos JSON de auditoria gerados por sessão
├── src/
│   ├── __init__.py
│   ├── agents.py      # Lógica de LLMs, Prompts e Parsing de JSON
│   ├── main.py        # Interface Streamlit e orquestração de telas
│   └── rag.py         # Ingestão de dados e busca vetorial
├── .env.example
├── .gitignore
└── requirements.txt
```

### 4.3 Como executar

Instruções passo a passo para rodar o projeto localmente:

```bash
# 1. Instalar dependências congeladas
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente na raiz do projeto (arquivo .env)
# Crie um arquivo .env e adicione sua chave de API
GEMINI_API_KEY=sua_chave_aqui

# 3. Executar a aplicação Web
streamlit run src/main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| **Resiliência de Parsing JSON** | Taxa de sucesso na extração de JSON das respostas do LLM (tratamento de sujeira Markdown). | 100% de recuperação após implementação de higienização de string e blocos `try-except`. |
| **Aderência de Formato da Banca** | Capacidade de formatar a questão conforme exigência da banca (Múltipla escolha vs Certo/Errado). | Alta assertividade após inserção de ordem explícita no *prompt* gerador. |
| **Rastreabilidade** | Capacidade de salvar a sessão sem perdas para auditoria do nível. | Sucesso na exportação do dicionário da sessão para a pasta `logs/`. |
| **Explicabilidade** | O agente fornece o motivo para as recomendações de trilha de estudo. | 100% das recomendações são acompanhadas de justificativa legível. |

### 5.2 Exemplos de teste

#### Teste 1: Validação de Formato e Geração de Questão (Banca FCC)

- **Entrada:** Configuração de "Redes de Computadores" para a banca FCC, seguida do comando "praticar".
- **Saída esperada:** Questão sobre o tópico atual contendo 5 alternativas (A, B, C, D, E) acopladas ao enunciado.
- **Saída obtida:** O Agente gerou uma questão sobre o Modelo OSI e TCP/IP, incluindo as 5 alternativas perfeitamente integradas no campo do enunciado em JSON.
- **Resultado:** Sucesso.

#### Teste 2: Avaliação de Resposta Incorreta e Identificação de Lacunas

- **Entrada:** Diante de uma questão gerada sobre Hadoop e HDFS, o usuário envia uma resposta absurdamente errada ("Integração contínua é quando o código só é integrado uma vez por ano").
- **Saída esperada:** O Agente detecta o erro estrutural, devolve "Incorreto", aponta a justificativa técnica com base no ecossistema Big Data e registra a lacuna no log.
- **Saída obtida:** O Agente retornou a correção técnica, justificou o conceito correto de HDFS e preencheu o campo `lacuna` de aprendizado na memória e na tela.
- **Resultado:** Sucesso.

### 5.3 Análise dos resultados

Os resultados demonstraram que o agente atingiu plenamente o objetivo de atuar como tutor, indo além de um simples chatbot. O RAG conseguiu ancorar o conhecimento e isolar alucinações de temas complexos de TI (como Kubernetes e Apache Spark). 

O ponto forte do sistema é a sua robustez arquitetural: quando esbarrou no limite de cotas do modelo padrão (`RESOURCE_EXHAUSTED` do Gemini 2.5 Flash), a arquitetura permitiu o *hot-swap* para o modelo `gemini-2.5-flash-lite` no arquivo de configuração dos agentes sem alterar a interface, mantendo a operação. Um ponto de melhoria identificado foi a teimosia dos LLMs em envelopar outputs estruturados (JSON) em blocos de Markdown, o que exigiu o desenvolvimento de um "limpador" programático em Python.

---

## 6. Diferenciais implementados

- [x] RAG com base externa (ChromaDB persistente)
- [x] Múltiplos agentes (Diagnóstico, Recomendador, Gerador, Avaliador)
- [ ] Uso de ferramentas (tools)
- [x] Memória persistente (Salva histórico da sessão em JSON na pasta `logs/`)
- [x] Explicabilidade (Trilha de estudos justificada item a item)
- [x] Análise crítica de limitações (Discussão sobre cotas de API e formatos de saída do LLM)

---

## 7. Limitações e Trabalhos Futuros

**Limitações encontradas:**
1. **Cotas de API:** O volume de chamadas simultâneas (orquestração da máquina de estados) consome rapidamente o *Free Tier* de modelos avançados, exigindo *fallback* para versões mais leves (Lite) durante testes intensivos.
2. **Parsing Rigoroso:** O acoplamento de outputs JSON exigiu *try-excepts* para prevenir a quebra do Streamlit quando o modelo insere textos fora do formato.

**Trabalhos Futuros:**
Ativar o módulo `ingest_pdf` (já existente no backend) diretamente na interface web, permitindo que o candidato faça o *upload* de um edital em PDF na tela do Streamlit. Isso parametrizaria o agente para aquele concurso específico de forma totalmente dinâmica.

---

## 8. Referências

1. LangChain Documentation. *LLM Chain and Prompt Templates*. Disponível em: [https://docs.langchain.com](https://docs.langchain.com).
2. Google for Developers. *Gemini API: Text Generation and Structured Output*. Disponível em: [https://ai.google.dev/docs](https://ai.google.dev/docs).
3. ChromaDB Documentation. *Getting Started with Persistent Vector Databases*. Disponível em: [https://docs.trychroma.com](https://docs.trychroma.com).
4. Streamlit Documentation. *Session State and Callbacks*. Disponível em: [https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state).

---

## 9. Checklist de entrega

- [X] Documento de engenharia preenchido
- [X] Código funcional no repositório
- [X] Relatório de entrega preenchido
- [X] Pull Request aberto