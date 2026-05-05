# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Carlos Eduardo Rodrigues
> **Matrícula:** 221031265
> **Data de entrega:** 05/05/2026

---

## 1. Resumo do Projeto

Este projeto automatiza a triagem inicial de artigos científicos recebidos por meio de um webhook, aplicando extração de metadados, validação de DOI e decisões de roteamento para apoio à curadoria. Um agente de IA é usado para classificar o artigo quanto à relevância temática, extrair tópicos e gerar um sumário curto; seus sinais são combinados com validação automática (Crossref) e regras de negócio para decidir se o artigo segue para revisão humana, busca semântica (RAG) ou publicação direta. Como resultado principal, o fluxo reduz trabalho manual, padroniza logs de decisão e envia notificações e evidências para um canal de auditoria (Telegram Bot).

## 2. Problema Escolhido

Organizar e priorizar artigos para triagem editorial consome tempo e depende de decisões repetitivas e subjetivas. Automação melhora consistência e velocidade: o sistema classifica relevância temática, valida DOI e identifica casos de baixa confiança que precisam de revisão humana. Isso é útil para eventos, periódicos ou equipes de revisão que recebem grande volume de submissões.

## 3. Desenho do Fluxo

## Workflow Solução A
![a](docs/evidence/imgs/solution-a.png)

## Workflow Solução B
![b](docs/evidence/imgs/solution-b.png)

## Workflow Solução C
![c](docs/evidence/imgs/solution-c-2.png)




### 3.1 Nós utilizados
### Solução A

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Webhook Trigger | n8n-nodes-base.webhook | Recebe requisições POST em `/article-triage` (entrada do fluxo). |
| Normalize Input | n8n-nodes-base.function | Normaliza e extrai campos do payload (título, resumo, DOI, keywords). |
| AI Classification | n8n-nodes-base.httpRequest | Chama a API do modelo generativo para classificar e estimar confiança. |
| Parse AI Output | n8n-nodes-base.function | Parseia a resposta do modelo e calcula decisão/confiança. |
| Route Decision | n8n-nodes-base.switch | Roteia para aprovação, revisão ou rejeição com base na decisão. |
| Send a text message / Send a text message1 / Send a text message2 | n8n-nodes-base.telegram | Envia notificações para o canal do Telegram (aprovado / revisão / rejeitado). |

### Solução B

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Webhook Trigger | n8n-nodes-base.webhook | Recebe requisições POST em `/article-triage-rag`. |
| Normalize Input | n8n-nodes-base.function | Normaliza e prepara o payload para busca e classificação. |
| Local Retriever | n8n-nodes-base.httpRequest | Consulta o retriever local (`/search`) para contexto RAG. |
| AI RAG Classification | n8n-nodes-base.httpRequest | Chama o modelo generativo com contexto do retriever para classificação. |
| Parse RAG Output | n8n-nodes-base.function | Parseia a resposta do modelo RAG e normaliza confiança/decisão. |
| Route RAG | n8n-nodes-base.switch | Roteia para as ações finais conforme decisão. |
| Telegram Review / Telegram Reject / Telegram Store | n8n-nodes-base.telegram | Notificações para revisão, rejeição ou armazenamento. |

### Solução C

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Webhook Trigger | n8n-nodes-base.webhook | Recebe requisições POST em `/article-triage-full`. |
| Validate & Normalize | n8n-nodes-base.function | Valida presença de título/resumo e normaliza campos. |
| AI Classification | n8n-nodes-base.httpRequest | Solicita classificação ao modelo generativo. |
| Parse AI | n8n-nodes-base.function | Parseia saída do modelo e combina com o payload original. |
| Has DOI? | n8n-nodes-base.switch | Verifica se há DOI e decide caminho (validar DOI ou pular). |
| Validate DOI | n8n-nodes-base.httpRequest | Consulta a API do Crossref para validar o DOI. |
| Recalc Confidence | n8n-nodes-base.function | Recalcula a confiança final combinando sinais (IA, DOI, metadados). |
| Final Router | n8n-nodes-base.switch | Roteia para notificação adequada (store / review / reject). |
| Telegram Review / Telegram Reject / Telegram Store | n8n-nodes-base.telegram | Envia mensagem final ao Telegram com o resultado. |


## 4. Papel do Agente de IA
- **Tipo de decisão tomada pela IA:** Classificação de relevância, extração de tópicos/resumo, e estimativa de confiança.
- **Como a decisão da IA afeta o fluxo:** A pontuação e a confiança geradas pela IA são usados para decidir se o artigo deve ser: aceito automaticamente, rejeitado ou notificado para revisão humana.


## 5. Lógica de Decisão

- Regras gerais usadas em todas as soluções:
	- `confidence >= 0.70` → aceitar/`store` (notificação de sucesso).
	- `0.50 <= confidence < 0.70` → solicitar revisão humana (`request_human_review`).
	- `confidence < 0.50` → rejeitar (`reject`).

