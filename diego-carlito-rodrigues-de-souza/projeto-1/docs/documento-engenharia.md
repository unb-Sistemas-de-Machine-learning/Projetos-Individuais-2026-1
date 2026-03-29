# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Diego Carlito Rodrigues de Souza
> **Matrícula:** 221007690
> **Domínio:** Educação 
> **Função do agente:** Recomendação 
> **Restrição obrigatória:** Explicabilidade obrigatória 

---

## 1. Problema e Contexto

A preparação para concursos públicos de Tecnologia da Informação (TI) é um processo longo, complexo e altamente individualizado. Candidatos precisam dominar dezenas de matérias — como Redes de Computadores, Banco de Dados, Segurança da Informação, Sistemas Operacionais e Legislação — enquanto adaptam seus estudos ao perfil específico de cada banca examinadora (CESPE, FCC, FGV, VUNESP, entre outras). 

O principal problema enfrentado pelos candidatos é a falta de orientação personalizada: sem saber exatamente quais tópicos priorizar, qual é seu nível atual e por que certa ordem de estudo é recomendada, muitos desperdiçam tempo estudando assuntos de baixa incidência ou pulam pré-requisitos fundamentais. 

Este projeto propõe um Agente Tutor de Concursos de TI, que diagnostica o nível do candidato, recomenda uma trilha de estudos personalizada e gera questões no estilo da banca alvo — sempre com explicabilidade total, ou seja, justificando cada recomendação e decisão tomada.

**Público-alvo:**
* Candidatos a concursos de TI (analista, técnico, perito etc.).
* Estudantes em qualquer nível de preparação: iniciante a avançado.
* Candidatos focados em bancas específicas (CESPE, FCC, FGV etc.).

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|---|---|---|
| Candidato a concurso | Usuário principal | Receber recomendações personalizadas e explicadas, economizar tempo de estudo |
| Professor / Mentor | Usuário secundário | Usar o agente como ferramenta de apoio pedagógico |
| Desenvolvedor / Aluno | Criador e mantenedor | Implementar, avaliar e evoluir o sistema |
| Banca examinadora (indireta) | Fonte de dados | Seus editais e questões alimentam a base de conhecimento do agente |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|---|---|---|
| RF01 | O agente deve receber como entrada o concurso alvo e a matéria de interesse do candidato. | Alta |
| RF02 | O agente deve aplicar 2 a 3 questões diagnósticas para avaliar o nível atual do candidato. | Alta |
| RF03 | O agente deve recomendar uma trilha de estudos ordenada por pré-requisitos e incidência em provas. | Alta |
| RF04 | Cada recomendação deve ser acompanhada de uma justificativa explícita (ex: 'Estude TCP/IP antes de VPN porque...'). | Alta |
| RF05 | O agente deve gerar questões no estilo da banca informada pelo candidato. | Alta |
| RF06 | O agente deve avaliar as respostas do candidato, identificar lacunas e atualizar a trilha de estudos. | Alta |
| RF07 | O agente deve buscar na base de conhecimento (RAG) questões e conteúdos relevantes para o tópico em estudo. | Média |
| RF08 | O agente deve exibir, ao final de cada sessão, um resumo do desempenho e próximos passos recomendados. | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|---|---|---|
| RNF01 | Toda recomendação, geração de questão e avaliação deve incluir justificativa legível ao usuário. | Explicabilidade |
| RNF02 | O tempo de resposta do agente deve ser inferior a 15 segundos por interação. | Desempenho |
| RNF03 | O sistema deve funcionar com custo de API inferior a R$ 0,10 por sessão completa. | Custo |
| RNF04 | O código deve ser modular, com cada agente em um arquivo separado. | Manutenibilidade |
| RNF05 | O sistema deve logar todas as interações para permitir auditoria e análise de qualidade. | Rastreabilidade |
| RNF06 | A base de conhecimento deve ser facilmente expansível com novos editais e questões. | Escalabilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Diagnóstico de nível do candidato

* **Ator:** Candidato a concurso
* **Pré-condição:** Candidato informa concurso alvo (ex: SEFAZ-SP) e matéria (ex: Banco de Dados)
* **Fluxo principal:**
  1. Agente Diagnóstico seleciona 3 questões de dificuldade progressiva na base RAG.
  2. Candidato responde cada questão.
  3. Agente avalia as respostas e classifica o nível: Iniciante / Intermediário / Avançado.
  4. Classificação é passada ao Agente Recomendador.
* **Pós-condição:** Nível do candidato identificado e trilha de estudos gerada.

### Caso de uso 2: Geração de questão e avaliação

* **Ator:** Candidato a concurso
* **Pré-condição:** Candidato está em um tópico da trilha de estudos
* **Fluxo principal:**
  1. Candidato solicita uma questão de prática.
  2. Agente Gerador cria questão no estilo CESPE/FCC/FGV com base em exemplos do RAG.
  3. Candidato responde.
  4. Agente Avaliador corrige, explica o gabarito e aponta a lacuna de conhecimento.
  5. Agente atualiza a trilha se necessário.
* **Pós-condição:** Candidato recebe feedback detalhado e trilha de estudos é ajustada.

### Caso de uso 3: Consulta de justificativa

* **Ator:** Candidato a concurso
* **Pré-condição:** Agente emitiu uma recomendação de estudo
* **Fluxo principal:**
  1. Candidato pergunta 'por que devo estudar este tópico agora?'.
  2. Agente recupera o contexto da trilha e gera explicação baseada em pré-requisitos e incidência em provas.
  3. Agente cita as questões na base que justificam a incidência.
* **Pós-condição:** Candidato compreende a lógica da recomendação.

---

## 6. Fluxo do Agente

