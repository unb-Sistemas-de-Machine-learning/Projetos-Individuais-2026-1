# Triagem Inteligente de Demandas Academicas com n8n e IA

## Resumo

Este repositorio entrega o Projeto Individual 3 com foco em automacao de triagem para coordenacao academica. A solucao recebe uma mensagem de aluno via webhook, usa IA para classificar e extrair dados, escolhe o fluxo adequado no n8n e registra rastreabilidade para auditoria.

Foram implementadas tres abordagens executaveis:

- Solution A: prompt unico com classificacao direta
- Solution B: classificacao com base de conhecimento (RAG simples)
- Solution C: pipeline multi-etapas com validacao e fallback

A solucao final escolhida foi a Solution C, documentada em ADR.

## Estrutura

```
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
│       └── triagem-demandas-academicas.json
└── tests/
    └── test_solutions.py
```

## Problema Resolvido

Demandas academicas chegam em texto livre e sem padrao. O objetivo e reduzir tempo de resposta e retrabalho com triagem automatica orientada por decisao:

1. classificar categoria
2. estimar urgencia
3. extrair campos uteis (RA, email, etc.)
4. rotear para acao automatica ou escalonar humano

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate

# Rodar testes
python -m unittest discover -s tests -p "test_*.py" -v

# Gerar comparacao das 3 solucoes
python src/run_benchmark.py
```

Nao ha dependencias Python externas obrigatorias para os prototipos locais.

## Workflow n8n

- Arquivo de importacao: src/workflows/triagem-demandas-academicas.json
- Fluxo: Webhook -> Normalizacao -> Classificacao IA -> Validacao de confianca -> Persistencia -> Roteamento -> Acao
- Integracoes previstas: Google Sheets, Slack e Email

## Evidencias e Decisoes

- Evidencias: docs/evidence/
- Decisao arquitetural: docs/adr/001-escolha-da-solucao.md
- Consolidacao para merge: docs/merge-readiness-pack.md

## Status de validacao local

- Suite de testes automatizados: 5/5 passando
- Benchmark gerado com comparacao das 3 abordagens
- Artefatos atualizados em docs/evidence/

Resumo do benchmark:

- solution-a: confianca media 0.60, tempo medio 0.028 ms
- solution-b: confianca media 0.68, tempo medio 0.069 ms
- solution-c: confianca media 0.684, tempo medio 0.053 ms

## Criterios da rubrica x evidencias

| Criterio de avaliacao | Onde esta evidenciado |
|-----------------------|------------------------|
| Clareza do Mission Brief | docs/mission-brief.md |
| Qualidade do agent.md | agent.md |
| Mentorship Pack e Workflow Runbook | docs/mentorship-pack.md e docs/workflow-runbook.md |
| Implementacao das tres solucoes | solutions/solution-a/, solutions/solution-b/, solutions/solution-c/ |
| Testes e rastreabilidade | tests/test_solutions.py e docs/evidence/test-results.md |
| Comparacao e decisao arquitetural | docs/adr/001-escolha-da-solucao.md e docs/evidence/comparacao-solucoes.md |
| Prontidao de merge | docs/merge-readiness-pack.md |

## Validacao rapida no n8n

1. Importar src/workflows/triagem-demandas-academicas.json no n8n.
2. Configurar credenciais (OpenAI, Google Sheets, Slack, Email).
3. Ativar o workflow.
4. Enviar payload de teste para o webhook:

```bash
curl -X POST "http://localhost:5678/webhook/triagem-demandas-academicas" \
    -H "Content-Type: application/json" \
    -d '{"message":"Nao consigo acessar o portal e preciso urgente para enviar atividade","source":"teste-local"}'
```

5. Confirmar em logs/planilha a categoria, urgencia, confianca e rota escolhida.

## Pendencia para fechar nota maxima

Para cumprir integralmente o processo avaliado, gere commits separados por etapa com racionalidade. Foi preparado um roteiro em docs/evidence/plano-de-commits.md.

## Nota sobre credenciais

O workflow exportado usa placeholders de credenciais. Para executar no n8n, configure suas credenciais reais no ambiente local.

