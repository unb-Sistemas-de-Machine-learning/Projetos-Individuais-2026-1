# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Hian Praxedes de Souza Oliveira <br>
> **Matrícula:** 200019520<br>
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

Este projeto apresenta um agente de IA voltado ao domínio da educação, com a função de resumir materiais didáticos em PDF para apoiar estudantes na revisão de conteúdo. O sistema recebe como entrada um arquivo PDF, extrai seu texto, processa esse conteúdo por meio de um pipeline sequencial e utiliza o modelo Gemini para gerar uma saída estruturada. A resposta inclui resumo geral, principais pontos, palavras-chave e sugestão de revisão. O principal objetivo foi construir uma solução funcional, simples e de baixo custo, atendendo à restrição obrigatória proposta na atividade. Como resultado, o agente mostrou capacidade de resumir adequadamente conteúdos educacionais curtos e médios, produzindo saídas úteis para estudo e revisão rápida. A implementação também incluiu testes com múltiplos exemplos e análise crítica das limitações.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Educação |
| **Função do agente** | Resumo |
| **Restrição obrigatória** | Baixo custo |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe como entrada um arquivo PDF contendo material educacional, como apostilas, artigos, capítulos, anotações ou textos de aula. O usuário informa o caminho do arquivo no terminal, e o sistema faz a leitura do documento.

### 3.2 Processamento (Pipeline)

O pipeline do agente ocorre nas seguintes etapas:

1. Recebimento do caminho do arquivo PDF.
2. Verificação da existência e do tipo do arquivo.
3. Extração do texto do PDF.
4. Validação da quantidade mínima de conteúdo.
5. Pré-processamento para reduzir ruídos básicos.
6. Montagem do prompt com instruções específicas.
7. Envio do texto ao modelo Gemini.
8. Recebimento e pós-processamento da resposta.
9. Exibição da saída estruturada ao usuário.

```text
PDF → Extração de texto → Validação → Pré-processamento → Prompt → Gemini → Pós-processamento → Saída
```

### 3.3 Decisão

O agente “pensa” por meio de uma combinação de regras simples e instruções dadas ao LLM. A parte determinística do sistema valida a entrada, trata erros e organiza o texto. A parte de decisão semântica é delegada ao modelo Gemini, que recebe um prompt instruindo a gerar uma resposta fiel, concisa e organizada em quatro partes: resumo geral, principais pontos, palavras-chave e sugestão de revisão. A lógica central do agente é orientar o modelo para condensar o conteúdo sem inventar informações e mantendo foco em utilidade para estudo.

### 3.4 Saída (Output)

A saída do agente é textual e estruturada em quatro partes:

- **Resumo geral**
- **Principais pontos**
- **Palavras-chave**
- **Sugestão de revisão**

Esse formato foi escolhido para facilitar revisão rápida e organização do estudo pelo usuário.

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.x | Linguagem principal |
| google-genai | atual | Integração com o modelo Gemini |
| python-dotenv | atual | Leitura de variáveis de ambiente |
| pypdf | atual | Extração de texto de arquivos PDF |
| Gemini | 2.5 Flash | Geração de resumos |

### 4.2 Estrutura do código

```text
projeto-1/
├── src/
│   ├── main.py
│   ├── agent.py
│   ├── pipeline.py
│   ├── prompts.py
│   ├── pdf_reader.py
│   └── evaluator.py
├── data/
│   └── pdfs/
│       ├── exemplo1.pdf
│       ├── exemplo2.pdf
│       └── exemplo3.pdf
├── resultados/
│   └── resultados-testes.md
├── requirements.txt
├── documento-engenharia.md
├── relatorio-entrega.md
└── README.md
```

### 4.3 Como executar

```bash
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar ambiente virtual (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente no arquivo .env
GEMINI_API_KEY=sua_chave_aqui
MODEL_NAME=gemini-2.5-flash

# 5. Executar
python src/main.py
```

Para testar múltiplos PDFs coloque os arquivos na pasta `data/pdfs:`

```bash
python src/evaluator.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Fidelidade | Verifica se o resumo preserva as ideias centrais do texto original | Satisfatório |
| Clareza | Avalia se a resposta é compreensível e bem escrita | Satisfatório |
| Organização | Verifica se a saída segue a estrutura esperada | Satisfatório |
| Utilidade para revisão | Avalia se a resposta ajuda o estudante a revisar o conteúdo | Satisfatório |
| Custo | Observa simplicidade da arquitetura e baixo consumo de recursos | Satisfatório |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:** PDF com conteúdo sobre aprendizagem baseada em problemas.
- **Saída esperada:** resumo correto destacando definição, papel do aluno, papel do professor e benefícios da metodologia.
- **Saída obtida:** o agente gerou resumo coerente, listou pontos principais, palavras-chave e sugestão de revisão.
- **Resultado:** Sucesso

#### Teste 2

- **Entrada:** PDF com conteúdo sobre metodologias ativas.
- **Saída esperada:** resumo destacando protagonismo do estudante e benefícios pedagógicos.
- **Saída obtida:** o agente resumiu corretamente o conteúdo e apresentou saída organizada.
- **Resultado:** Sucesso

#### Teste 3

- **Entrada:** PDF com conteúdo sobre avaliação formativa.
- **Saída esperada:** resumo destacando acompanhamento contínuo da aprendizagem e diferença em relação à avaliação classificatória.
- **Saída obtida:** o agente produziu resposta fiel ao texto e útil para revisão.
- **Resultado:** Sucesso

### 5.3 Análise dos resultados

Os resultados obtidos indicam que o agente atingiu o objetivo principal do projeto: resumir materiais didáticos de forma útil, organizada e com baixo custo arquitetural. Os principais pontos fortes foram a simplicidade da solução, a clareza da saída e a aderência ao problema proposto. A arquitetura em pipeline foi suficiente para atender aos requisitos do trabalho sem necessidade de componentes mais sofisticados. Como pontos fracos, observou-se dependência da qualidade do texto extraído do PDF e limitação em casos de arquivos escaneados sem texto digital. Além disso, a avaliação foi manual, sem métricas automáticas quantitativas.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [ ] Memória persistente
- [x] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

Entre as limitações encontradas, destaca-se a dependência de PDFs com texto extraível. Arquivos escaneados podem não ser processados adequadamente sem uso de OCR. Além disso, o sistema ainda não possui interface gráfica e depende de execução via terminal. Como trabalhos futuros, pretende-se permitir leitura de outros formatos de arquivo, oferecer diferentes níveis de resumo, incluir interface web simples e adicionar métricas automáticas de avaliação.

---

## 8. Referências

1. Documentação oficial do Google Gemini API.
2. Documentação da biblioteca `pypdf`.
3. Materiais da disciplina de Sistemas de Machine Learning.
4. Documentação oficial do Python.

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
