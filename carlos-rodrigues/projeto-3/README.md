# Projeto 4 - Curadoria Automática de Artigos Científicos

**Aluno:** Carlos Eduardo Rodrigues  
**Matrícula:** 221031265  


Sistema de curadoria automática de artigos científicos implementado em n8n com três abordagens diferentes (simples, RAG, robusto). O agente classifica artigos por relevância, valida metadados, controla confiança e escalona para revisão humana quando necessário.

O fluxo recebe novos artigos por webhook, classifica relevância com IA, extrai campos estruturados, aplica regras de decisão e notifica o resultado via Telegram Bot para revisão humana, aprovação ou descarte.

---

## Como Executar

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