# ADR 001 — Escolha da Solução Final: Triagem Inteligente CDC

**Status:** Aceita

---

##  Contexto

O Projeto Individual 3 exige a construção de uma automação inteligente utilizando **n8n** e agentes de IA.

O cenário escolhido foi a **triagem automatizada de reclamações baseadas no Código de Defesa do Consumidor (CDC)**.

O fluxo final implementado utiliza:

- Webhook/Form Trigger para entrada de dados  
- Agente de IA (Gemini 3 Flash) para análise jurídica e classificação  
- Parsing de Resposta para normalização do JSON  
- Roteamento Condicional (Switch) para direcionar a demanda por categoria  
- Integrações Externas:
  - Telegram (alertas urgentes)
  - Gmail (respostas automatizadas)
  - Google Sheets (persistência e rastreabilidade)

---

##  Problema

Relatos de consumidores podem ser:

- Vagos  
- Complexos  
- Urgentes (ex: corte de serviços essenciais)  

O risco é:

- Tempo de resposta humano elevado  
- Falta de padronização na análise  
- Possível ignorância de artigos relevantes do CDC  

A automação busca:

- Reduzir tempo de resposta  
- Padronizar a triagem inicial  
- Garantir tratamento adequado para casos críticos  

---

## Alternativas Consideradas

###  Solution A — Prompt Simples

Uso de uma única chamada de IA que apenas resume o texto.

**Vantagens:**
- Baixa complexidade  
- Implementação rápida  

**Desvantagens:**
- Não toma decisões automáticas  
- Não separa urgências de dúvidas simples  

---

###  Solution B — Base de Conhecimento (RAG)

Adição de um documento PDF do CDC como contexto fixo para a IA.

**Vantagens:**
- Reduz alucinações sobre artigos de lei  

**Desvantagens:**
- Maior custo computacional  
- Não resolve roteamento multicanal  

---

###  Solution C — Fluxo Agêntico Multicanal (**Escolhida**)

Uso da IA como motor de decisão para rotear o fluxo entre diferentes canais.

**Vantagens:**
- Uso real do n8n como orquestrador  
- Tratamento diferenciado de urgências  
- Alta rastreabilidade via Google Sheets  
- Integração multicanal (Telegram + Gmail)

**Desvantagens:**
- Maior complexidade de configuração  
- Necessidade de parsing e validação de dados  

---

##  Decisão

A solução escolhida foi:

> **Solution C — Fluxo Agêntico Multicanal**

---

##  Justificativa

Esta solução foi adotada por demonstrar claramente o uso da IA como **componente decisório**, e não apenas informativo.

Exemplo:

- Se a IA classifica como **URGENTE**  
  → fluxo direciona para **Telegram (alerta imediato)**  

- Se classifica como **DUVIDA**  
  → fluxo responde automaticamente via **Gmail**  

Isso garante:

- Rapidez no atendimento  
- Uso eficiente de recursos humanos  
- Aderência ao Art. 22 do CDC (serviços essenciais)

---

##  Consequências

- Sistema robusto e próximo de ambiente produtivo  
- Necessidade de monitoramento contínuo da **confiança da IA**  
- Possibilidade de erro de classificação (risco controlado com fallback)

---

##  Critérios de Comparação

| Critério                  | Solution A | Solution B | Solution C |
|--------------------------|------------|------------|------------|
| Inteligência de Roteamento | Inexistente | Baixa      | Alta       |
| Multicanalidade           | Não        | Não        | Sim        |
| Rastreabilidade           | Baixa      | Média      | Alta       |
| Aderência ao Projeto      | Média      | Boa        | Excelente  |