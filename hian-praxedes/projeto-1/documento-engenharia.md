# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Hian Praxedes de Souza Oliveira <br>
> **Matrícula:** 200019520 <br>
> **Domínio:** Educação <br>
> **Função do agente:** Resumo <br>
> **Restrição obrigatória:** Baixo custo

---

## 1. Problema e Contexto

No domínio da educação, estudantes frequentemente precisam lidar com materiais extensos, densos e técnicos, como apostilas, artigos, capítulos de livros e slides de aula em formato PDF. Esse volume de informação torna o processo de revisão mais demorado e dificulta a identificação rápida dos conceitos centrais.

O problema abordado neste projeto é a necessidade de apoiar estudantes na compreensão e revisão de materiais didáticos de forma mais rápida e objetiva. Para isso, foi projetado um agente de IA capaz de ler arquivos PDF contendo conteúdo educacional, extrair o texto e gerar um resumo estruturado com foco em utilidade para estudo.

O público-alvo principal são estudantes de graduação e cursos técnicos que precisam revisar conteúdos com frequência. A relevância do problema está no ganho de produtividade, na redução do esforço de leitura inicial e no apoio à organização do estudo. A solução foi projetada com foco em baixo custo, utilizando uma arquitetura simples e direta, sem componentes complexos ou dependência de múltiplos serviços externos.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Estudante | Usuário principal do sistema | Obter resumos rápidos e úteis de materiais de estudo |
| Professor | Indica ou acompanha o uso da ferramenta | Apoiar a revisão de conteúdos pelos alunos |
| Desenvolvedor | Implementa e mantém o sistema | Garantir funcionamento, simplicidade e evolução do projeto |
| Avaliador da disciplina | Analisa a entrega do projeto | Verificar requisitos, arquitetura, implementação e avaliação |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O sistema deve receber como entrada um arquivo PDF contendo material didático. | Alta |
| RF02 | O sistema deve extrair o texto do arquivo PDF informado pelo usuário. | Alta |
| RF03 | O sistema deve validar se o texto extraído possui conteúdo suficiente para resumo. | Alta |
| RF04 | O sistema deve enviar o conteúdo processado para um modelo de linguagem. | Alta |
| RF05 | O sistema deve gerar um resumo geral do conteúdo do PDF. | Alta |
| RF06 | O sistema deve listar os principais pontos abordados no material. | Alta |
| RF07 | O sistema deve extrair palavras-chave relevantes para estudo. | Média |
| RF08 | O sistema deve apresentar uma sugestão de revisão com base no conteúdo resumido. | Média |
| RF09 | O sistema deve permitir a execução de testes com múltiplos arquivos PDF. | Média |
| RF10 | O sistema deve registrar os resultados dos testes em arquivo Markdown. | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O sistema deve possuir baixo custo de execução por requisição. | Custo |
| RNF02 | O sistema deve utilizar arquitetura simples e de fácil manutenção. | Manutenibilidade |
| RNF03 | O sistema deve responder em tempo adequado para arquivos curtos e médios. | Desempenho |
| RNF04 | O sistema deve ser executável localmente em ambiente Python. | Portabilidade |
| RNF05 | O sistema deve apresentar saída clara, legível e organizada. | Usabilidade |
| RNF06 | O sistema deve minimizar uso de recursos e chamadas desnecessárias ao modelo. | Eficiência |
| RNF07 | O sistema deve tratar erros básicos, como arquivo inexistente ou PDF sem texto extraível. | Confiabilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Resumir material didático em PDF

- **Ator:** Estudante
- **Pré-condição:** O usuário possui um arquivo PDF com texto extraível e o ambiente está configurado.
- **Fluxo principal:**
  1. O estudante executa o programa.
  2. O estudante informa o caminho de um arquivo PDF.
  3. O sistema extrai o texto do arquivo.
  4. O sistema valida e pré-processa o conteúdo.
  5. O sistema envia o texto para o modelo Gemini.
  6. O sistema retorna um resumo estruturado ao usuário.
- **Pós-condição:** O usuário visualiza o resumo do material informado.

### Caso de uso 2: Executar testes em múltiplos PDFs

