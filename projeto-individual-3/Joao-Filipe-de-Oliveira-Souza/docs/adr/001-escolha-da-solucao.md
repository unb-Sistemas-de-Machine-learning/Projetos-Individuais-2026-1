# ADR-001: Escolha da arquitetura final de triagem

> **Data:** 05/05/2026
> **Status:** aceita

---

## Contexto

O projeto exige automacao de triagem com uso real de IA em decisao de fluxo, incluindo classificacao, roteamento, integracao externa e rastreabilidade. Foram avaliadas tres alternativas com diferentes niveis de controle e complexidade.

---

## Alternativas consideradas

### Alternativa A: Prompt unico

- **Descricao:** um unico prompt classifica e define resposta final.
- **Pros:** simples de montar e baixo custo inicial.
- **Contras:** menor previsibilidade, maior sensibilidade a variacao de prompt e menor controle de fallback.

### Alternativa B: Prompt + base de conhecimento

- **Descricao:** classificacao com suporte de conteudo de referencia.
- **Pros:** melhora contextualizacao e qualidade em casos especificos.
- **Contras:** exige manutencao da base e aumenta pontos de falha.

### Alternativa C: Pipeline multi-etapas com parser estruturado e validacao

- **Descricao:** fluxo com preparacao de contexto, classificacao por IA, parse estruturado, validacao por limiar de confianca, persistencia e roteamento por urgencia.
- **Pros:** maior auditabilidade, melhor tratamento de erro e comportamento mais previsivel.
- **Contras:** implementacao mais detalhada e dependente de mais configuracoes.

---

## Decisao

Foi escolhida a **Alternativa C**. O motivo principal foi combinar qualidade da IA com regras deterministicas de seguranca operacional. O limiar de confianca (>= 0.70) reduz o risco de automacao indevida e melhora a confiabilidade do roteamento.

---

## Consequencias

- Ganho de rastreabilidade com persistencia de campos-chave da triagem.
- Maior robustez no tratamento de incerteza.
- Aumento moderado de complexidade de manutencao do workflow.
- Necessidade de monitorar credenciais e disponibilidade de servicos externos.

---

## Referencias

- `src/workflows/Sistema de Triagem Automatica de Demandas-2.json`
- `relatorio-entrega.md`
- `docs/merge-readiness-pack.md`