O agente opera em um pipeline multi-etapa com quatro sub-agentes especializados:

```text
Usuário (concurso + matéria) 
↓ 
[Agente Diagnóstico] → aplica 2-3 questões → classifica nível 
↓ 
[RAG — Base de Conhecimento] → editais, questões, resumos por banca 
↓ 
[Agente Recomendador] → gera trilha ordenada + justificativa explícita 
↓ 
[Agente Gerador de Questões] → questão no estilo da banca alvo 
↓ 
[Agente Avaliador] → corrige, explica, identifica lacuna, atualiza trilha 
↓ 
Usuário (feedback + próximos passos) 
```

**Descrição de cada etapa:**
* **Agente Diagnóstico:** recebe o input do usuário, consulta o RAG e seleciona questões calibradas para medir o nível.
* **Base RAG (ChromaDB):** armazena vetorialmente editais, questões anteriores e resumos de matérias por banca.
* **Agente Recomendador:** com base no nível identificado e nos dados do RAG, gera trilha de tópicos ordenada por pré-requisito e frequência de cobrança, com justificativa para cada item.
* **Agente Gerador:** cria questões inéditas no estilo da banca alvo, usando exemplos do RAG como referência.
* **Agente Avaliador:** corrige a resposta, explica o raciocínio, identifica o gap de conhecimento e decide se a trilha deve ser ajustada.

---

## 7. Arquitetura do Sistema

* **Tipo de agente:**
  * RAG (Retrieval-Augmented Generation): a base de conhecimento é consultada a cada etapa para fundamentar as respostas.
  * Tool-using: a busca no RAG é implementada como uma ferramenta (tool) chamada pelo LLM.
  * Multi-agente com pipeline sequencial: quatro agentes com responsabilidades distintas e comunicação via memória compartilhada.
* **LLM utilizado:** Google Gemini 1.5 Flash (via API do Google AI Studio).
* **Componentes principais:**
  * [x] Módulo de entrada: recebe e valida os dados do candidato (concurso, matéria, nível).
  * [x] Processamento / LLM: quatro instâncias especializadas do LLM com prompts distintos.
  * [x] Ferramentas externas (tools): busca semântica no ChromaDB para recuperar questões e conteúdos relevantes.
  * [x] Memória: contexto acumulado (nível, respostas, trilha) passado entre os agentes.
  * [x] Módulo de saída: formata e exibe recomendações, questões e feedbacks com justificativas.

**Tabela de Tecnologias:**

| Componente | Tecnologia | Função |
|---|---|---|
| Linguagem | Python 3.11+ | Linguagem principal de implementação |
| Orquestração de agentes | LangChain | Gerenciar o pipeline multi-agente e o fluxo de memória |
| LLM | Google Gemini 1.5 Flash | Motor de linguagem para todos os agentes |
| Banco vetorial (RAG) | ChromaDB | Armazenar e recuperar questões e conteúdos por similaridade semântica |
| Leitura de PDFs | PyPDF2 / pdfplumber | Ingestão de editais e apostilas em PDF para a base RAG |
| Interface | Streamlit | Aplicação web interativa para visualização do chat e formatação de dados (Markdown) |
| Logs / Rastreabilidade | Python logging + JSON | Registrar todas as interações para auditoria |

---

## 8. Estratégia de Avaliação

**Métricas definidas:**

| Métrica | Descrição | Meta |
|---|---|---|
| Precisão do diagnóstico | O nível identificado corresponde ao nível real do candidato (avaliação manual) | ≥ 80% |
| Relevância da trilha | Os tópicos recomendados aparecem no edital do concurso alvo | ≥ 90% |
| Qualidade das questões | Questão gerada é coerente, tem gabarito correto e imita o estilo da banca | ≥ 85% |
| Explicabilidade | Cada recomendação possui justificativa compreensível (avaliação subjetiva) | 100% das saídas |
| Latência | Tempo de resposta por interação | < 15 segundos |
| Custo por sessão | Tokens consumidos por sessão completa | R$ 0,00 (Free Tier Google AI Studio) |

**Conjunto de testes:**
* Mínimo de 10 cenários de teste cobrindo diferentes concursos (SEFAZ, TRF, Receita Federal), matérias (Redes, BD, SO, Segurança) e níveis (iniciante, intermediário, avançado).
* Avaliação manual pelo próprio desenvolvedor como candidato real, comparando as recomendações com materiais de referência do mercado.
* Registro de todas as interações em JSON para análise posterior.

**Método de avaliação:**
* Manual: verificação da coerência das recomendações e questões geradas.
* Automático: validação de latência e custo via logs.
* Comparativo: comparação da trilha gerada com cronogramas de cursos preparatórios de referência (Estratégia Concursos, Gran Cursos).

---

## 9. Referências

1. LangChain Documentation. Disponível em: [https://docs.langchain.com](https://docs.langchain.com).
2. ChromaDB Documentation. Disponível em: [https://docs.trychroma.com](https://docs.trychroma.com).
3. Google Gemini API Documentation. Disponível em: [https://ai.google.dev/docs](https://ai.google.dev/docs).
4. CÓDIGO FONTE TV. RAG (Retrieval-Augmented Generation) // Dicionário do Programador. YouTube, 17 out. 2024. Disponível em: https://www.youtube.com/watch?v=CuPKOGdA46Q. Acesso em: 28 mar. 2026.
5. ALVES, Isaque et al. Practices for Managing Machine Learning Products: a Multivocal Literature Review. Disponível em: [https://www.academia.edu/105083380/Practices_for_Managing_Machine_Learning_Products_a_Multivocal_Literature_Review](https://www.academia.edu/105083380/Practices_for_Managing_Machine_Learning_Products_a_Multivocal_Literature_Review).
