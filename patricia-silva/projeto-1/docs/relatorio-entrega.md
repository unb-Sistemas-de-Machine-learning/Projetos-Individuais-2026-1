# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Patricia Helena Macedo da Silva  
> **Matrícula:** 221037993
> **Data de entrega:** 30/03/2026  

---

## 1. Resumo do Projeto

Foi implementado um **agente de recomendação de estudo** no domínio da educação, com **explicabilidade obrigatória**: cada sugestão inclui justificativa ligada ao objetivo, nível e tempo informados pelo usuário. O protótipo combina **RAG leve** (recuperação TF-IDF sobre ficheiros Markdown locais em `data/kb/`) com um **LLM** (Google **Gemini** com saída JSON, por padrão `gemini-2.5-flash` (com fallbacks se o ID não existir na API), ou Ollama local). A saída é validada por **Pydantic**, reforçando o requisito de campos de explicabilidade. O principal resultado é um fluxo reproduzível via CLI que entrega um plano priorizado e transparente, além de testes automatizados para recuperação e schema.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Educação [2] |
| **Função do agente** | Recomendação [2] |
| **Restrição obrigatória** | Explicabilidade obrigatória [4] |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

Parâmetros textuais: **objetivo** de aprendizagem (obrigatório), **nível** (iniciante/intermediário/avançado), **horas por semana**, e **restrições ou preferências** opcionais. A entrada é normalizada em `EntradaUsuario` e convertida em consulta para o recuperador e em bloco de perfil para o prompt.

### 3.2 Processamento (Pipeline)

```
Entrada (CLI) → EntradaUsuario → consulta textual
    → RAG (TF-IDF, top-k trechos de data/kb/*.md)
    → montagem do prompt (perfil + contexto recuperado)
    → LLM (JSON) → validação Pydantic (AgenteSaida) → saída
```

### 3.3 Decisão

O “raciocínio” combina **recuperação** (quais trechos da base local são mais similares à consulta) e **geração condicionada** pelo prompt de sistema, que obriga justificativas e formato JSON. Em caso de falha de validação, há **nova tentativa** com o erro embutido no prompt (`agent.gerar_plano`).

### 3.4 Saída (Output)

JSON com: `resumo_perfil`, lista `recomendacoes` (cada item: `titulo`, `tipo`, `descricao`, `justificativa`, `passos`), e `avisos_ou_limitacoes`. A explicabilidade está no campo `justificativa` e nos avisos explícitos sobre limitações.

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.11+ (testado em 3.13) | Linguagem principal |
| google-generativeai | ≥0.8 | Gemini com `response_mime_type=application/json` |
| scikit-learn | ≥1.3 | TF-IDF e similaridade para RAG leve |
| Pydantic | ≥2.0 | Validação da saída estruturada |
| httpx | ≥0.27 | Cliente HTTP para API do Ollama |
| pytest | ≥8.0 | Testes automatizados |

### 4.2 Estrutura do código

```
projeto-1/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── retrieval.py
│   ├── agent.py
│   └── pipeline.py
├── data/
│   └── kb/
│       ├── metodos_estudo.md
│       ├── planejamento_tempo.md
│       └── recursos_tipos.md
├── tests/
│   ├── test_retrieval.py
│   └── test_schemas.py
├── docs/
│   ├── documento-engenharia.md
│   ├── relatorio-entrega.md
│   └── diagrama_arquitetura.png
├── requirements.txt
├── .env.example
└── README.md
```

### 4.3 Como executar

**PowerShell (Windows):**

```powershell
cd patricia-silva\projeto-1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edite .env: defina GEMINI_API_KEY ou deixe vazio e use Ollama

python -m src.main --objetivo "Aprender Python para dados" --nivel iniciante --horas 5h --restricoes "Sem vídeo longo"
```

**Linux/macOS:**

```bash
cd patricia-silva/projeto-1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export GEMINI_API_KEY=...   # ou use Ollama sem chave

python -m src.main --objetivo "Aprender Python para dados" --nivel iniciante --horas 5h
```

Testes:

