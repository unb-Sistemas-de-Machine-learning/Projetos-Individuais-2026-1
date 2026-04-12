# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Leonardo Fernandes Padre
> **Matrícula:** 200067036
> **Data de entrega:** 28/03/2026

---

## 1. Resumo do Projeto

O projeto consiste na construção de um agente tutor inteligente capaz de auxiliar estudantes no aprendizado do conteúdo do livro *Modern Operating Systems* de Andrew Tanenbaum. O problema central é a dificuldade de estudar de forma ativa e adaptativa a partir de um livro técnico extenso escrito em inglês, sem supervisão humana.

O agente combina recuperação semântica de informação (RAG) com um modelo de linguagem de grande escala (LLM) via Groq API, operando inteiramente em português brasileiro. Ele suporta três modos de interação: resposta a perguntas sobre o conteúdo do livro, geração de resumos temáticos e aplicação de testes de múltipla escolha com feedback imediato.

O principal resultado obtido é um tutor funcional via terminal que adapta o nível de dificuldade das questões ao desempenho histórico do aluno, mantendo memória persistente entre sessões. O sistema processa o livro em chunks semânticos respeitando a estrutura de capítulos e seções, garantindo que o contexto recuperado seja coerente e relevante para cada consulta.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Educação / Sistemas Operacionais |
| **Função do agente** | Tutor adaptativo com RAG |
| **Restrição obrigatória** | Interação exclusivamente em português; fonte de conhecimento restrita ao livro fornecido |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe mensagens de texto em português brasileiro digitadas pelo usuário no terminal. As entradas podem ser de três naturezas:

- **Perguntas livres** sobre o conteúdo do livro (ex: "O que é um deadlock?")
- **Solicitações de resumo** sobre um tópico específico (ex: "Resuma escalonamento de processos")
- **Solicitações de teste** sobre um tópico (ex: "Me teste sobre memória virtual") seguidas das respostas do aluno (ex: "1-A 2-C 3-B")

### 3.2 Processamento (Pipeline)

O pipeline é dividido em duas fases: ingestão (executada uma única vez) e inferência (executada a cada interação).

**Fase de ingestão:**
```
PDF → Extração de texto (PyMuPDF) → Detecção de cabeçalhos tipográficos
    → Segmentação semântica por seção → Chunks com título e página
    → Embeddings multilíngues (SentenceTransformers) → Índice FAISS
```

**Fase de inferência:**
```
Mensagem do usuário → Detecção de intenção → Tradução da query PT→EN
                    → Busca vetorial FAISS (query PT + query EN)
                    → Re-ranking e seleção dos top-k chunks
                    → Montagem do prompt com contexto + perfil do aluno
                    → LLM Groq (LLaMA 3) → Resposta em português
                    → Atualização da memória do aluno (se for teste)
```

### 3.3 Decisão

O agente utiliza um roteador de intenção baseado em palavras-chave para classificar cada mensagem em um de quatro modos: `qa`, `resumo`, `teste` ou `resposta_teste`. O estado de teste pendente é mantido em memória de sessão, garantindo que a mensagem seguinte a um teste seja sempre interpretada como resposta.

O LLM é utilizado em três papéis distintos, cada um com um prompt de sistema especializado:

- **Q&A:** instruído a responder somente com base nos trechos recuperados, adaptando a linguagem ao nível do aluno
- **Resumo:** instruído a estruturar a resposta em introdução, pontos principais e conclusão
- **Geração de teste:** instruído a seguir um formato rígido com marcadores `QUESTÃO N`, `RESPOSTA_N` e `EXPLICAÇÃO_N`, permitindo que o gabarito seja extraído por regex antes de ser exibido ao aluno

O perfil do aluno (nível, taxa de acerto, tópicos fracos e fortes) é injetado no prompt de sistema em todas as chamadas, permitindo que o LLM adapte vocabulário e complexidade das respostas.

### 3.4 Saída (Output)

- **Modo Q&A:** texto dissertativo em português, fundamentado nos trechos do livro recuperados
- **Modo resumo:** texto estruturado com introdução, pontos principais e conclusão
- **Modo teste:** três questões de múltipla escolha em português, com quatro alternativas cada, seguidas de instrução de resposta
- **Modo feedback:** resultado questão a questão com ícone de acerto/erro, explicação dos erros, pontuação e nível atualizado do aluno

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.10+ | Linguagem principal |
| Groq API | — | Inferência LLM (LLaMA 3.3 70B) via nuvem |
| FAISS (`faiss-cpu`) | 1.8+ | Índice vetorial para busca semântica |
| SentenceTransformers | 3.x | Geração de embeddings multilíngues |
| PyMuPDF (`fitz`) | 1.24+ | Extração de texto e metadados tipográficos do PDF |
| python-dotenv | — | Gerenciamento de variáveis de ambiente |

