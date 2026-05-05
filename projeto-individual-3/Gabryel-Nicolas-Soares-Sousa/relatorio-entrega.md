# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Gabryel Nicolas Soares de Sousa
> **Matrícula:** 221022570
> **Data de entrega:** 05/05/2025

---

## 1. Resumo do Projeto

Este projeto implementa um sistema de triagem automática de chamados de suporte utilizando o n8n como orquestrador e a API da OpenAI (GPT-3.5-turbo) como agente de classificação. O sistema recebe mensagens de usuários via webhook, utiliza a IA para classificar a demanda por categoria e urgência e retornar um JSON estruturado, e roteia automaticamente o fluxo: chamados urgentes geram notificação por email ao time de suporte, demais chamados são registrados no Google Sheets, e entradas inválidas ou de baixa confiança ativam um caminho de fallback para revisão manual. O resultado é um pipeline completamente automatizado, auditável e rastreável, onde a IA influencia diretamente o roteamento — não apenas gera texto.

---

## 2. Problema Escolhido

Equipes de suporte recebem diariamente mensagens de diferentes naturezas e urgências. A triagem manual é lenta, sujeita a erros humanos e atrasa o atendimento em situações críticas. O sistema automatiza essa etapa inicial: a IA classifica cada chamado e o n8n direciona para o caminho correto sem intervenção humana, garantindo que demandas urgentes sejam escaladas imediatamente e que todas as demandas sejam rastreadas.

Este cenário é relevante por representar um problema real enfrentado por times de TI e atendimento em organizações de diferentes tamanhos, com impacto direto na qualidade e velocidade do serviço prestado.

---

## 3. Desenho do Fluxo

```
[Webhook] → [IF: Validar Entrada] → [HTTP Request: Classificar com IA] → [Code: Extrair JSON]
                                                                                    ↓
                                                                     [Switch: Urgência e Confiança]
                                                                      ├── alta urgência → [Gmail] → [Sheets]
                                                                      ├── baixa confiança → [Sheets Fallback]
                                                                      └── demais → [Sheets Normal]
```

### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Receber Chamado | Webhook | Ponto de entrada; recebe JSON com mensagem, nome e email |
| Validar Entrada | IF | Verifica se o campo `mensagem` existe e não está vazio |
| Classificar com IA | HTTP Request | Envia mensagem à API da OpenAI e recebe JSON de classificação |
| Extrair e Validar JSON da IA | Code (JS) | Faz parse do retorno da IA e valida os campos obrigatórios |
| Switch: Urgência e Confiança | Switch | Roteia o fluxo com base em `urgencia` e `confianca` |
| Enviar Email de Alerta | Gmail | Notifica o time de suporte em casos de alta urgência |
| Registrar no Sheets (Urgente) | Google Sheets | Persiste chamados urgentes com caminho `alta_urgencia` |
| Registrar no Sheets (Normal) | Google Sheets | Persiste chamados de média/baixa urgência |
| Registrar no Sheets (Fallback) | Google Sheets | Persiste casos inválidos ou de baixa confiança |
| Registrar Erro da API | Google Sheets | Persiste falhas na chamada à OpenAI |
| Responder OK | Respond to Webhook | Retorna confirmação ao solicitante |
| Responder Fallback | Respond to Webhook | Retorna aviso de revisão manual ao solicitante |
| Responder Inválido | Respond to Webhook | Retorna erro de validação ao solicitante |

---

## 4. Papel do Agente de IA

- **Modelo/serviço utilizado:** OpenAI GPT-3.5-turbo via HTTP Request
- **Tipo de decisão tomada pela IA:** Classificação de texto + extração estruturada em JSON
- **Como a decisão da IA afeta o fluxo:** O campo `urgencia` determina qual branch do Switch é executado — sem a IA, o fluxo não sabe para onde rotear. O campo `confianca` determina se o chamado segue o fluxo normal ou vai para fallback. A IA é o componente central de decisão: ela não apenas gera texto, ela define o caminho de execução do workflow.

---

## 5. Lógica de Decisão

- **Condição 1 — Urgência Alta + Confiança não baixa:**
  - Caminho A → Email de alerta enviado ao time de suporte + registro no Sheets com caminho `alta_urgencia`

