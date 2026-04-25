# Mission Brief

> **Aluno(a):** Carlos Henrique Souza Bispo
> **Matricula:** 211061529
> **Dominio:** Triagem de Demandas Academicas

---

## 1. Objetivo do agente

Automatizar a triagem inicial de mensagens de alunos, classificando a solicitacao, estimando urgencia, extraindo dados essenciais e roteando para o setor correto com rastreabilidade.

---

## 2. Problema que ele resolve

Demandas chegam em texto livre e sem padrao, o que torna a triagem manual lenta e sujeita a erros. O agente reduz tempo de resposta, padroniza encaminhamentos e melhora qualidade operacional.

---

## 3. Usuarios-alvo

- Equipe de secretaria academica
- Coordenacao de curso
- Equipes de suporte tecnico e financeiro

---

## 4. Contexto de uso

Uso em ambiente administrativo universitario, integrado a webhook e n8n. Acontece continuamente durante o atendimento dos alunos, com necessidade de resposta rapida e rastreavel.

---

## 5. Entradas e saidas esperadas

| Item | Descricao |
|------|-----------|
| **Entrada** | Mensagem textual do aluno |
| **Formato da entrada** | JSON com `message`, opcionalmente `source` |
| **Saida** | Classificacao + decisao de fluxo |
| **Formato da saida** | JSON estruturado com categoria, urgencia, confianca, entidades e acao |

---

## 6. Limites do agente

### O que o agente faz:

- Classifica demanda em categorias operacionais
- Estima urgencia e confianca
- Extrai campos relevantes (ex: RA)
- Decide fluxo automatico ou escalonamento humano

### O que o agente NAO deve fazer:

- Decidir casos criticos com baixa confianca
- Assumir informacoes nao presentes no texto
- Substituir validacao humana em casos sensiveis

---

## 7. Criterios de aceitacao

- [x] Tres abordagens implementadas e comparadas
- [x] Decisao final registrada em ADR
- [x] Testes automatizados executados
- [x] Fluxo n8n exportado e documentado
- [x] Evidencias de funcionamento registradas

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Classificacao incorreta em texto ambiguo | Media | Alto | Limiar de confianca + fallback humano |
| Falha em integracao externa | Media | Medio | Retentativa e log de erro |
| Dados incompletos (sem RA) | Alta | Medio | Validacao de campos e solicitacao de complemento |

---

## 9. Evidencias necessarias

- [x] Resultados de testes
- [x] Benchmark comparativo entre as solucoes
- [x] Logs/outputs de exemplo do processamento
