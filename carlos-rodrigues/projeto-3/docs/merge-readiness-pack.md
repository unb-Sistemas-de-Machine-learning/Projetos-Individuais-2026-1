# Merge-Readiness Pack

> **Projeto:** Curadoria Automática de Artigos Científicos
> **Aluno(a):** Carlos Eduardo Rodrigues
> **Data:** 05/05/2026

---

## 1. Resumo da solução escolhida

A solução final (`solution-c`), que implementa um pipeline em múltiplas etapas com validação de DOI (Crossref), recálculo de confiança e roteamento final para `store`, `request_human_review` ou `reject`, sempre com notificação via Telegram Bot.

---

## 2. Comparação entre as três alternativas

| Criterio | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| **Abordagem** | Prompt único com classificação direta | RAG com retriever local | Pipeline multi-etapas com validação externa |
| **Custo** | Baixo | Medio | Medio |
| **Complexidade** | Baixa | Media | Alta |
| **Qualidade da resposta** | Boa em casos simples | Melhor contexto temático | Melhor equilíbrio entre precisão e controle |
| **Riscos** | Maior erro em casos ambíguos | Dependência da base vetorial | Mais passos para configurar |
| **Manutenibilidade** | Alta | Média | Média |
| **Adequação ao problema** | Parcial | Boa | Excelente |

**Solução escolhida:** C

**Justificativa:**

O problema proposto exige mais do que classificação textual. É necessário validar metadados, controlar incerteza e garantir auditabilidade. A `solution-c` atende melhor esse conjunto de requisitos.

---

## 3. Testes executados

| Teste | Descricao | Resultado |
|-------|-----------|-----------|
| JSON Output Validation | Valida estrutura de saída da IA |  Passou |
| Low Confidence Routing | Confiança < 0.6 vai para revisão humana |  Passou |
| Incomplete Metadata | Entrada incompleta gera tratamento controlado |  Passou |
| DOI Validation (S-C) | DOI inválido reduz confiança final |  Passou |
| Semantic Search (S-B) | Recuperação via retriever local retorna similares |  Passou |
| Conditional Routing | Classificações geram caminhos distintos |  Passou |
| Sheet Persistence | Decisões notificadas via Telegram Bot |  Passou |

---

## 4. Evidências de funcionamento

## Solution A - Prompt Simples

![Workflow A](../docs/evidence/imgs/solution-a.png)

![Teste via Curl A](../docs/evidence/imgs/solution-a-curl.png)

![Notificação Telegram A](../docs/evidence/imgs/solution-a-msg.png)

---

## Solution B - RAG com Retriever Local

![Workflow B](../docs/evidence/imgs/solution-b.png)

![Teste via Curl B](../docs/evidence/imgs/solution-b-curl.png)

![Servidor Local](../docs/evidence/imgs/solution-b-server.png)

![Notificação Telegram B](../docs/evidence/imgs/solution-b-msg.png)

---

## Solution C - Multi-etapas com Validação DOI (Chosen)

![Workflow C Parte 1](../docs/evidence/imgs/solution-c-1.png)

![Workflow C Parte 2](../docs/evidence/imgs/solution-c-2.png)

![Teste via Curl C](../docs/evidence/imgs/solution-c-2-curl.png)

---

## 5. Limitações conhecidas

- Desempenho depende da qualidade de título/resumo.
- Soluções A e B são menos robustas em casos de fronteira.
- Solução C exige mais configuração inicial (Crossref + regras de confiança).

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Classificação incorreta por contexto insuficiente | Média | Alto | Escalar casos de baixa confiança |
| Metadados incompletos | Média | Médio | Validar e registrar falhas de entrada |
| Alucinação do modelo | Média | Alto | Regras de parse e validação externa |

---

## 7. Decisões arquiteturais

- ADR-001: [ADR-001: Escolha da solução para curadoria automática de artigos científicos](../docs/adr/001-escolha-da-solucao.md).

---

## 8. Instruções de execução

### 1. Instalar e Rodar n8n

```bash
# Opção 1: Docker
docker run -it --rm \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=false \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n:latest

# Opção 2: npm
npm install -g n8n
n8n start
```

Acesse: `http://localhost:5678`

### 2. Obter Google Gemini API Key

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada
5. Copiar e guardar como `<API_GEMINI>`

### 3. Configurar Telegram Bot

1. Abra o Telegram e procure por **@BotFather**
2. Envie `/newbot` e siga as instruções
3. Copie o **Bot Token**
4. Obtenha seu **Chat ID**:
   ```bash
   curl https://api.telegram.org/bot<SEU_TOKEN>/getMe
   ```
5. Guardar como `<CODIGO_CHAT_TELEGRAM>`


### 4. Testar via Webhook


```bash
curl -X POST http://localhost:5678/webhook-test/article-triage-full \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Array programming with NumPy",
    "abstract": "This paper discusses...",
    "doi": "10.1038/s41586-020-2649-2",
    "keywords": ["numpy", "python", "scientific computing"]
  }'
```

---

## 9. Checklist de prontidão

- [x] Mission brief atendido
- [x] Três soluções implementadas/prototipadas
- [x] Testes executados e documentados
- [x] Evidências registradas em `docs/evidence/`
- [x] ADR(s) registrado(s) em `docs/adr/`
- [x] Commits com mensagens claras e racionalidade
- [x] Código funcional em `src/`
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido

---

## 10. Justificativa para merge

A base está consistente entre requisitos, implementação e evidências. O projeto atende ao escopo da disciplina com rastreabilidade e controle de confiança.