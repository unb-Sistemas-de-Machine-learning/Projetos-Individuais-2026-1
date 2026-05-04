# Projeto 1 - Agente de Resumo de Materiais Didáticos de Baixo Custo

## Visão geral

Este projeto implementa um agente de IA no domínio da educação com a função de resumir materiais didáticos em PDF para estudantes. A solução foi projetada com arquitetura simples e baixo custo, utilizando extração de texto do PDF e geração de resumo com o modelo Gemini.

## Objetivo

Apoiar estudantes na revisão de conteúdos por meio da geração de:

- resumo geral
- principais pontos
- palavras-chave
- sugestão de revisão

## Arquitetura

O sistema segue um pipeline sequencial:

```text
PDF → Extração de texto → Validação → Pré-processamento → Prompt → Gemini → Pós-processamento → Saída
```

## Estrutura do projeto

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
├── resultados/
│   └── resultados-testes.md
├── requirements.txt
├── .env.example
├── documento-engenharia.md
├── relatorio-entrega.md
└── README.md
```

## Como executar

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual no PowerShell

```bash
.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Criar arquivo `.env`

Crie um arquivo chamado `.env` na raiz do projeto com o conteúdo:

```env
GEMINI_API_KEY=sua_chave_aqui
MODEL_NAME=gemini-2.5-flash
```

### 5. Rodar o projeto

```bash
python src/main.py
```

Ao executar, informe o caminho de um arquivo PDF.

Exemplo:

```text
data/pdfs/exemplo1.pdf
```

## Como rodar os testes

Coloque arquivos PDF dentro de `data/pdfs/` e execute:

```bash
python src/evaluator.py
```

Os resultados serão salvos em:

```text
resultados/resultados-testes.md
```

## Tecnologias utilizadas

- Python
- Gemini API
- google-genai
- python-dotenv
- pypdf

## Limitações

- depende de PDFs com texto extraível
- não trata bem PDFs escaneados sem OCR
- não possui interface gráfica
- avaliação realizada principalmente de forma manual

## Melhorias futuras

- adicionar suporte a OCR
- permitir outros formatos de arquivo
- criar interface web
- adicionar níveis de resumo
- implementar avaliação automática