```bash
python -m pytest tests/ -v
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Testes automatizados | Regressão em KB, retriever e schema | 3/3 passando (execução local) |
| Explicabilidade estrutural | Schema exige `justificativa` mínima | Garantido por Pydantic |
| Relevância / utilidade | Avaliação humana sugerida | A preencher após revisão manual de 2–3 cenários |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:** `python -m src.main --objetivo "Aprender Inglês para conversação" --nivel intermediário --horas 8h --restricoes "sem aulas longas; preferencia por pratica"`

- **Saída esperada:**
  - JSON ou saída de texto com 2-6 recomendações de estudo personalizadas, cada uma com título, tipo, descrição, justificativa e passos. A justificativa deve mencionar objetivo, nível e tempo (explicabilidade obrigatória).

- **Saída obtida:**

```text
O aluno é um estudante de nível intermediário de inglês, com o objetivo principal de melhorar a conversação. Possui 8 horas semanais para dedicar aos estudos e prefere atividades práticas e sessões de estudo curtas, evitando aulas longas.

1. [Prática] Prática de Conversação Direta (Curta e Frequente)
   Engaje-se em sessões de conversação curtas (15-30 minutos) com falantes nativos ou outros estudantes de inglês. Utilize aplicativos de intercâmbio de idiomas ou participe de grupos de conversação online.
   Por quê: Esta atividade é diretamente alinhada ao objetivo de 'aprender Inglês para conversação', aproveita o nível 'intermediário' para aplicação prática e atende à 'preferência por prática' e à restrição de 'sem aulas longas'.
   1) Dedique 2-3 horas por semana, divididas em sessões de 20-30 minutos.
   2) Use plataformas como Tandem, HelloTalk ou encontre grupos de conversação online.
   3) Prepare tópicos de conversa ou perguntas para iniciar o diálogo.
   4) Não tenha medo de cometer erros; o foco é a fluência e a comunicação.

2. [Estudo e Prática] Imersão Ativa com Mídia (Foco na Escuta e Repetição)
   Assista a séries, filmes, vídeos curtos ou ouça podcasts em inglês. O foco deve ser na compreensão ativa e na repetição de frases e expressões que chamem sua atenção.
   Por quê: Essencial para desenvolver a compreensão auditiva e a familiaridade com o ritmo e a entonação da fala natural, crucial para o objetivo de 'conversação', e pode ser fragmentado em sessões curtas, respeitando a 'restrição de aulas longas'.


   1) Dedique 2 horas por semana, em blocos de 30-45 minutos.
   2) Escolha conteúdo que você goste (séries, podcasts, vídeos do YouTube).
   3) Comece com legendas em inglês e, gradualmente, tente assistir sem elas.
   4) Pause e repita frases ou diálogos que achar interessantes para praticar a pronúncia e a entonação.

3. [Estudo e Prática] Expansão de Vocabulário e Expressões (Contextualizada)
   Concentre-se na aquisição de vocabulário contextual e expressões idiomáticas comuns, que são essenciais para uma conversação mais rica e natural. Use a 'prática recuperativa' para fixar novas palavras.
   Por quê: Para um aluno 'intermediário', a aquisição de vocabulário e expressões idiomáticas é fundamental para enriquecer a 'conversação' e torná-la mais autêntica. A 'prática recuperativa' é útil aqui para fixar as novas palavras.
   1) Dedique 1 hora por semana, em sessões de 15-20 minutos.
   2) Anote palavras e frases novas que encontrar em mídias ou conversas.
   3) Crie flashcards (físicos ou digitais) e revise-os regularmente, tentando lembrar o significado e o uso sem olhar (prática recuperativa).
   4) Tente usar as novas palavras e expressões em suas sessões de conversação ou escrita.

4. [Prática] Autoavaliação da Fala (Gravação e Análise)
   Grave-se falando sobre tópicos do dia a dia ou respondendo a perguntas. Depois, ouça a gravação para identificar pontos de melhoria na pronúncia, fluência e gramática.
   Por quê: Esta prática ativa é excelente para o nível 'intermediário' e para o objetivo de 'conversação', permitindo identificar erros e melhorar a fluência de forma autônoma e em sessões curtas, alinhando-se à 'preferência por prática'.
   1) Dedique 1 hora por semana, em sessões de 10-15 minutos.
   2) Escolha um tópico simples (seu dia, um hobby, um filme que assistiu).
   3) Grave-se falando por 2-5 minutos.
   4) Ouça a gravação e anote 1-2 pontos específicos para melhorar na próxima vez (ex: 'r' enrolado, pausa excessiva, erro de concordância).

