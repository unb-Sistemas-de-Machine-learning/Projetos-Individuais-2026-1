# Workflow Runbook

> **Projeto:** IssueTriageBot
> **Aluno(a):** Felipe Amorim de Araújo

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar pelo menos um commit com mensagem descritiva e racionalidade.

### Etapa 1: Ler o Mission Brief

- [ ] Ler e compreender o mission brief
- [ ] Identificar entradas, saídas e restrições
- [ ] Anotar dúvidas ou ambiguidades

### Etapa 2: Propor três soluções possíveis

- [ ] Descrever solution-a (zero-shot prompt — enviar dados da issue ao Gemini e pedir JSON direto)
- [ ] Descrever solution-b (base de conhecimento — carregar `knowledge-base.json` com issues classificadas anteriormente e injetar exemplos relevantes no prompt em tempo de execução)
- [ ] Descrever solution-c (multi-etapas com validação — chamar Gemini, validar schema JSON, retry em caso de saída inválida, fallback com `ai_flagged=true`)

### Etapa 3: Registrar cada solução em pasta separada

- [ ] Criar `docker-compose.yml` na raiz do projeto para subir o n8n localmente
- [ ] Criar `solutions/solution-a/`
- [ ] Criar `solutions/solution-b/`
- [ ] Criar `solutions/solution-c/`

### Etapa 4: Implementar protótipos mínimos

- [ ] Implementar protótipo da solution-a (`solutions/solution-a/utils.js` + workflow n8n exportado)
- [ ] Implementar protótipo da solution-b (`solutions/solution-b/utils.js` + workflow n8n exportado)
- [ ] Implementar protótipo da solution-c (`solutions/solution-c/utils.js` + workflow n8n exportado)

### Etapa 5: Executar testes e validação

**5a — Testes unitários (utils.js)**

- [ ] Criar testes Jest em `tests/solution-a/`, `tests/solution-b/`, `tests/solution-c/`
- [ ] Executar `npm test` e salvar saída em `docs/evidence/<solution>/jest-output.txt`
- [ ] Todos os testes devem passar antes de avançar para a validação integrada

**5b — Validação end-to-end (GitHub → n8n → Gemini → Slack + Sheets)**

Para cada solução, executar o fluxo completo com integrações reais antes de descartá-la:

**Setup (uma vez por solução):**
- [ ] Subir o ambiente: `docker-compose up -d`
- [ ] Em outro terminal, iniciar o tunnel: `ngrok http 5678`
- [ ] Copiar a URL pública gerada pelo ngrok (formato `https://<random>.ngrok-free.app`) — ela muda a cada restart do ngrok
- [ ] Importar o workflow `.json` da solução no n8n e ativar o workflow
- [ ] Criar um repositório de teste no GitHub (ex: `issuetriagebot-test-<solution>`)
- [ ] Registrar um webhook no repositório de teste: URL = `<ngrok-url>/webhook/github-issues`, evento = `Issues`, content type = `application/json`
  - **Atenção:** a URL do ngrok muda a cada restart — se reiniciar o ngrok, atualize o webhook no GitHub antes de testar novamente
- [ ] Confirmar que as credenciais Gemini, Slack e Google Sheets estão configuradas no n8n
- [ ] _(Contexto: o tunnel nativo do n8n `N8N_TUNNEL_ENABLED` foi removido na v2.x — ver ADR-001)_

**Execução dos casos de teste:**
- [ ] Abrir issue no repositório de teste com título `"[TEST] App crashes on login"` e corpo descritivo → deve rotear para `#incidents` (critical) ou `#backlog` (bug não-crítico) e gerar linha no Sheets
- [ ] Abrir issue com título `"[TEST] Add dark mode support"` → deve rotear para `#backlog` como `feature` e gerar linha no Sheets
- [ ] Abrir issue com título `"[TEST] How do I reset my password?"` → deve rotear para `#questions` e gerar linha no Sheets
- [ ] Para a solution-c: configurar key Gemini inválida, abrir issue, confirmar que `ai_flagged=true` aparece na linha do Sheets e que o fallback é roteado corretamente
- [ ] Medir o tempo entre a criação da issue no GitHub e a mensagem aparecer no Slack — deve ser < 30s

