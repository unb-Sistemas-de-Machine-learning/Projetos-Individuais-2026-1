# Mission Brief

> **Aluno(a):** Joao Filipe de Oliveira Souza
> **Matricula:** 231035141
> **Dominio:** Triagem automatica de demandas de atendimento academico

---

## 1. Objetivo do agente

Implementar um agente de IA orquestrado por n8n para classificar demandas academicas, estimar urgencia e definir o encaminhamento operacional mais adequado com rastreabilidade.

---

## 2. Problema que ele resolve

A equipe de atendimento recebe demandas em texto livre e sem padronizacao. Isso gera atraso, retrabalho e erro de encaminhamento. O agente reduz o tempo de triagem inicial e aumenta consistencia na priorizacao.

---

## 3. Usuarios-alvo

- Solicitantes (alunos e usuarios internos) que enviam demandas pelo formulario.
- Equipes operacionais (atendimento, suporte e financeiro) que recebem os encaminhamentos.
- Coordencao/gestao que precisa de trilha de auditoria.

---

## 4. Contexto de uso

O agente opera no fluxo de atendimento inicial. Toda nova demanda enviada pelo formulario do n8n e processada automaticamente, com classificacao por IA e decisao de rota por urgencia.

---

## 5. Entradas e saidas esperadas

| Item | Descricao |
|------|-----------|
| **Entrada** | Nome, email, assunto e descricao da demanda |
| **Formato da entrada** | Dados estruturados do Form Trigger do n8n |
| **Saida** | Classificacao da demanda, urgencia e acao de encaminhamento |
| **Formato da saida** | JSON estruturado + persistencia em Data Table + notificacao por email |

---

## 6. Limites do agente

### O que o agente faz:

- Classifica a demanda em categorias predefinidas.
- Estima urgencia (baixa, media, alta).
- Encaminha automaticamente para o fluxo operacional.
- Registra dados de decisao para auditoria.

### O que o agente NAO deve fazer:

- Tomar decisoes irreversiveis fora do escopo de triagem.
- Responder com dados nao presentes na entrada.
- Omitir baixa confianca da classificacao.
- Substituir validacao humana em casos ambiguos.

---

## 7. Criterios de aceitacao

- [x] Fluxo no n8n recebe entrada e executa classificacao automatica.
- [x] IA influencia decisao de roteamento (nao apenas resposta textual).
- [x] Existe limiar de confianca com fallback seguro.
- [x] Decisoes e dados principais ficam persistidos para auditoria.
- [x] Integracao externa de encaminhamento esta ativa (email).

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Classificacao incorreta em texto ambiguo | Media | Alto | Limiar de confianca e fallback para categoria/urgencia segura |
| Falha em servico externo (email) | Media | Medio | Retentativa no n8n e monitoramento dos logs |
| Dados incompletos na entrada | Baixa | Medio | Campos obrigatorios no formulario |
| Violation de privacidade por dados sensiveis no texto | Baixa | Alto | Restricao de uso, revisao periodica e boas praticas de acesso |

---

## 9. Evidencias necessarias

- [x] Workflow exportado em JSON no repositorio.
- [x] Relatorio tecnico preenchido.
- [x] ADR da escolha da solucao registrada.
- [x] Runbook e merge-readiness pack preenchidos.
- [x] Roteiro e log de evidencias em `docs/evidence/evidence-log.md`.
