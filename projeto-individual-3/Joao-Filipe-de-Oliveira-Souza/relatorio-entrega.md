# Relatorio de Entrega — Projeto Individual 3: Automacao com n8n e Agentes de IA

> **Aluno(a):** Joao Filipe de Oliveira Souza
> **Matricula:** 231035141
> **Data de entrega:** 25/04/2026

---

## 1. Resumo do Projeto

O projeto implementa uma automacao para triagem de demandas academicas usando n8n como orquestrador e IA para tomada de decisao. A entrada chega por formulario nativo do n8n. O agente classifica a demanda, estima urgencia e retorna saida estruturada via parser. Em seguida, o fluxo aplica regras de confianca para definir categoria e urgencia finais, persiste os dados em Data Table e roteia a acao por urgencia (alta, media ou baixa). Foram comparadas tres abordagens (prompt unico, prompt com base de conhecimento e pipeline multi-etapas). A solucao final adotada foi a abordagem multi-etapas (solution-c), por oferecer melhor equilibrio entre qualidade de resposta, rastreabilidade e seguranca operacional.

---

## 2. Problema Escolhido

Secretarias e coordenacoes academicas recebem muitas demandas em formato nao padronizado. A falta de triagem inicial gera atraso, retrabalho e risco de encaminhamento incorreto. A automacao reduz tempo de resposta e melhora consistencia no roteamento.

---

## 3. Desenho do Fluxo

```text
Formulario -> Preparar Contexto -> Agente IA + Parser -> Validacao de confianca -> Data Table -> Roteamento por urgencia -> Acao final
```

### 3.1 Nos utilizados

| No | Tipo | Funcao no fluxo |
|----|------|-----------------|
| Formulario de Demanda | Form Trigger | Receber solicitacao do usuario |
| Preparar Contexto para IA | Set | Consolidar assunto, descricao e dados do solicitante |
| Agente Classificador | AI Agent | Classificacao semantica da demanda |
| OpenAI GPT-5 Mini | LLM Chat | Modelo usado pelo agente |
| Parser de Classificacao | Structured Output Parser | Garantir saida JSON estruturada |
| Verificar Confianca da IA | Set | Aplicar regra de fallback por limiar |
| Armazenar Demanda | Data Table | Persistir trilha de auditoria |
| Rotear por Urgencia | Switch | Encaminhar para alta, media ou baixa urgencia |
| Enviar email - alta prioridade | Gmail | Notificar caso urgente |
| Enviar Email - Media Urgencia | Gmail | Notificar caso de media urgencia |
| Baixa Urgencia - Registrado | Set | Registrar baixa urgencia sem envio de email |

---

## 4. Papel do Agente de IA

- **Modelo/servico utilizado:** OpenAI (via no de chat no n8n)
- **Tipo de decisao tomada pela IA:** classificacao, urgencia e resumo da demanda
- **Como a decisao da IA afeta o fluxo:** define `categoria` e `urgencia` iniciais, que sao validadas por regra de confianca antes do roteamento

---

## 5. Logica de Decisao

- **Condicao 1: confianca >= 0.70**
  - Caminho A -> manter `categoria` e `urgencia` da IA
- **Condicao 2: confianca < 0.70**
  - Caminho B -> fallback para `categoria_final = outro` e `urgencia_final = media`
- **Condicao 3: urgencia_final**
  - alta -> email de alta prioridade
  - media -> email de media urgencia
  - baixa -> registro de baixa urgencia

---

## 6. Integracoes

| Servico | Finalidade |
|---------|------------|
| OpenAI | Classificacao e extracao estruturada da demanda |
| Gmail | Encaminhamento de casos alta/media urgencia |
| Data Table (n8n) | Persistencia de classificacao e decisao |

---

## 7. Persistencia e Rastreabilidade

Cada execucao registra `categoria`, `urgencia`, `confianca`, `resumo`, `categoria_final` e `urgencia_final`. O historico pode ser auditado no Data Table e nos logs de execucao do n8n.

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** interromper execucao e registrar erro no n8n para reprocessamento.
- **Entradas invalidas:** campos obrigatorios no formulario (nome, email, assunto, descricao).
- **Fallback (baixa confianca):** regra `confianca < 0.70` com categoria/urgencia seguras.

---

## 9. Diferenciais implementados

- [ ] Memoria de contexto
- [x] Multi-step reasoning
- [ ] Integracao com base de conhecimento na solucao final
- [ ] Uso de embeddings / busca semantica

---

## 10. Limitacoes e Riscos

A classificacao depende da qualidade do texto de entrada e pode falhar em mensagens muito curtas ou ambiguas. Integracoes externas (OpenAI e Gmail) tambem podem falhar e exigem monitoramento.

---

## 11. Como executar

```bash
# 1. Importar workflow no n8n
# arquivo: src/workflows/Sistema de Triagem Automática de Demandas-2.json

# 2. Configurar credenciais OpenAI e Gmail

# 3. Ativar workflow e submeter casos de tests/casos-teste-triagem.csv

# 4. Registrar evidencias em docs/evidence/evidence-log.md
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
- [x] Demonstracao do fluxo (roteiro e log em docs/evidence)
- [x] Relatorio de entrega preenchido
- [ ] Pull Request aberto
