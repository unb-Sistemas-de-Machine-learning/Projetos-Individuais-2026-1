# Workflow Runbook

> **Projeto:** Sistema de Triagem Automatica de Demandas Academicas
> **Aluno(a):** Joao Filipe de Oliveira Souza

---

## Processo obrigatorio de execucao

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief
- [x] Identificar entradas, saidas e restricoes
- [x] Anotar duvidas/limites de automacao

### Etapa 2: Propor tres solucoes possiveis

- [x] **Solution A:** Prompt unico para classificar e responder
- [x] **Solution B:** Classificacao com apoio de base de conhecimento
- [x] **Solution C:** Pipeline multi-etapas com parser estruturado e validacao de confianca

### Etapa 3: Registrar cada solucao em pasta separada

- [x] Criar `solutions/solution-a/`
- [x] Criar `solutions/solution-b/`
- [x] Criar `solutions/solution-c/`
- [x] Registrar comparacao no relatorio e na documentacao de decisao

### Etapa 4: Implementar prototipos minimos

- [x] Prototipo A validado conceitualmente
- [x] Prototipo B validado conceitualmente
- [x] Prototipo C implementado no n8n (workflow final exportado)

### Etapa 5: Executar testes

- [x] Testes manuais de fluxo com diferentes urgencias
- [x] Verificacao de persistencia e roteamento por regra
- [x] Consolidar roteiro de evidencias em `docs/evidence/`

### Etapa 6: Comparar as solucoes

| Criterio | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo | Medio | Medio |
| Complexidade | Baixa | Media | Media/Alta |
| Qualidade da resposta | Media | Alta | Alta |
| Riscos | Alto (instavel) | Medio (dependencia de base) | Baixo/Medio (controle por regra) |
| Manutenibilidade | Media | Media | Alta |
| Adequacao ao problema | Media | Boa | Muito boa |

### Etapa 7: Escolher uma solucao final

- [x] Solucao escolhida: **Solution C**
- [x] Justificativa: melhor equilibrio entre qualidade de classificacao, rastreabilidade e seguranca operacional.

### Etapa 8: Registrar a decisao em ADR

- [x] Criado `docs/adr/001-escolha-da-solucao.md`

### Etapa 9: Gerar o Merge-Readiness Pack

- [x] Preenchido `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [ ] Historico de commits por etapa ainda nao consolidado
