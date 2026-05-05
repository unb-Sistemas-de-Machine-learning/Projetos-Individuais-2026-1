# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Patricia Helena Macedo da Silva
> **Matrícula:** 221037993
> **Data de entrega:** 05/05/2026

---

## 1. Resumo do Projeto

Foi implementada uma automação de **triagem de suporte técnico** no **n8n**, com **dois** usos de IA na solução principal (B): o primeiro classifica e extrai um JSON operacional (`categoria`, `urgencia`, `confianca`, `resumo_curto`); o segundo gera uma **orientação** ao usuário fundamentada em um **FAQ** armazenado em **Google Sheets**. O orquestrador aplica **Switch** conforme urgência e confiança, grava auditoria na aba `Tickets` e expõe um **Webhook** para entrada de chamados. Soluções alternativas (A: prompt único; C: pipeline em duas IAs sem FAQ) foram prototipadas para comparação.

---

## 2. Problema Escolhido

Triagem automática de demandas de **suporte técnico** (acesso, performance, erros, dúvidas de uso), reduzindo tempo de resposta e priorizando incidentes críticos, mantendo rastreabilidade das decisões.

---

## 3. Desenho do Fluxo

```
Webhook → Validar entrada → (Paralelo) Gemini triagem | Ler FAQ Sheets
           → Merge → Segunda Gemini com contexto FAQ → Rotear → Sheets Tickets → Respond
```

### 3.1 Nós utilizados (Solução B)


| Nó                   | Tipo               | Função no fluxo                           |
| -------------------- | ------------------ | ----------------------------------------- |
| Webhook              | Webhook            | Entrada HTTP POST                         |
| Normalize Input      | Set                | Extrai `message` e `email`                |
| Input válido?        | If                 | Bloqueia texto vazio ou muito curto       |
| Gemini Triagem       | HTTP Request       | Classificação JSON                        |
| Parse Triagem        | Code               | Interpreta JSON + anexa mensagem original |
| Ler FAQ Sheet        | Google Sheets      | Lê base de conhecimento                   |
| FAQ para Texto       | Code               | Serializa FAQ em texto                    |
| Merge Triagem e FAQ  | Merge              | Junta os dois ramos                       |
| Juntar Campos        | Code               | Objeto único para etapa 2                 |
| Gemini Com FAQ       | HTTP Request       | Gera orientação ao usuário                |
| Parse Resposta Final | Code               | Define `rota` e texto final               |
| Switch Rota          | Switch             | escala / revisão / auto                   |
| Sheets Log Tickets   | Google Sheets      | Auditoria                                 |
| Respond              | Respond to Webhook | Resposta ao cliente                       |


---

### 3.2 Evidências visuais do fluxo

As evidências visuais do fluxo completo estão documentadas em [evidence/](evidence/):

1. [Webhook — Configuração](evidence/B-01-webhook-configuracao.png)
2. [Normalize Input — Output](evidence/B-02-normalize-input-output.png)
3. [Input válido? — If Branch (True)](evidence/B-03-input-valido-if-branch-true.png)
4. [Gemini Triagem — Request/Response](evidence/B-04-gemini-triagem-request-response.png)
5. [Parse Triagem — JSON estruturado](evidence/B-05-parse-triagem-json-estruturado.png)
6. [Ler FAQ Sheet — Output](evidence/B-06-ler-faq-sheet-output.png)
7. [FAQ para Texto — Output](evidence/B-07-faq-para-texto-output.png)
8. [Merge Triagem e FAQ — Output](evidence/B-08-merge-triagem-faq-output.png)
9. [Juntar Campos — Output](evidence/B-09-juntar-campos-output.png)
10. [Gemini Com FAQ — Request/Response](evidence/B-10-gemini-com-faq-request-response.png)
11. [Parse Resposta Final — Rota](evidence/B-11-parse-resposta-final-rota.png)
12. [Switch Rota — Branch](evidence/B-12-switch-rota-branch.png)
13. [Sheets Log Tickets — Append OK](evidence/B-13-sheets-log-tickets-append-ok.png)
14. [Respond OK — Output](evidence/B-14-respond-ok-output.png)
15. [Execution Completa — Sucesso](evidence/B-15-execution-completa-sucesso.png)
16. [PowerShell — Resposta Webhook](evidence/B-16-powershell-resposta-webhook.png)
17. [Google Sheets — Linha gerada](evidence/B-17-google-sheets-linha-gerada.png)
18. [Caso Inválido — Execution Completa](evidence/B-18-caso-invalido-execution-completa-invalida.png)
19. [Caso Inválido — Respond Erro Validação](evidence/B-19-caso-invalido-respond-erro-validacao.png)
20. [PowerShell — Caso Inválido Resposta](evidence/B-20-powershell-caso-invalido-respond-erro-validacao.png)

