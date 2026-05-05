# Merge-Readiness Pack

> **Projeto:** Triagem de suporte técnico (n8n + IA)
> **Aluno(a):** Patricia Helena Macedo da Silva
> **Matrícula:** 221037993

> **Data:** 05/05/2026

---

## 1. Resumo da solução escolhida

Automação no **n8n** que recebe chamados via **Webhook**, classifica com **Google Gemini** (JSON estruturado), lê **FAQs** no **Google Sheets**, gera **orientação** contextual em segunda chamada quando aplicável, **registra** cada execução na planilha e **roteia** entre escalação (urgência alta / confiança baixa) e resposta automática.

---

## 2. Comparação entre as três alternativas


| Critério                  | Solution A                       | Solution B                        | Solution C                  |
| ------------------------- | -------------------------------- | --------------------------------- | --------------------------- |
| **Abordagem**             | Prompt único + Switch            | FAQ Sheets + 2ª IA                | 2 chamadas IA sequenciais   |
| **Custo**                 | Baixo                            | Médio                             | Alto                        |
| **Complexidade**          | Baixa                            | Média                             | Alta                        |
| **Qualidade da resposta** | Roteamento forte; texto genérico | Roteamento + texto alinhado a FAQ | Bom texto; sem FAQ nativo   |
| **Riscos**                | Baixo                            | Médio (planilha)                  | Médio (2 LLMs)              |
| **Manutenibilidade**      | Alta                             | Média                             | Média                       |
| **Adequação ao problema** | MVP                              | **Adotada**                       | Pesquisa / demo alternativa |


**Solução escolhida:** **B**

**Justificativa:** integra **base de conhecimento** real (Sheets), atende melhor o README de extensões e mantém decisão da IA **no centro do grafo**.

---

## 3. Testes executados


| Teste | Descrição                            | Resultado    | Evidências                                                                                                                                                                                       |
| ----- | ------------------------------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| T1    | Mensagem com indisponibilidade geral | Passou | [B-T1-powershell-resposta.png](evidence/B-T1-powershell-resposta.png), [B-T1-sheets-linha-gerada.png](evidence/B-T1-sheets-linha-gerada.png)                                           |
| T2    | Mensagem trivial "esqueci a senha"   | Passou | [B-T2-powershell-resposta.png](evidence/B-T2-powershell-resposta.png), [B-T2-sheets-linha-gerada.png](evidence/B-T2-sheets-linha-gerada.png)                                           |
| T3    | Texto vazio ou muito curto           | Falhou | [B-T3-n8n-respond-erro-validacao.png](evidence/B-T3-n8n-respond-erro-validacao.png), [B-T3-powershell-resposta-invalida.png](evidence/B-T3-powershell-resposta-invalida.png)           |
| T4    | Corpo JSON inválido                  | Falhou | [B-T4-n8n-respond-erro-validacao.png](evidence/B-T4-n8n-respond-erro-validacao.png), [B-T4-powershell-resposta-json-invalido.png](evidence/B-T4-powershell-resposta-json-invalido.png) |

---

## 4. Evidências de funcionamento

Evidências registradas em `evidence/`:

### Configuração e Setup

- [B-01-webhook-configuracao.png](evidence/B-01-webhook-configuracao.png) - Configuração do webhook
- [B-02-normalize-input-output.png](evidence/B-02-normalize-input-output.png) - Normalização de entrada
- [B-03-input-valido-if-branch-true.png](evidence/B-03-input-valido-if-branch-true.png) - Validação de entrada válida

### Triagem com IA (Primeira Chamada)

- [B-04-gemini-triagem-request-response.png](evidence/B-04-gemini-triagem-request-response.png) - Request/Response da triagem
- [B-05-parse-triagem-json-estruturado.png](evidence/B-05-parse-triagem-json-estruturado.png) - Parse do JSON estruturado

### Integração com FAQ

- [B-06-ler-faq-sheet-output.png](evidence/B-06-ler-faq-sheet-output.png) - Leitura da planilha FAQ
- [B-07-faq-para-texto-output.png](evidence/B-07-faq-para-texto-output.png) - Conversão FAQ para texto
- [B-08-merge-triagem-faq-output.png](evidence/B-08-merge-triagem-faq-output.png) - Merge dos ramos
- [B-09-juntar-campos-output.png](evidence/B-09-juntar-campos-output.png) - Junção de campos

### Orientação Contextual (Segunda Chamada IA)

- [B-10-gemini-com-faq-request-response.png](evidence/B-10-gemini-com-faq-request-response.png) - Request/Response com FAQ
- [B-11-parse-resposta-final-rota.png](evidence/B-11-parse-resposta-final-rota.png) - Parse da resposta final

### Roteamento e Execução

