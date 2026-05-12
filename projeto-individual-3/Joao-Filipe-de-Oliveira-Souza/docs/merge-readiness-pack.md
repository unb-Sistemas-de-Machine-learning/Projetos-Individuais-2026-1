# Merge-Readiness Pack

> **Projeto:** Sistema de Triagem Automatica de Demandas Academicas
> **Aluno(a):** Joao Filipe de Oliveira Souza
> **Data:** 05/05/2026

---

## 1. Resumo da solucao escolhida

A entrega adota um workflow n8n com agente de IA para classificar demandas e regras deterministicas para validar confianca e rotear por urgencia. A combinacao melhora previsibilidade operacional e reduz risco de encaminhamento indevido.

---

## 2. Comparacao entre as tres alternativas

| Criterio | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| **Abordagem** | Prompt unico | Prompt + base de conhecimento | Pipeline com parser estruturado e validacao |
| **Custo** | Baixo | Medio | Medio |
| **Complexidade** | Baixa | Media | Media/Alta |
| **Qualidade da resposta** | Media | Alta | Alta |
| **Riscos** | Alto | Medio | Baixo/Medio |
| **Manutenibilidade** | Media | Media | Alta |
| **Adequacao ao problema** | Media | Boa | Muito boa |

**Solucao escolhida:** C

**Justificativa:**
- melhor controle de erro por limiar de confianca (>= 0.70);
- maior auditabilidade com persistencia dos campos de decisao;
- roteamento por urgencia com comportamento previsivel.

---

## 3. Testes executados

| Teste | Descricao | Resultado |
|-------|-----------|-----------|
| T1 | Mensagem com urgencia alta e tema tecnico | Passou |
| T2 | Mensagem com urgencia media e tema financeiro | Passou |
| T3 | Mensagem ambigua com baixa confianca | Passou |
| T4 | Persistencia de categoria/urgencia/confianca no Data Table | Passou |
| T5 | Disparo de email por rota de urgencia | Passou |

---

## 4. Evidencias de funcionamento

- Workflow exportado em `src/workflows/Sistema de Triagem Automatica de Demandas-2.json`.
- Log estruturado de evidencias em `docs/evidence/evidence-log.md`.
- Campos persistidos no Data Table: categoria, urgencia, confianca, resumo, categoria_final, urgencia_final.

---

## 5. Limitacoes conhecidas

- Dependencia de servicos externos (LLM e Gmail).
- Classificacoes em texto muito curto podem reduzir confianca.
- Sem suite de testes automatizada para simulacoes em lote.

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Erro de classificacao em caso ambiguo | Media | Alto | fallback para categoria segura e urgencia media |
| Indisponibilidade da API de IA | Baixa/Media | Alto | retentativa e monitoramento de execucoes |
| Falha no envio de email | Media | Medio | reprocessamento manual e alerta operacional |

---

## 7. Decisoes arquiteturais

- ADR-001: Escolha da Solution C como arquitetura final.
- Uso de parser estruturado para saida JSON consistente.
- Separacao entre inferencia da IA e regras de negocio fixas.

---

## 8. Instrucoes de execucao

```bash
# 1) Abrir o n8n
# 2) Importar o workflow em src/workflows/
# 3) Configurar credenciais (OpenAI e Gmail)
# 4) Ativar o workflow e submeter o formulario
```

---

## 9. Checklist de revisao

- [x] Mission brief atendido
- [x] Tres solucoes comparadas
- [x] Testes executados e documentados
- [x] Plano e log de evidencias registrados em `docs/evidence/`
- [x] ADR registrado em `docs/adr/`
- [ ] Commits por etapa com racionalidade clara
- [x] Fluxo funcional em `src/`
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido

---

## 10. Justificativa para merge

A entrega possui workflow funcional, documentacao tecnica completa, decisao arquitetural registrada e rastreabilidade da classificacao para auditoria. Os itens pendentes concentram-se em evidencias visuais e organizacao do historico de commits, sem bloquear validacao funcional da automacao.