### Solução A
- Entrada -> modelo gera `classification` e `confidence`.
- Ação: aplica os limiares gerais acima e usa `Route Decision` para:
	- `store`: enviar `Send a text message` (aprovado).
	- `request_human_review`: enviar `Send a text message1` (revisão).
	- `reject`: enviar `Send a text message2` (rejeitado).

### Solução B
- Adiciona contexto do `Local Retriever` antes de chamar o modelo.
- Ajuste de decisão: quando o retriever retorna contexto relevante e a confiança do modelo for média, o fluxo tende a favorecer `request_human_review` + enriquecimento via RAG para fornecer justificativa; se o contexto aumentar a confiança, pode evoluir para `store`.
- Ação: `Route RAG` decide entre `Telegram Review`, `Telegram Reject` e `Telegram Store`.

### Solução C
- Combina sinais (IA, validação Crossref, completude de metadados) em `Recalc Confidence`.
	- `final_confidence >= 0.75` → `store` (notificar `Telegram Store`).
	- `0.50 <= final_confidence < 0.75` → `request_human_review` (notificar `Telegram Review`).
	- `final_confidence < 0.50` → `reject` (notificar `Telegram Reject`).


## 6. Integrações
| Serviço | Finalidade |
|---------|------------|
| `Telegram Bot` | Canal de auditoria e notificações. |
| `Crossref` | Validação de DOI e metadados bibliográficos. |
| `Modelo Generativo (Gemini)` | Classificação, extração de tópicos e sumarização. |
| `Retriever local` | Fonte de conhecimento para RAG (`src/solution-b-retriever.js`). |

## 7. Persistência e Rastreabilidade

Cada execução do workflow fica registrada na interface do n8n com timestamp, duração e estado (success/error). Ao abrir uma execução é possível inspecionar os dados de cada nó — entradas, saídas e respostas HTTP — permitindo reconstruir o fluxo de processamento (payload recebido, chamada ao modelo, resultado da verificação DOI, decisão final, etc.).


## 8. Tratamento de Erros e Limites

- **Parse inválido do modelo:** Nós `Parse AI Output` (solução A/C) e `Parse RAG Output` (solução B) contêm try/catch. Se a resposta do modelo for JSON malformado, retorna fallback com `confidence=0.5`, `decision='request_human_review'` e `reason='Parse error'`, encaminhando para revisão.

- **Entradas inválidas:** Solução C valida no nó `Validate & Normalize`, se faltar `title` ou `abstract`, retorna imediatamente `decision='reject'` e `reason='Missing required fields'`, interrompendo o fluxo e notificando rejeição via Telegram.

- **Falhas de serviço (Crossref/Modelo):** Solução C usa `onError: 'continueRegularOutput'` no nó `Validate DOI` para evitar crash se a API falhar; o fluxo continua e recalcula confiança sem o sinal de DOI (peso reduzido).

- **Thresholds de confiança:** Todas as soluções usam limiares rígidos para evitar decisões ambíguas.

## 9. Diferenciais implementados
- [ ] Memória de contexto
- [x] Multi-step reasoning
- [x] Integração com base de conhecimento
- [ ] Uso de embeddings / busca semântica

## 10. Limitações e Riscos

Limitações incluem dependência da qualidade do modelo de IA e cobertura da base de conhecimento local. Riscos: classificações incorretas (falsos positivos/negativos), falhas no serviço de terceiros (Crossref ou API do modelo).

## 11. Como executar

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

### 4. Rodar Servidor Auxiliar (Solution B)

Se for testar Solution B, inicie o servidor local em outro terminal:

```bash
# A partir da raiz do projeto
node src/solution-b-retriever.js
```

### 5. Testar via Webhook


```bash
# Solution A
curl -X POST http://localhost:5678/webhook-test/article-triage \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chatbots in Customer Service",
    "abstract": "This study evaluates...",
    "keywords": ["AI", "CX", "chatbots"]
  }'

# Solution B
curl -X POST http://localhost:5678/webhook-test/article-triage-rag \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Chatbots in Customer Service",
    "abstract": "This study evaluates...",
    "keywords": ["AI", "CX", "chatbots"]
  }'

# Solution C
curl -X POST http://localhost:5678/webhook-test/article-triage-full \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Array programming with NumPy",
    "abstract": "This paper discusses...",
    "doi": "10.1038/s41586-020-2649-2",
    "keywords": ["numpy", "python", "scientific computing"]
  }'
```

## 12. Referências
1. Documentação do n8n: https://docs.n8n.io/


## 13. Checklist de entrega
- [x] Workflow exportado do n8n (.json)
- [x] Código/scripts auxiliares incluídos
- [x] Demonstração do fluxo (vídeo ou prints)
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
