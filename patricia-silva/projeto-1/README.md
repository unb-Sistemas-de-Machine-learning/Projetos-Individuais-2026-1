# Projeto 1 — Agente de recomendação de estudo (explicabilidade obrigatória)
> **Aluno(a):** Patricia Helena Macedo da Silva 
> **Matrícula:** 221037993
> **Domínio:** Educação [2]
> **Função do agente:** Recomendação [2]
> **Restrição obrigatória:** Explicabilidade obrigatória  [4]

Protótipo em Python: **RAG leve** (TF-IDF sobre `data/kb/*.md`) + **LLM** com saída JSON validada (Pydantic). Cada recomendação inclui **justificativa** obrigatória.

## Requisitos

- Python 3.11+  
- **Opção A:** chave **Google Gemini** (`GEMINI_API_KEY` em [Google AI Studio](https://aistudio.google.com/apikey))  
- **Opção B:** [Ollama](https://ollama.com/) em execução local (deixe `GEMINI_API_KEY` vazio)

## Instalação

```powershell
cd projeto-individual-1\patricia-silva\projeto-1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edite `.env`: defina `GEMINI_API_KEY` e opcionalmente `GEMINI_MODEL` (no AI Studio use o **nome exato** do modelo; o padrão do código é `gemini-2.5-flash`, com fallbacks automáticos se der 404), ou deixe a chave vazia e use Ollama.

## Exemplos de execução

```powershell
python -m src.main --objetivo "Aprender fundamentos de machine learning" --nivel intermediario --horas 8h --restricoes "Preferencia por exercicios"
```

Saída apenas JSON (útil para scripts):

```powershell
python -m src.main --objetivo "Revisar calculo" --nivel iniciante --horas 4h --json
```

## Testes

```powershell
python -m pytest tests/ -v
```

## Documentação da disciplina

- [`documento-engenharia.md`](docs/documento-engenharia.md) — requisitos, fluxo, arquitetura  
- [`relatorio-entrega.md`](docs/relatorio-entrega.md) — modelagem, avaliação, checklist  

