# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Diego Carlito Rodrigues de Souza
> **Matrícula:** 221007690
> **Data de entrega:** 05/05/2026

---

## 1. Resumo do Projeto

O projeto automatiza a triagem e o atendimento inicial da monitoria acadêmica de Engenharia de Software da UnB. Utiliza um agente de IA (Llama3 via Groq) como roteador semântico para classificar as intenções dos alunos e orquestrar o fluxo no n8n. O principal resultado é a separação eficiente entre dúvidas técnicas (resolvidas via Método Socrático pela IA), burocráticas (resolvidas por mensagens fixas) e exceções críticas (escaladas ao professor), garantindo conformidade pedagógica e eficiência operacional.

---

## 2. Problema Escolhido

O cenário escolhido é a sobrecarga de monitores e professores com dúvidas repetitivas ou inadequadas. Em disciplinas de programação, é comum que alunos peçam códigos prontos (o que fere o aprendizado) ou misturem emergências médicas com dúvidas simples. A automação é relevante pois garante que cada demanda receba o tratamento correto: tutoria educativa para técnica e escala humana para casos sensíveis.

---

## 3. Desenho do Fluxo

O fluxo foi desenhado para ser resiliente e modular, utilizando o Telegram como interface primária.

```
Telegram Trigger → Information Extractor (IA) → Switch (Roteador) → [Rota 0: IA Socrática] / [Rota 1: Msg Administrativa] / [Rota 2: Msg Exceção] → Telegram (Resposta Final)
```

### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| **Telegram Trigger** | Trigger | Inicia o fluxo ao receber uma mensagem do aluno no bot. |
| **Information Extractor** | AI Agent | Analisa a mensagem e gera um JSON com a categoria e o assunto. |
| **Switch** | Logic | Lê a chave `route_to` do JSON e direciona para um dos 3 caminhos. |
| **Socratic Mentor (AI)** | AI Agent | Sub-agente que gera perguntas guiadoras para dúvidas técnicas. |
| **Telegram Send** | Action | Envia a resposta final (IA ou fixa) de volta ao chat do aluno. |

---

## 4. Papel do Agente de IA

A IA atua como o "cérebro analítico" do sistema, não apenas gerando texto, mas definindo o destino lógico de cada execução.

- **Modelo/serviço utilizado:** Llama3-70b-8192 via Groq Cloud.
- **Tipo de decisão tomada pela IA:** Classificação de intenção e roteamento semântico.
- **Como a decisão da IA afeta o fluxo:** Se a IA classificar como `tecnica`, o fluxo consome créditos de LLM para tutoria; se for `administrativa` ou `excecao`, o n8n ignora a geração de texto da IA e envia respostas determinísticas salvas no sistema.

---

## 5. Lógica de Decisão

O roteamento é baseado no valor extraído pela IA para a variável `route_to`:

- **Condição 1: `route_to == tecnica`**
  - Caminho A → Aciona o Mentor Socrático para guiar o aluno no erro de código.
- **Condição 2: `route_to == administrativa`**
  - Caminho B → Envia mensagem fixa informando que a dúvida foi registrada para o professor.
- **Condição 3: `route_to == excecao`**
  - Caminho C → Envia alerta prioritário e orientações sobre atestados/emergências.

---

## 6. Integrações

| Serviço | Finalidade |
|---------|------------|
| **Telegram API** | Interface de chat em tempo real com o aluno (Entrada e Saída). |
| **Groq Cloud** | Provedor de inferência de LLM de baixa latência para o roteador e mentor. |

---

## 7. Persistência e Rastreabilidade

O fluxo utiliza o painel de **Executions** do n8n para auditoria total, permitindo visualizar o JSON gerado pela IA em cada etapa. Entradas administrativas são preparadas para persistência em Google Sheets (configurado como mock na entrega final).

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** Uso de JSON Schema estrito para evitar que o modelo retorne formatos inválidos que travariam o Switch.
- **Entradas inválidas:** O nó de extração possui instruções para classificar entradas irreconhecíveis como `administrativa` por padrão (fallback de segurança).
- **Fallback (baixa confiança):** Implementado via prompt de sistema que obriga a IA a declarar o nível de confiança; valores "baixos" podem ser encaminhados para a rota de exceção.

---

## 9. Diferenciais implementados

- [x] Multi-step reasoning (Separação entre classificação e resposta)
- [ ] Memória de contexto
- [ ] Integração com base de conhecimento
- [ ] Uso de embeddings / busca semântica

---

## 10. Limitações e Riscos

A principal limitação é a dependência da semântica: se um aluno usar sarcasmo extremo, a IA pode classificar uma dúvida técnica como administrativa. Existe também o risco de *rate limit* da API gratuita da Groq durante períodos de alta demanda (ex: véspera de prova).

---

## 11. Como executar

```bash
# 1. Importar o workflow no n8n utilizando o arquivo src/workflow.json
# 2. Configurar as credenciais 'Telegram Account' e 'Groq API' no painel do n8n
# 3. Ativar o workflow no toggle superior direito
# 4. Enviar uma mensagem de teste (ex: "Como funciona o loop for?") para o bot no Telegram
# 5. Alternativamente, rodar o script ./src/testar-bot.sh no terminal
```

---

## 12. Referências

1. Documentação oficial do n8n: [https://docs.n8n.io/](https://docs.n8n.io/)
2. API de Bots do Telegram: [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
3. Groq Cloud Documentation: [https://console.groq.com/docs](https://console.groq.com/docs)

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (.json) em `src/`
- [x] Código/scripts auxiliares incluídos (`testar-bot.sh`)
- [x] Demonstração do fluxo (prints em `docs/evidence/`)
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
