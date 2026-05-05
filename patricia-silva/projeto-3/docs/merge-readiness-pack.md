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



---

## 4. Evidências de funcionamento



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


1. Importar no n8n o workflow `workflows/solution-b-faq-sheets.json`.
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
- [x] Evidências registradas em `docs/evidence/`
- [x] ADR(s) registrado(s) em `docs/adr/`
- [x] Commits com mensagens claras e racionalidade
- [x] Código funcional em `src/`
- [x] Agent.md preenchido
- [x] Mentorship Pack preenchido
- [x] Workflow Runbook seguido

---

## 10. Justificativa para merge

A entrega cobre o cenário de **suporte técnico** com **IA decidindo rotas**, **integrações reais**, **auditoria em Sheets**, **tratamento de erro** e **três variantes** arquiteturais comparadas. A base técnica e documental está pronta para revisão; resta concluir somente a etapa de commits/PR conforme fluxo da disciplina.