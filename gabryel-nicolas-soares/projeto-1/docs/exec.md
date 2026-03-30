# Como executar o projeto

## Pré-requisitos

- Python 3.11 ou superior — https://www.python.org/downloads/
- Ollama — https://ollama.com
- Git — https://git-scm.com

---

## Passo 1 — Clonar o repositório

```bash
git clone https://github.com/gabryelns/Projetos-Individuais-2026-1.git
cd projeto-1
```

---

## Passo 2 — Criar e ativar o ambiente virtual

**Windows:**
```bash
python -m venv .venv
```
Depois ative:
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Quando ativado, aparece `(.venv)` no início da linha do terminal.

---

## Passo 3 — Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Passo 4 — Instalar o Ollama

1. Acesse https://ollama.com e baixe o instalador para seu sistema
2. Instale normalmente
3. O Ollama inicia automaticamente em segundo plano após a instalação

Para verificar se está rodando:
```bash
ollama list
```

---

## Passo 5 — Baixar o modelo Llama 3

> ⚠️ Necessário apenas na primeira vez. O download é de aproximadamente 4GB.

```bash
ollama pull llama3
```

---

## Passo 6 — Executar o agente

```bash
python src/main.py
```

---

## Observações

- O Ollama precisa estar rodando em segundo plano para o agente funcionar
- Se aparecer erro de conexão, verifique se o Ollama está ativo com `ollama list`
- O projeto não requer chave de API — tudo roda localmente
- Os dados da sessão são descartados ao encerrar o programa