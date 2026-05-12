# Triagem Inteligente de E-mails de Suporte da Codzz

## Resumo

Este projeto implementa uma automação inteligente no n8n para triagem de e-mails de suporte da Codzz. O fluxo lê e-mails via IMAP, usa agente de IA para classificar categoria, atribuir urgência e gerar resumo operacional, persiste os dados no Supabase e roteia notificações por tipo de demanda.

Foram prototipadas três abordagens executáveis para o mesmo problema:

- Solution A: classificador por prompt e regras simples
- Solution B: classificador com base de conhecimento local
- Solution C: pipeline multi-etapas com validação e fallback

A solução final escolhida foi a Solution C, por equilibrar qualidade, rastreabilidade e segurança operacional.

## Estrutura

```text
.
├── agent.md
├── docs/
│   ├── mission-brief.md
│   ├── mentorship-pack.md
│   ├── workflow-runbook.md
│   ├── merge-readiness-pack.md
│   ├── adr/
│   │   └── 001-escolha-da-solucao.md
│   └── evidence/
├── relatorio-entrega.md
├── requirements.txt
├── solutions/
│   ├── solution-a/
│   ├── solution-b/
│   └── solution-c/
├── src/
│   ├── run_benchmark.py
│   └── workflows/
│       └── fluxo_n8n_agente_email.json
└── tests/
    └── test_solutions.py
```

## Como executar

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python src/run_benchmark.py
```

## Workflow n8n

- Arquivo: `src/workflows/fluxo_n8n_agente_email.json`
- Fluxo principal: IMAP -> normalização -> AI Agent -> parse estruturado -> persistência -> switch de categoria -> notificação
- Integrações: IMAP, OpenAI, Supabase e HTTP API de notificação

## Evidências

- Documentação do processo: `docs/`
- Evidências de execução e comparação: `docs/evidence/`
- Decisão arquitetural: `docs/adr/001-escolha-da-solucao.md`
- Vídeo de demonstração do fluxo: [https://youtu.be/mlclCzgOFtY](https://youtu.be/mlclCzgOFtY)

## Status atual

- Testes automatizados: 3/3 passando
- Benchmark das soluções: executado e salvo em `docs/evidence/benchmark-output.json`
- Evidência visual de persistência no Supabase: registrada em `docs/evidence/funcionamento.md`