- **Condição 2 — Confiança Baixa:**
  - Caminho B → Registro no Sheets com flag `fallback_revisao_manual`, sem notificação ativa

- **Condição 3 — Demais casos (urgência média/baixa, confiança alta/média):**
  - Caminho C → Apenas registro no Sheets com caminho `normal`

---

## 6. Integrações

| Serviço | Finalidade |
|---------|------------|
| OpenAI API | Classificação e extração de informações da mensagem recebida |
| Google Sheets | Persistência de todos os chamados com timestamp e caminho executado |
| Gmail | Notificação do time de suporte para chamados de alta urgência |

---

## 7. Persistência e Rastreabilidade

Todos os chamados são registrados no Google Sheets independentemente do caminho executado, com as colunas: Timestamp, Nome, Email, Mensagem original, Categoria, Urgência, Resumo, Confiança e Caminho executado. Isso permite auditoria completa: é possível verificar quais chamados foram notificados, quais foram registrados silenciosamente e quais ativaram o fallback, com data e hora de cada execução.

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** O nó HTTP Request tem `onError: continueErrorOutput`, redirecionando falhas para o nó "Registrar Erro da API" no Sheets, sem interromper o sistema.
- **Entradas inválidas:** O nó IF verifica a presença e não-vacuidade do campo `mensagem` antes de chamar a IA. Entradas inválidas são redirecionadas para o fallback diretamente.
- **Fallback (baixa confiança):** Quando a IA retorna `confianca: "baixa"`, o Switch direciona para registro no Sheets com flag `fallback_revisao_manual`. Nenhum email é enviado para evitar notificações incorretas.

---

## 9. Diferenciais implementados

- [ ] Memória de contexto
- [x] Multi-step reasoning — o fluxo executa duas etapas de decisão em sequência: validação da entrada (IF) e avaliação combinada de urgência e confiança (Switch)
- [ ] Integração com base de conhecimento
- [ ] Uso de embeddings / busca semântica

---

## 10. Limitações e Riscos

**Limitações:**
- O sistema não tem memória: cada chamado é processado de forma independente, sem histórico do usuário
- A qualidade da classificação depende do prompt — mensagens ambíguas podem ser mal classificadas
- Não há interface de revisão para chamados de baixa confiança — requer acesso manual ao Sheets

**Riscos:**
- Chamado crítico classificado com urgência baixa não gerará email. Mitigado pelo fallback de baixa confiança e revisão periódica do Sheets.
- Indisponibilidade da OpenAI: capturada pelo tratamento de erro, mas o chamado fica pendente até revisão manual.
- Expiração do OAuth do Gmail: pode interromper notificações silenciosamente.

---

## 11. Como executar

```bash
# 1. Importar o workflow no n8n
# Acesse seu n8n → Workflows → Import from file → selecione src/workflow.json

# 2. Configurar credenciais no n8n
# - OpenAI: Settings → Credentials → New → Header Auth
#   nome: Authorization | valor: Bearer SUA_OPENAI_API_KEY
# - Gmail: Settings → Credentials → New → Gmail OAuth2 → autenticar com Google
# - Google Sheets: Settings → Credentials → New → Google Sheets OAuth2 → autenticar

# 3. Criar planilha no Google Sheets com as colunas:
# Timestamp | Nome | Email | Mensagem | Categoria | Urgência | Resumo | Confiança | Caminho

# 4. Atualizar o ID da sua planilha nos três nós do Google Sheets (campo documentId)

# 5. Ativar o workflow (toggle "Active" no canto superior direito)

# 6. Testar com curl:
curl -X POST https://seu-n8n.app.n8n.cloud/webhook/triagem \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Meu acesso não funciona desde ontem", "nome": "Gabryel", "email": "gabryel@email.com"}'
```

---

## 12. Referências

1. Documentação do n8n: https://docs.n8n.io
2. OpenAI API Reference: https://platform.openai.com/docs/api-reference/chat
3. Google Sheets node (n8n): https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googlesheets/

---

## 13. Checklist de entrega

- [ ] Workflow exportado do n8n (.json) — em `src/workflow.json`
- [ ] Código/scripts auxiliares incluídos — nó Code em `src/workflow.json`
- [ ] Demonstração do fluxo (prints) — em `docs/evidence/`
- [ ] Relatório de entrega preenchido — este arquivo
- [ ] Pull Request aberto
