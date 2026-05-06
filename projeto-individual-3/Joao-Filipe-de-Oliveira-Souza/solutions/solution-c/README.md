# Solution C - Pipeline multi-etapas com validacao

## Objetivo

Implementar triagem robusta com inferencia por IA + regras deterministicas de seguranca e auditabilidade.

## Como funciona

1. Coleta demanda via formulario.
2. Prepara contexto consolidado para IA.
3. Classifica com agente e parser estruturado.
4. Aplica validacao por limiar de confianca (`>= 0.70`).
5. Persiste campos chave para auditoria.
6. Roteia por urgencia para acao final.

## Regras de seguranca

- Se `confianca >= 0.70`, aceita classificacao da IA.
- Se `confianca < 0.70`, aplica fallback:
  - `categoria_final = outro`
  - `urgencia_final = media`

## Fluxo no n8n (implementado)

```text
Form Trigger -> Set contexto -> Agent + LLM + Structured Parser -> Set validacao -> Data Table -> Switch urgencia -> Gmail/registro
```

## Artefato principal

Workflow exportado:

- `src/workflows/Sistema de Triagem Automática de Demandas-2.json`
- Casos de teste: `tests/casos-teste-triagem.csv`
- Log de evidencias: `docs/evidence/evidence-log.md`

## Vantagens

- Melhor previsibilidade operacional.
- Alta rastreabilidade.
- Menor risco de automacao indevida.

## Desvantagens

- Maior complexidade de configuracao.
- Dependencia de multiplas integracoes.

## Criterios de avaliacao da alternativa

- Taxa de roteamento correto por urgencia.
- Completude da trilha de auditoria.
- Comportamento em baixa confianca.

## Status

Implementada e selecionada como solucao final (ADR-001).

## Como demonstrar

1. Importar o workflow no n8n.
2. Configurar credenciais OpenAI e Gmail.
3. Executar os cenarios de `tests/casos-teste-triagem.csv`.
4. Registrar resultados em `docs/evidence/evidence-log.md`.