- **Ator:** Desenvolvedor
- **Pré-condição:** Existem arquivos PDF na pasta de testes do projeto.
- **Fluxo principal:**
  1. O desenvolvedor executa o script de avaliação.
  2. O sistema percorre os PDFs da pasta configurada.
  3. O sistema extrai o texto de cada arquivo.
  4. O sistema gera os resumos para cada PDF.
  5. O sistema salva os resultados em um arquivo Markdown.
- **Pós-condição:** Os resultados dos testes ficam registrados para análise posterior.

### Caso de uso 3: Validar erro de entrada

- **Ator:** Usuário
- **Pré-condição:** O usuário informa um caminho inválido, um arquivo não PDF ou um PDF sem texto extraível.
- **Fluxo principal:**
  1. O usuário informa o caminho do arquivo.
  2. O sistema verifica a existência e o tipo do arquivo.
  3. O sistema tenta extrair o texto.
  4. O sistema identifica o erro e retorna uma mensagem apropriada.
- **Pós-condição:** O usuário recebe feedback claro sobre a falha.

---

## 6. Fluxo do Agente

O fluxo do agente ocorre de forma sequencial:

1. O usuário informa o caminho de um arquivo PDF.
2. O sistema verifica se o arquivo existe e se possui extensão `.pdf`.
3. O módulo de leitura de PDF extrai o texto do documento.
4. O texto é validado e pré-processado.
5. Um prompt estruturado é montado com instruções para o modelo.
6. O modelo Gemini gera a resposta.
7. O sistema pós-processa a saída.
8. O usuário recebe:
   - resumo geral
   - principais pontos
   - palavras-chave
   - sugestão de revisão

```text
PDF → Extração de texto → Validação → Pré-processamento → Prompt → Gemini → Pós-processamento → Saída
```

---

## 7. Arquitetura do Sistema

A arquitetura escolhida foi um **pipeline sequencial**, com foco em simplicidade, clareza e baixo custo.

- **Tipo de agente:** pipeline sequencial
- **LLM utilizado:** Gemini
- **Componentes principais:**
  - [x] Módulo de entrada
  - [x] Processamento / LLM
  - [ ] Ferramentas externas (tools)
  - [ ] Memória
  - [x] Módulo de saída

### Descrição da arquitetura

O sistema é composto pelos seguintes módulos:

1. **Módulo de entrada**
   - recebe o caminho do arquivo PDF informado pelo usuário.

2. **Módulo de leitura de PDF**
   - usa biblioteca Python para extrair texto do documento.

3. **Módulo de validação e pré-processamento**
   - verifica se há conteúdo suficiente e limpa ruídos básicos do texto.

4. **Módulo de orquestração do prompt**
   - estrutura a instrução enviada ao modelo, definindo o formato da resposta.

5. **Módulo LLM**
   - utiliza o Gemini para gerar o resumo e os demais elementos da saída.

6. **Módulo de saída**
   - apresenta o resultado ao usuário em formato organizado.

A decisão por essa arquitetura foi motivada pela restrição obrigatória de **baixo custo**. Por isso, não foram adotados mecanismos mais complexos como RAG, múltiplos agentes, memória persistente ou bases vetoriais.

### Diagrama de arquitetura

```mermaid
flowchart LR
    A[Usuário] --> B[Entrada do PDF]
    B --> C[Leitura e extração de texto]
    C --> D[Validação e pré-processamento]
    D --> E[Montagem do prompt]
    E --> F[Gemini]
    F --> G[Pós-processamento]
    G --> H[Resumo final]
```

---

## 8. Estratégia de Avaliação

O agente foi avaliado com base em critérios qualitativos e operacionais.

- **Métricas definidas:**
  - fidelidade ao texto original
  - clareza do resumo
  - organização da resposta
  - utilidade para revisão
  - custo reduzido de execução
  - tempo de resposta

- **Conjunto de testes:**
  - múltiplos exemplos de materiais didáticos em PDF
  - textos educacionais curtos e médios
  - casos normais e casos de erro de entrada

- **Método de avaliação:**
  - avaliação manual das respostas geradas
  - comparação entre o conteúdo original e os principais pontos destacados
  - verificação da estrutura de saída produzida pelo agente

---

## 9. Referências

1. Documentação oficial do Google Gemini API.
2. Documentação da biblioteca `pypdf`.
3. Materiais da disciplina de Sistemas de Machine Learning.
4. Documentação do Python e bibliotecas utilizadas no projeto.
