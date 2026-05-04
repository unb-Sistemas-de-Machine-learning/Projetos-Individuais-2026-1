# Merge-Readiness Pack

> **Projeto:** Triagem Inteligente de Demandas Academicas
> **Aluno(a):** Carlos Henrique Souza Bispo
> **Data:** 25/04/2026

---

## 1. Resumo da solucao escolhida

Foi escolhida a Solution C (pipeline multi-etapas com validacao e fallback). Ela combina classificacao, extracao de entidades, verificacao de consistencia e decisao de escalonamento com base em confianca.

---

## 2. Comparacao entre as tres alternativas

| Criterio | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| **Abordagem** | Prompt unico e heuristica de palavras-chave | Classificacao com recuperacao em base de conhecimento | Pipeline com classificacao, validacao e decisao |
| **Custo** | Baixo | Medio | Medio |
| **Complexidade** | Baixa | Media | Media/Alta |
| **Qualidade da resposta** | Media | Boa | Muito boa |
| **Riscos** | Alto risco de ambiguidade | Dependencia da qualidade da base | Custo de implementacao maior |
| **Manutenibilidade** | Alta | Media | Alta |
| **Adequacao ao problema** | Media | Boa | Muito boa |

**Solucao escolhida:** C

**Justificativa:**

A Solution C oferece melhor equilibrio entre qualidade de decisao, robustez a entradas incompletas, rastreabilidade e seguranca operacional (fallback por baixa confianca).

Metricas observadas no benchmark local:

- solution-a: confianca media 0.60, tempo medio 0.028 ms
- solution-b: confianca media 0.68, tempo medio 0.069 ms
- solution-c: confianca media 0.684, tempo medio 0.053 ms

Mesmo sem maior confianca media absoluta, a solution-c foi escolhida por apresentar guardrails explicitos para solicitacao de dados e escalonamento humano.

---

## 3. Testes executados

| Teste | Descricao | Resultado |
|-------|-----------|-----------|
| test_solution_a_classifies_support | valida classificacao basica da solution-a | Passou |
| test_solution_b_uses_knowledge_base | valida recuperacao de politica na solution-b | Passou |
| test_solution_c_escalates_low_confidence | valida fallback com baixa confianca | Passou |
| test_solution_c_requests_ra_for_financial | valida solicitacao de dados faltantes | Passou |
| test_benchmark_script_generates_outputs | valida geracao de evidencias automatizadas | Passou |

---

## 4. Evidencias de funcionamento

- `docs/evidence/test-results.md` com resultado dos testes.
- `docs/evidence/funcionamento.md` com exemplos de entrada/saida.
- `docs/evidence/comparacao-solucoes.md` gerado automaticamente pelo benchmark.
- `docs/evidence/benchmark-output.json` com dados brutos da comparacao.
- `docs/evidence/plano-de-commits.md` com mensagens e racionalidade sugeridas por etapa.

---

## 5. Limitacoes conhecidas

- O prototipo local usa regras heuristicas para simular parte do raciocinio da IA.
- O workflow n8n exportado depende de credenciais reais para execucao completa.

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Mensagens ambiguas sem contexto | Media | Alto | fallback por confianca + revisao humana |
| Falha de integracao (Slack/Email/Sheets) | Media | Medio | logs, retentativa e alerta |
| Falta de campos essenciais (RA) | Alta | Medio | validacao de entidades + solicitacao de complemento |

---

## 7. Decisoes arquiteturais

- ADR-001: escolha da Solution C como abordagem final.

---

## 8. Instrucoes de execucao

```bash
# Rodar testes
python -m unittest discover -s tests -p "test_*.py" -v

# Gerar comparacao entre as solucoes
python src/run_benchmark.py

# Importar workflow no n8n
# arquivo: src/workflows/triagem-demandas-academicas.json
```

---

## 9. Checklist de revisao

- [x] Mission brief atendido
- [x] Tres solucoes implementadas/prototipadas
- [x] Testes executados e documentados
- [x] Evidencias registradas em `docs/evidence/`
- [x] ADR(s) registrado(s) em `docs/adr/`
- [ ] Commits com mensagens claras e racionalidade
- [x] Codigo funcional em `src/`
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido

---

## 10. Justificativa para merge

A entrega atende aos artefatos obrigatorios, apresenta tres alternativas comparadas, registra decisao arquitetural com racionalidade e possui testes automatizados para validar comportamento minimo esperado. A solucao escolhida e adequada para evolucao incremental em ambiente real de n8n.