5. [Estudo e Prática] Escrita Curta e Reflexiva (Diário ou Resumos)
   Escreva pequenos textos em inglês, como um diário pessoal, resumos de algo que leu ou ouviu, ou respostas a perguntas. Isso ajuda a solidificar a gramática e o vocabulário.        
   Por quê: Embora o foco seja 'conversação', a escrita regular em inglês solidifica a gramática e o vocabulário, que são pilares para uma fala mais estruturada e confiante, e pode ser feita em sessões curtas, alinhando-se à 'restrição de aulas longas'.
   1) Dedique 1 hora por semana, em sessões de 10-15 minutos.
   2) Escreva sobre seu dia, seus pensamentos, ou resuma um artigo/notícia que leu.
   3) Tente usar novas palavras e estruturas que aprendeu.
   4) Se possível, peça a um falante nativo ou professor para revisar seus textos ocasionalmente.

Avisos:
  - A consistência é mais importante que a intensidade. Tente manter a frequência das sessões curtas ao longo da semana.
  - Não se preocupe em ser perfeito. O objetivo principal é a comunicação e a fluência. Erros fazem parte do processo de aprendizagem.
  - Aproveite o tempo disponível para variar as atividades, mantendo o estudo dinâmico e interessante.
  
```
- **Resultado:** Sucesso

#### Teste 2 (validação de entrada obrigatória)

- **Entrada executada:**
  - `python -m src.main --objetivo "Aprender Inglês para conversação" --nivel intermediário --horas`

- **Saída esperada:**
  - O CLI deve sinalizar erro e indicar que o argumento `--horas` precisa de um valor, porque o campo é obrigatório.

- **Saída obtida:**
  ```text
  usage: main.py [-h] --objetivo OBJETIVO [--nivel NIVEL] [--horas HORAS] [--restricoes RESTRICOES] [--json]
  main.py: error: argument --horas: expected one argument


- **Resultado:** Sucesso (comportamento correto de validação de argumento ausente)

#### Teste 3 (execução de testes automatizados)

- **Entrada executada:**
  - `python -m pytest tests/ -v`

- **Saída esperada:**
  - Os testes devem passar sem erros, confirmando a funcionalidade de carga de KB, retriever e validação de schema.

- **Saída obtida:**
  ```text
  ================================================================================ test session starts ================================================================================
  platform win32 -- Python 3.13.1, pytest-9.0.2, pluggy-1.6.0 -- C:\path\to\project\.venv\Scripts\python.exe
  cachedir: .pytest_cache
  rootdir: C:\path\to\project
  plugins: anyio-4.13.0
  collected 3 items

  tests/test_retrieval.py::test_kb_nao_vazia PASSED                                                                                                                               [ 33%]
  tests/test_retrieval.py::test_retriever_ranqueia_repeticao PASSED                                                                                                               [ 66%]
  tests/test_schemas.py::test_schema_aceita_saida_minima PASSED                                                                                                                   [100%]

  =============================================================================== 3 passed in 1.71s ===============================================================================
  ```

- **Resultado:** Sucesso (todos os testes passaram, confirmando funcionalidade de KB, retriever e schema)

### 5.3 Análise dos resultados

O protótipo cumpre a restrição de **explicabilidade** por desenho (prompt + schema). A **relevância** depende do modelo e do conteúdo da KB local; a base é pequena e didática. Pontos fortes: pipeline claro, validação forte, testes sem LLM para componentes determinísticos. Pontos fracos: sem métricas automáticas de qualidade semântica; Ollama pode exigir mais iterações se o JSON vier malformado (Gemini com `application/json` tende a ser mais estável).

---

## 6. Diferenciais implementados

- [x] RAG com base externa *(base local em Markdown — conhecimento enriquecido fora do prompt fixo)*  
- [ ] Múltiplos agentes  
- [ ] Uso de ferramentas (tools)  
- [ ] Memória persistente  
- [x] Explicabilidade  
- [x] Análise crítica de limitações *(seção 5.3 e `avisos_ou_limitacoes`)*  

---

## 7. Limitações e Trabalhos Futuros

- KB pequena e estática; poderia expandir com curadoria ou ingestão de documentos oficiais.  
- RAG lexical não capta sinónimos complexos como embeddings; evolução natural: embeddings + vector store.  
- Sem autenticação nem armazenamento de histórico do usuário.  

---

## 8. Referências

1. Gemini API — https://ai.google.dev/gemini-api/docs  
2. Scikit-learn — TF-IDF — https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html  
3. Pydantic — https://docs.pydantic.dev/latest/  

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido  
- [x] Código funcional no repositório  
- [x] Relatório de entrega preenchido *(ajustar matrícula e exemplos 5.2 após execuções reais)*  
- [x] Pull Request aberto  
