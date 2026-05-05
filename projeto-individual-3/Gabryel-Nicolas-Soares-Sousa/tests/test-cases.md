# Casos de Teste — Triagem Inteligente de Chamados

**Aluno:** Gabryel Nicolas Soares de Sousa | 221022570

---

## Como executar os testes

Envie requisições POST para o webhook do n8n:

```bash
curl -X POST https://seu-n8n.app.n8n.cloud/webhook/triagem \
  -H "Content-Type: application/json" \
  -d '<payload abaixo>'
```

---

## T1 — Alta Urgência (Suporte Técnico)

**Payload:**
```json
{"mensagem": "Meu acesso ao sistema não funciona desde ontem, preciso urgente para apresentação com cliente", "nome": "João Silva", "email": "joao@empresa.com"}
```

**Resultado esperado:**
- `categoria`: suporte_tecnico
- `urgencia`: alta
- `confianca`: alta
- **Ação:** email enviado + registro no Sheets
- **Caminho:** branch "alta urgência"

---

## T2 — Baixa Urgência (Financeiro)

**Payload:**
```json
{"mensagem": "Gostaria de saber o valor da minha fatura do mês passado", "nome": "Maria Souza", "email": "maria@empresa.com"}
```

**Resultado esperado:**
- `categoria`: financeiro
- `urgencia`: baixa
- `confianca`: alta
- **Ação:** apenas registro no Sheets
- **Caminho:** branch "baixa/média urgência"

---

## T3 — Entrada Inválida (Fallback)

**Payload:**
```json
{"mensagem": "oi", "nome": "Teste", "email": "teste@email.com"}
```

**Resultado esperado:**
- `confianca`: baixa
- `categoria`: outros
- **Ação:** registro no Sheets com flag revisao_manual
- **Caminho:** branch "fallback"

---

## T4 — Categoria Comercial

**Payload:**
```json
{"mensagem": "Tenho interesse em contratar o plano enterprise para minha empresa de 50 funcionários", "nome": "Carlos Lima", "email": "carlos@empresa.com"}
```

**Resultado esperado:**
- `categoria`: comercial
- `urgencia`: baixa ou média
- **Ação:** registro no Sheets

---

## T5 — Entrada sem campo mensagem

**Payload:**
```json
{"nome": "Sem Mensagem", "email": "sem@email.com"}
```

**Resultado esperado:**
- Nó "Validar Entrada" bloqueia o fluxo
- **Ação:** redirecionado para fallback antes de chamar a IA
- **Caminho:** branch "fallback" por entrada inválida