## 4. Papel do Agente de IA

- **Modelo/serviço:** Google Gemini API (`gemini-2.5-flash` no workflow), via nó HTTP Request e cabeçalho `x-goog-api-key`.
- **Decisões:** (1) classificação estruturada que determina **rota**; (2) conteúdo da mensagem ao usuário condicionado ao FAQ.
- **Efeito no fluxo:** campos `urgencia`, `confianca` e `rota` alteram qual ramo do **Switch** será seguido; não é apenas “texto ornamental”.

---

## 5. Lógica de Decisão

- **Condição:** `urgencia == alta` -> rota `escala` (priorização / notificação, conforme configurado).
- **Condição:** `confianca` baixa na triagem **ou** `confianca_resposta` baixa na segunda etapa -> `revisao`.
- **Caso contrário:** `auto` (resposta automática orientada pelo FAQ).

---

## 6. Integrações


| Serviço           | Finalidade                        |
| ----------------- | --------------------------------- |
| Google Gemini API | Duas etapas de LLM na solução B   |
| Google Sheets     | FAQ (leitura) + Tickets (escrita) |
| Webhook n8n       | Entrada do “formulário” / sistema |


---

## 7. Persistência e Rastreabilidade

Cada execução bem-sucedida deve adicionar linha em `Tickets` com timestamp, mensagem, campos de classificação, rota e orientação final, permitindo auditoria posterior.

Evidências associadas:

- `evidence/B-13-sheets-log-tickets-append-ok.png`
- `evidence/B-17-google-sheets-linha-gerada.png`

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** `continueOnFail` nos HTTP + campos de erro nos nós Code; rota conservadora para revisão.
- **Entradas inválidas:** ramo dedicado sem chamada à API.
- **Fallback (baixa confiança):** rota `revisao` e linguagem prudente na orientação.

Evidências associadas:

- [Caso inválido — Respond Erro Validação](evidence/B-19-caso-invalido-respond-erro-validacao.png)
- [PowerShell — Caso Inválido Resposta](evidence/B-20-powershell-caso-invalido-respond-erro-validacao.png)

---

## 9. Diferenciais implementados

- Memória de contexto
- Multi-step reasoning (solução C; solução B aplica duas etapas de IA com papéis distintos)
- Integração com base de conhecimento (FAQ no Google Sheets)
- Uso de embeddings / busca semântica

Observação: os diferenciais marcados foram implementados e demonstrados nas evidências da solução B (RAG leve) e da solução C (pipeline multi-etapas).

---

## 10. Limitações e Riscos

- Classificação pode errar; mitigação com confiança e revisão.
- Dependência de disponibilidade da API e de conteúdo atualizado do FAQ.

---

## 11. Como executar

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

## 12. Referências

1. Documentação n8n — Webhook e Google Sheets.
2. Google Gemini API — `generateContent`, `responseMimeType: application/json`.

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (`src/workflows/*.json`)
- [x] Scripts auxiliares / testes manuais (`tests/`)
- [x] Demonstração do fluxo — evidências em [evidence/](evidence/)
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto (conforme repositório da disciplina)

