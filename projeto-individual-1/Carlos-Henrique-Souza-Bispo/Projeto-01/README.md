# Projeto Individual 1 - Agente de Classificacao de Risco de Evasao

## Tema do projeto

- Dominio: Educacao
- Funcao do agente: Classificacao
- Restricao obrigatoria: Explicabilidade obrigatoria

## Objetivo

Classificar risco de evasao estudantil em `baixo`, `moderado` ou `alto`, com justificativa explicavel e recomendacoes de intervencao.

## Estrutura

```text
Projeto-01/
├── src/
│   ├── agent.py
│   └── main.py
├── data/
│   └── test_cases.json
├── tests/
│   └── test_agent.py
├── requirements.txt
├── documento-engenharia.md
├── relatorio-entrega.md
└── README.md
```

## Como rodar o projeto

### 1) Pre-requisitos

- Python 3.10 ou superior
- pip
- PowerShell (Windows)

Verificacao:

```powershell
python --version
pip --version
```

### 2) Entrar na pasta

```powershell
cd "c:/Users/Carlos/Documents/Projetos-Individuais-2026-1/projeto-individual-1/Carlos-Henrique-Souza-Bispo/Projeto-01"
```

### 3) Criar e ativar ambiente virtual

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Se houver bloqueio de execucao no PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 4) Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5) Executar o projeto

```powershell
python src/main.py
```

### 6) Executar testes

```powershell
python -m unittest discover -s tests -v
```

## Uso opcional com OpenAI

Sem chave de API, o projeto roda normalmente com fallback local.

Para habilitar explicacao via LLM:

```powershell
$env:OPENAI_API_KEY="SUA_CHAVE_AQUI"
python src/main.py
```

## Solucao de problemas

- Erro "python nao reconhecido": instale Python e habilite a opcao de adicionar ao PATH.
- Erro ao ativar `.venv`: use os comandos de `ExecutionPolicy` acima.
- Erro de dependencia: atualize pip e reinstale:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
