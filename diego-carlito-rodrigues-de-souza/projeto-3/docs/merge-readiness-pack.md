# Merge-Readiness Pack

> **Projeto:** Assistente de Monitoria Universitária Autônomo
> **Aluno(a):** Diego Carlito Rodrigues de Souza
> **Data:** 05/05/2026

---

## 1. Resumo da solução escolhida

Foi implementada uma arquitetura agêntica de **Roteamento Híbrido (Solução C)** utilizando o n8n Cloud para orquestração. A entrada de dados ocorre via **Telegram Trigger**, proporcionando uma interface acessível ao aluno. O núcleo de inteligência usa um nó de *Information Extractor* conectado à API da Groq (Llama3.1-8b-instant), forçado por um **JSON Schema estrito** a classificar as intenções em três categorias exatas (`tecnica`, `administrativa`, `excecao`). 

Um nó `Switch` atua como guarda de trânsito: 
- Dúvidas técnicas acionam um sub-agente LLM instruído sob o **Método Socrático** (que guia sem dar código pronto).
- Dúvidas administrativas e exceções disparam respostas estáticas predefinidas, economizando tokens e eliminando o risco de alucinações sobre regras da disciplina.

---

## 2. Comparação entre as três alternativas

| Critério | Solution A (LLM Único/Monolítico) | Solution B (Classificador Regex/Keywords + LLM) | Solution C (LLM Router + Roteamento n8n) |
|----------|-----------|-----------|-----------|
| **Abordagem** | Um único prompt gigante lidando com tudo. | Regras rígidas (if/else) para triagem, IA para responder. | LLM extrai intenção (JSON), orquestrador divide fluxos. |
| **Custo** | Alto (gasta tokens processando regras a cada chamada). | Muito Baixo. | Médio/Baixo (tokens apenas na triagem e na rota técnica). |
| **Complexidade** | Baixa. | Média (manter dicionário de palavras-chave é custoso). | Alta (requer engenharia de prompt e orquestração). |
| **Qualidade da resposta** | Inconsistente (alta chance de alucinar regras e datas). | Baixa (falsa classificação por sinônimos). | Excelente (isola o contexto de cada sub-tarefa). |
| **Riscos** | *Prompt Injection* e desobediência do Método Socrático. | Quebra de fluxo quando o aluno usa gírias ou erros de digitação. | Dependência da estabilidade da API de triagem. |
| **Manutenibilidade** | Ruim (mexer no prompt quebra outras áreas). | Ruim (código engessado). | Excelente (módulos isolados, fácil plugar BDs futuramente). |
| **Adequação ao problema** | Baixa. | Média. | Alta (atende o requisito agêntico com precisão). |

**Solução escolhida:** Solução C

**Justificativa:** A separação de responsabilidades (SoC - *Separation of Concerns*) garante que a IA seja usada apenas onde a semântica é necessária (classificação de intenção e tutoria técnica), enquanto o n8n lida com a lógica de negócios e persistência. Isso mitigou os falsos positivos, comprovado através do *Prompt Tuning* realizado durante os testes.

---

## 3. Testes executados

| Teste | Descrição | Resultado |
|-------|-----------|-----------|
| **Triagem Técnica** | Aluno envia: "Meu loop while em Python não para de rodar, me dá o código certo?". Validação do roteamento para `Output 0` e recusa da IA em entregar o código, devolvendo perguntas guiadoras. | Passou |
| **Triagem Administrativa** | Aluno envia: "Qual é a data limite para entregar a documentação?". Validação do roteamento para `Output 1` e envio de mensagem fixa de registro, sem uso de LLM para resposta. | Passou |
| **Triagem de Exceção** | Aluno envia: "Peguei dengue/Meu computador queimou e perdi o projeto". Validação do roteamento para `Output 2` e disparo do alerta vermelho de escalonamento ao professor. | Passou |
| **Blindagem de JSON** | Inserção de bloqueios no prompt para evitar Markdown e caracteres especiais/acentos na estruturação de chaves do n8n. | Passou |

---

## 4. Evidências de funcionamento

As seguintes evidências foram consolidadas e anexadas ao repositório:

