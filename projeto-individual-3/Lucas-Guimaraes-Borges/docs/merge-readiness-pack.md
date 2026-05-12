# Merge-Readiness Pack

> **Projeto:** Triagem Inteligente de Emails da Codzz  
> **Aluno:** Lucas Guimarães Borges  
> **Data:** 05/05/2026

## 1. Resumo da solução escolhida

A solução final (Solution C) usa classificação + validação de confiança + fallback para escalonamento humano, reduzindo risco de roteamento incorreto em casos ambíguos.

## 2. Comparação entre as três alternativas

| Criterio | Solution A | Solution B | Solution C |
|----------|------------|------------|------------|
| Abordagem | Regras simples | Regras + base de conhecimento | Pipeline com validação |
| Custo | Baixo | Médio | Médio |
| Complexidade | Baixa | Media | Media |
| Qualidade da resposta | Media | Media-alta | Alta |
| Riscos | Maior falso positivo | Dependência da KB | Mais pontos de manutenção |
| Manutenibilidade | Alta | Media | Alta |
| Adequação ao problema | Média | Alta | Alta |

**Solução escolhida:** C

## 3. Testes executados

| Teste | Descrição | Resultado |
|-------|-----------|-----------|
| `test_solution_a_cancelamento_tem_prioridade` | Prioridade de cancelamento | Passou |
| `test_solution_b_financeiro` | Classificação financeira | Passou |
| `test_solution_c_escalonamento` | Fallback em baixa confiança | Passou |

## 4. Evidências de funcionamento

- Registro de dados em tabela Supabase (`docs/evidence/funcionamento.md`)
- Evidência visual de inserções em `suporte` (print)
- Benchmark das 3 soluções (`docs/evidence/benchmark-output.json`)
- Vídeo de demonstração do fluxo: [https://youtu.be/mlclCzgOFtY](https://youtu.be/mlclCzgOFtY)

## 5. Limitações conhecidas

- Classificação depende da qualidade textual do e-mail.
- Casos de múltiplas intenções ainda exigem revisão humana.

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Ambiguidade de linguagem | Média | Alto | Escalonamento por baixa confiança |
| Mudança de padrão de e-mails | Média | Médio | Revisão periódica de regras/KB |

## 7. Decisões arquiteturais

- ADR-001: Escolha da Solution C como base final.

## 8. Instruções de execução

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python src/run_benchmark.py
```

## 9. Checklist de revisão

- [x] Mission brief atendido
- [x] Três soluções implementadas/prototipadas
- [x] Testes executados e documentados
- [x] Evidências registradas em `docs/evidence/`
- [x] ADR registrado em `docs/adr/`
- [x] Agent.md preenchido
- [x] Mentorship pack e runbook preenchidos

## 10. Justificativa para merge

A entrega está completa no padrão solicitado, com rastreabilidade de decisões, três abordagens comparadas, workflow n8n incluído e evidências de funcionamento/testes.