### 4.2 Estrutura do código
```
project/
├── data/
│   └── PSPD_Tannenbaum.pdf       # livro-fonte (não versionado)
├── src/
│   ├── ingestion/
│   │   └── ingest.py             # pipeline PDF → chunks → FAISS
│   └── agent/
│       ├── agent.py              # RAGRetriever, TutorAgent, memória do aluno
│       └── interface.py          # CLI interativo
├── vector_store/                 # gerado automaticamente, não versionado
│   ├── index.faiss
│   ├── chunks.pkl
│   └── config.pkl
├── student_memory/               # gerado automaticamente, não versionado
│   └── student_profile.json
├── requirements.txt
├── .env                          # GROQ_API_KEY (não versionado)
└── main.py                       # ponto de entrada único
```

### 4.3 Como executar
```bash
# 1. Clonar o repositório e entrar na pasta
git clone 
cd project

# 2. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar a chave da API (obter em console.groq.com)
echo "GROQ_API_KEY=sua_chave_aqui" > .env

# 5. Adicionar o PDF do livro
cp /caminho/para/PSPD_Tannenbaum.pdf data/

# 6. Executar — o ingest roda automaticamente na primeira vez
python main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Corretude do roteamento | % de mensagens classificadas na intenção correta | Verificar manualmente com ao menos 10 entradas variadas |
| Relevância dos chunks | Score de similaridade coseno dos trechos recuperados (limiar > 0,2) | Monitorado em tempo de execução |
| Coerência da resposta | Resposta contém informação presente nos chunks recuperados | Avaliação qualitativa por inspeção |
| Integridade do teste | As 3 questões são exibidas completas e o gabarito é extraído corretamente | Verificar saída vs. gabarito interno |

### 5.2 Exemplos de teste

#### Teste 1 — Pergunta factual

- **Entrada:** `"O que é um deadlock?"`
- **Saída esperada:** Explicação em português sobre deadlock baseada no conteúdo do Tanenbaum, mencionando condições necessárias
- **Saída obtida:** Resposta coerente citando as quatro condições de Coffman (exclusão mútua, posse e espera, não-preempção, espera circular)
- **Resultado:** Sucesso

#### Teste 2 — Geração e avaliação de teste

- **Entrada:** `"Me teste sobre escalonamento de processos"`
- **Saída esperada:** 3 questões de múltipla escolha completas em português, sem gabarito visível
- **Saída obtida:** 3 questões exibidas corretamente; ao responder `"1-A 2-B 3-A"`, feedback individual por questão foi gerado com explicações
- **Resultado:** Sucesso

### 5.3 Análise dos resultados

O agente atingiu os objetivos principais: recupera trechos relevantes do livro, responde em português com base no conteúdo e adapta a dificuldade do teste ao nível do aluno. O chunking semântico por seção melhorou significativamente a coerência dos trechos recuperados em relação ao chunking por tamanho fixo.

O ponto mais fraco identificado é o roteador de intenção baseado em palavras-chave, que pode falhar em entradas ambíguas ou com vocabulário fora do esperado. A tradução automática da query PT→EN adiciona latência e uma chamada extra à API, o que pode ser limitante no plano gratuito do Groq.

---

## 6. Diferenciais implementados

- [x] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [x] Memória persistente
- [ ] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

**Limitações atuais:**

- O roteador de intenção é baseado em palavras-chave fixas, o que o torna frágil para entradas fora do padrão esperado. Uma alternativa seria usar o próprio LLM para classificar a intenção.
- O chunking semântico depende da qualidade tipográfica do PDF. PDFs com formatação irregular podem não ter os cabeçalhos detectados corretamente.
- Não há memória de conversa dentro da sessão: cada pergunta é tratada de forma isolada, sem considerar o histórico da conversa atual.
- O plano gratuito do Groq possui limite de requisições por minuto, o que pode causar erros em uso intensivo, especialmente com a chamada extra de tradução da query.

**Trabalhos futuros:**

- Substituir o roteador por classificação via LLM para maior robustez
- Adicionar histórico de conversa (janela das últimas N mensagens) no contexto do prompt
- Implementar interface web com Flask para maior acessibilidade
- Avaliar modelos de embedding específicos para português técnico
- Adicionar chunking por capítulo como nível hierárquico superior para resumos mais amplos

---

## 8. Referências

1. Tanenbaum, A. S. *Modern Operating Systems*. 4ª ed. Pearson, 2014.
2. Lewis, P. et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS, 2020.
3. Groq. *Groq API Documentation*. Disponível em: https://console.groq.com/docs

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