**Evidências obrigatórias em `docs/evidence/<solution>/`:**
- `jest-output.txt` — saída completa do `npm test`
- `github-webhook-delivered.png` — tela de "Recent Deliveries" do webhook no GitHub (200 OK)
- `slack-incidents.png` — screenshot do canal `#incidents` com a mensagem recebida
- `slack-backlog.png` — screenshot do canal `#backlog` com a mensagem recebida
- `slack-questions.png` — screenshot do canal `#questions` com a mensagem recebida
- `sheets-rows.png` — screenshot do Google Sheets com as linhas geradas
- `sheets-ai-flagged.png` — screenshot da linha com `ai_flagged=true` (obrigatório na solution-c)
- `n8n-execution-log.png` — screenshot do execution log do n8n com os nós bem-sucedidos

> **Critério de aceitação por solução:** webhook entregue pelo GitHub (200 OK), mensagens nos 3 canais Slack, linhas no Sheets, latência < 30s medida. Testes Jest passando sozinhos não validam a solução.

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo — 1 call/issue, prompt mínimo | Médio — 1 call/issue com prompt maior + custo de manter a base | Médio — até 2 calls/issue no retry path |
| Complexidade | Baixa — apenas prompt + parse | Média — requer criação e manutenção do `knowledge-base.json` | Alta — validação de schema + retry + fallback |
| Qualidade da resposta | Baseline — depende do modelo sem guia | Melhor — exemplos reais de issues classificadas guiam o modelo | Alta — validação garante JSON sempre válido |
| Riscos | Saída malformada sem validação | Base desatualizada ou enviesada degrada a qualidade | Maior latência no retry path |
| Manutenibilidade | Alta — prompt simples de ajustar | Média — base precisa de curadoria contínua | Baixa — mais código, mais pontos de falha |
| Adequação ao problema | Aceitável para MVP | Boa para consistência de classificação com exemplos reais | Ótima para produção robusta |

### Etapa 7: Escolher uma solução final

- [ ] Solução escolhida: 
- [ ] Justificativa: 

### Etapa 8: Registrar a decisão em ADR

- [ ] Criar `docs/adr/XXX-escolha-da-solucao.md` seguindo o template abaixo
- [ ] Confirmar que a decisão cita evidências de `docs/evidence/` — ADR sem evidência não é válido
- [ ] Verificar se alguma outra decisão técnica tomada durante o projeto exige ADR adicional (ver regras abaixo)

**Template obrigatório:**

```markdown
# ADR-NNN: [Título curto da decisão]

## Status
Aceito | Em discussão | Substituído por ADR-XXX

## Contexto
[Qual problema ou restrição motivou esta decisão? Qual era a pressão do mission-brief?]

## Alternativas consideradas
| Opção | Prós | Contras |
|-------|------|---------|
| ... | ... | ... |

## Decisão
[O que foi decidido e por quê — deve citar resultados mensuráveis dos testes, não preferência subjetiva]

## Consequências
[O que muda, o que fica mais difícil, o que fica mais fácil com esta escolha]

## Evidências
[Arquivos em docs/evidence/ que fundamentam a decisão — ex: comparação de latência, screenshot de execução]
```

**Quando criar um ADR além do ADR-001:**
- Qualquer escolha de design que tinha mais de uma alternativa viável (ex: formato do prompt, estrutura do JSON de saída, estratégia de retry)
- Qualquer restrição do mission-brief que forçou uma troca explícita (ex: latência vs. robustez)
- Qualquer incerteza registrada em commit que foi resolvida pelos testes — o ADR fecha o ciclo

### Etapa 9: Gerar o Merge-Readiness Pack

- [ ] Preencher `docs/merge-readiness-pack.md`

### Etapa 10: Fazer commits separados por etapa

- [ ] Verificar que cada etapa tem pelo menos um commit
- [ ] Verificar que cada commit contém racionalidade da decisão
