# Relatorio de Entrega — Projeto Individual 3: Automacao com n8n e Agentes de IA

> **Aluno(a):** Carlos Henrique Souza Bispo
> **Matricula:** 211061529
> **Data de entrega:** 25/04/2026

---

## 1. Resumo do Projeto

O projeto implementa uma automacao para triagem de demandas academicas usando n8n como orquestrador e IA para tomada de decisao. A entrada chega por webhook em texto livre. O agente classifica a demanda, estima urgencia e extrai dados relevantes (RA, email e contexto). Em seguida, o fluxo aplica regras de confianca para escolher entre atendimento automatico, notificacao de time responsavel ou escalonamento humano. Foram prototipadas tres abordagens (prompt simples, RAG simples e pipeline multi-etapas com validacao) e comparadas por custo, qualidade, riscos e manutenibilidade. A solucao final adotada foi a abordagem multi-etapas (solution-c), por oferecer melhor equilibrio entre qualidade de resposta, rastreabilidade e seguranca operacional.

---

## 2. Problema Escolhido

Secretarias e coordenacoes academicas recebem muitas demandas em formato nao padronizado. A falta de triagem inicial gera atraso, retrabalho e risco de encaminhamento incorreto. A automacao reduz tempo de resposta e melhora consistencia no roteamento.

---

## 3. Desenho do Fluxo

```text
Entrada Webhook -> Normalizacao -> Classificacao IA -> Validacao de confianca -> Persistencia -> Roteamento -> Acao final
```

### 3.1 Nos utilizados

| No | Tipo | Funcao no fluxo |
|----|------|-----------------|
| Webhook Entrada | Webhook | Receber requisicoes externas |
| Normalizar Entrada | Code | Padronizar payload e validar campos minimos |
| Classificar com IA | OpenAI Chat | Classificacao e extracao em JSON |
| Parse da Resposta | Code | Validar JSON retornado pela IA |
| Baixa Confianca? | IF | Direcionar para fallback humano |
| Persistir Google Sheets | Google Sheets | Auditoria de entrada/decisao |
| Rotear Categoria | Switch | Encaminhamento por categoria |
| Notificar Slack | Slack | Escalonamento operacional |
| Enviar Email * | Email | Encaminhamento setorial |
| Responder Webhook | Respond to Webhook | Retorno para cliente |

---

## 4. Papel do Agente de IA

- **Modelo/servico utilizado:** OpenAI (via no de chat no n8n)
- **Tipo de decisao tomada pela IA:** classificacao, extracao estruturada e suporte ao roteamento
- **Como a decisao da IA afeta o fluxo:** define categoria, urgencia e limiar de confianca que determina atendimento automatico ou revisao humana

---

## 5. Logica de Decisao

- **Condicao 1: confianca < 0.70**
  - Caminho A -> Notificar fila humana (Slack)
  - Caminho B -> continuar roteamento automatico
- **Condicao 2: categoria**
  - suporte_tecnico -> email para suporte
  - financeiro -> email para financeiro
  - secretaria_academica -> email para secretaria
  - indefinido -> revisao manual

---

## 6. Integracoes

| Servico | Finalidade |
|---------|------------|
| Google Sheets | Persistencia de entrada, classificacao e decisao |
| Slack | Notificacao de casos urgentes e baixa confianca |
| Email | Encaminhamento para times responsaveis |

---

## 7. Persistencia e Rastreabilidade

Cada execucao registra timestamp, mensagem original, categoria, urgencia, confianca e acao escolhida. O historico pode ser auditado na planilha e nos logs do n8n.

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** fallback para regras locais e escalonamento humano.
- **Entradas invalidas:** validacao no inicio do fluxo com resposta orientada.
- **Fallback (baixa confianca):** IF de confianca para bloquear automacao critica.

---

## 9. Diferenciais implementados

- [ ] Memoria de contexto
- [x] Multi-step reasoning
- [x] Integracao com base de conhecimento
- [ ] Uso de embeddings / busca semantica

---

## 10. Limitacoes e Riscos

A classificacao depende da qualidade do texto de entrada e pode falhar em mensagens muito curtas ou ambiguas. Integracoes externas (Slack/Email/Sheets) tambem podem falhar e exigem monitoramento.

---

## 11. Como executar

```bash
# 1. Rodar testes locais
python -m unittest discover -s tests -p "test_*.py" -v

# 2. Gerar benchmark/comparacao
python src/run_benchmark.py

# 3. Importar workflow no n8n
# arquivo: src/workflows/triagem-demandas-academicas.json
```

---

## 12. Referencias

1. Documentacao oficial n8n: https://docs.n8n.io/
2. OpenAI API docs: https://platform.openai.com/docs
3. Material da disciplina e templates de entrega

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (.json)
- [x] Codigo/scripts auxiliares incluidos
- [x] Demonstracao do fluxo (logs/outputs em docs/evidence)
- [x] Relatorio de entrega preenchido
- [ ] Pull Request aberto