- [`docs/evidence/fluxo-n8n-final.png`](evidence/fluxo-n8n-final.png): Captura do canvas do n8n com a arquitetura completa (Telegram Trigger, Extractor, Switch, Sub-agentes).
- [`docs/evidence/evidencia-telegram.png`](evidence/evidencia-telegram.png): Teste de aceitação real na interface do Telegram provando o roteamento correto para os 3 cenários (Técnico, Administrativo, Exceção).
- [`docs/evidence/evidencia-extracao-json.png`](evidence/evidencia-extracao-json.png): Auditoria do Output do nó *Information Extractor* validando a obediência ao JSON Schema restrito.
- [`docs/evidence/evidencia-historico-execucoes.png`](evidence/evidencia-historico-execucoes.png): Histórico de painel (Logs) comprovando estabilidade e *Success* rate na execução dos webhooks.

---

## 5. Limitações conhecidas

- **Rate Limits da API:** O plano gratuito da Groq possui limitações de requisições por minuto que podem criar gargalos em épocas de provas.
- **Armazenamento Volátil:** A rota administrativa atualmente responde ao usuário, mas o nó do Google Sheets (mockado) precisa de credenciamento definitivo para persistência real dos dados da disciplina.

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Downtime da API da Groq | Média | Alto | Implementar um nó de *Error Trigger* no n8n que avisa o aluno: "Sistema indisponível no momento". |
| Alucinação no JSON de roteamento | Baixa | Médio | Uso de JSON Schema com `description` explícita reforçando a classificação de cada contexto e proibição de acentuação. |
| *Jailbreak* do Método Socrático | Baixa | Médio | Prompt de sistema agressivo limitando o papel ("NUNCA escreva blocos de código com a solução"). |

---

## 7. Decisões arquiteturais

- **[ADR-001: Adoção de Arquitetura Agêntica Híbrida para Triagem](adr/001-escolha-da-solucao.md):** Escolha da Alternativa C (LLM como roteador semântico + n8n como executor determinístico) para isolar o comportamento probabilístico da IA das lógicas de negócio.
- **Integração de Interface (UI):** Substituição do Webhook HTTP direto por um *Telegram Trigger* para prover uma interface nativa e de fácil acesso aos alunos.
- **Governança do Modelo (Prompt Engineering):** Aplicação do Método Socrático na rota técnica para evitar a entrega de código pronto, e uso de JSON Schema estrito no classificador para evitar quebras no roteamento do n8n.

---

## 8. Instruções de execução

```bash
# Passos para executar a solução final localmente/nuvem

# 1. Acesse a pasta
cd diego-carlito-rodrigues-de-souza/projeto-3

# 2. Acesse o n8n e importe o fluxo final
# Menu -> Workflows -> Import from File -> Selecione "src/workflow.json"

# 3. Configure as Credenciais
# - Crie/atualize a credencial "Telegram account" com o Token do BotFather.
# - Crie/atualize a credencial da API da Groq.

# 4. Ative o Workflow
# Mude o toggle superior direito de "Inactive" para "Active".
# Interaja com o bot diretamente via Telegram.

# 5. (Opcional) Teste via Terminal
# Caso não queira usar o celular, insira seu Token e Chat ID no script e rode:
chmod +x src/testar-bot.sh
./src/testar-bot.sh
```

---

## 9. Checklist de revisão

- [x] Mission brief atendido
- [x] Três soluções implementadas/prototipadas (Documentadas no Item 2)
- [x] Testes executados e documentados
- [x] Evidências registradas em `docs/evidence/`
- [x] ADR registrado em `docs/adr/`
- [x] Commits com mensagens claras e racionalidade
- [x] Código funcional em `src/workflow.json`
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido

---

## 10. Justificativa para merge

A entrega cumpre integralmente os requisitos de construção de uma arquitetura agêntica estabelecidos no projeto de disciplina. A transição de um *Webhook* genérico para uma interface em tempo real no Telegram eleva o rigor da solução. Além disso, os testes empíricos de *Prompt Tuning* provam a maturidade no manuseio de LLMs (evitando alucinações e erros de syntaxe JSON). O código, a orquestração e as evidências estão coesos e devidamente documentados, tornando a solução estável e pronta para avaliação (ou integração em um cenário real da UnB).
