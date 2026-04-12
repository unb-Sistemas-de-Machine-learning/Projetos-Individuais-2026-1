# Agente Auditor de Compras Publicas

Projeto individual da disciplina de Sistemas de Machine Learning.

O agente consulta licitacoes no PNCP, enriquece os dados com CNPJ via Brasil API, aplica regras deterministicamente auditaveis e gera um relatorio em Markdown com score, grau de risco e parecer consolidado com LLM.

## Estrutura principal

```text
projeto-1/
├── auditor.py
├── auditor/
├── documento-engenharia.md
├── relatorio-entrega.md
├── relatorio_auditoria.md
└── .env.example
```

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite o arquivo `.env` e preencha:

```env
KEY=sua_chave_aqui
```

Depois execute:

```bash
python auditor.py \
  --data-inicial 20260320 \
  --data-final 20260329 \
  --modalidade 5 \
  --top-n 5 \
  --saida-md relatorio_auditoria.md
```