- [B-12-switch-rota-branch.png](evidence/B-12-switch-rota-branch.png) - Switch de rota
- [B-13-sheets-log-tickets-append-ok.png](evidence/B-13-sheets-log-tickets-append-ok.png) - Append na planilha
- [B-14-respond-ok-output.png](evidence/B-14-respond-ok-output.png) - Resposta OK
- [B-15-execution-completa-sucesso.png](evidence/B-15-execution-completa-sucesso.png) - Execução completa
- [B-16-powershell-resposta-webhook.png](evidence/B-16-powershell-resposta-webhook.png) - Resposta via PowerShell

### Persistência e Auditoria

- [B-17-google-sheets-linha-gerada.png](evidence/B-17-google-sheets-linha-gerada.png) - Linha gerada no Sheets

### Tratamento de Erros

- [B-18-caso-invalido-execution-completa-invalida.png](evidence/B-18-caso-invalido-execution-completa-invalida.png) - Execução inválida
- [B-19-caso-invalido-respond-erro-validacao.png](evidence/B-19-caso-invalido-respond-erro-validacao.png) - Resposta erro validação
- [B-20-powershell-caso-invalido-respond-erro-validacao.png](evidence/B-20-powershell-caso-invalido-respond-erro-validacao.png) - PowerShell erro validação

### Evidências dos Testes

As evidências específicas dos testes executados estão discriminadas na **Seção 3** acima, incluindo os prints:

- [B-T1-powershell-resposta.png](evidence/B-T1-powershell-resposta.png) - Teste T1: Resposta PowerShell
- [B-T1-sheets-linha-gerada.png](evidence/B-T1-sheets-linha-gerada.png) - Teste T1: Linha gerada no Sheets
- [B-T2-powershell-resposta.png](evidence/B-T2-powershell-resposta.png) - Teste T2: Resposta PowerShell
- [B-T2-sheets-linha-gerada.png](evidence/B-T2-sheets-linha-gerada.png) - Teste T2: Linha gerada no Sheets
- [B-T3-n8n-respond-erro-validacao.png](evidence/B-T3-n8n-respond-erro-validacao.png) - Teste T3: Erro validação n8n
- [B-T3-powershell-resposta-invalida.png](evidence/B-T3-powershell-resposta-invalida.png) - Teste T3: Resposta inválida PowerShell
- [B-T4-n8n-respond-erro-validacao.png](evidence/B-T4-n8n-respond-erro-validacao.png) - Teste T4: Erro validação n8n
- [B-T4-powershell-resposta-json-invalido.png](evidence/B-T4-powershell-resposta-json-invalido.png) - Teste T4: Resposta JSON inválido PowerShell

---

## 5. Limitações conhecidas

- A qualidade depende do **modelo** e do **conteúdo da FAQ**.
- Classificação pode errar; mitigamos com `confianca` e revisão.
- Rate limits da API Gemini em dias de pico.

---

## 6. Riscos


| Risco                    | Probabilidade | Impacto | Mitigação                             |
| ------------------------ | ------------- | ------- | ------------------------------------- |
| Erro de urgência         | Média         | Alto    | Revisão humana quando confiança baixa |
| Indisponibilidade Gemini | Baixa         | Médio   | Mensagem amigável + log de erro       |


---

## 7. Decisões arquiteturais

- ADR-001: Escolha da solução B (FAQ + Sheets)

---

## 8. Instruções de execução


1. Importar no n8n o workflow `src/workflows/solution-b-faq-sheets.json`.
2. Configurar a chave da API Gemini nos nós HTTP (`x-goog-api-key`) e manter o modelo `gemini-2.5-flash`.
3. Configurar credencial Google Sheets e apontar o mesmo `Document ID` para:
  - leitura da aba `FAQ`;
  - escrita da aba `Tickets`.
4. Garantir que a planilha tenha:
  - aba `FAQ` com colunas `titulo` e `resposta`;
  - aba `Tickets` com colunas de auditoria (`timestamp`, `email`, `mensagem`, `categoria`, `urgencia`, `confianca`, `rota`, `resumo`, `orientacao`).
5. Executar o webhook com método `POST` e corpo JSON contendo ao menos:
  - `message` (obrigatório);
  - `email` (opcional, recomendado para rastreabilidade).
6. Verificar resultado:
  - resposta HTTP retornada pelo webhook;
  - execução concluída no n8n;
  - nova linha registrada em `Tickets`.
7. Repetir com um caso inválido (mensagem curta) para validar o tratamento de erro.

---

## 9. Checklist de revisão

- [x] Mission brief atendido
- [x] Três soluções implementadas/prototipadas
- [x] Testes executados e documentados
- [x] Evidências registradas em `evidence/`
- [x] ADR(s) registrado(s) em `docs/adr/`
- [x] Commits com mensagens claras e racionalidade
- [x] Código funcional em `src/`
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido

---

## 10. Justificativa para merge

A entrega cobre o cenário de **suporte técnico** com **IA decidindo rotas**, **integrações reais**, **auditoria em Sheets**, **tratamento de erro** e **três variantes** arquiteturais comparadas. A base técnica e documental está pronta para revisão; resta concluir somente a etapa de commits/PR conforme fluxo da disciplina.