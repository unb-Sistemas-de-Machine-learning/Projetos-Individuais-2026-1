# Mission Brief

> **Aluno(a):** Marcos Antonio Teles de Castilhos
> **Matrícula:** 221008300
> **Domínio:** Finanças Pessoais (Automação de Triagem e Registro)

---

## 1. Objetivo do agente

_Descreva de forma clara e concisa o que o agente deve fazer._
Processar inputs financeiros naturais (áudio e texto), extrair metadados e validar o formato para registrar despesas em uma base estruturada automaticamente.

---

## 2. Problema que ele resolve

_Qual problema real o agente pretende resolver? Por que esse problema é relevante?_
A fricção no lançamento manual de despesas financeiras prejudica o acompanhamento do orçamento. O agente centraliza e automatiza a coleta de dados de forma nativa e rápida.

---

## 3. Usuários-alvo

_Quem vai usar o agente? Qual o perfil desses usuários?_
Uso estritamente pessoal. Perfil técnico que valoriza arquiteturas determinísticas.

---

## 4. Contexto de uso

_Em que situação o agente será utilizado? Descreva o ambiente, o momento e as condições de uso._
Lançamento on-the-go via aplicativo mobile do Telegram no exato momento da transação, operando como um terminal ubíquo.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| Entrada | Mensagem do Telegram (Texto ou Voice). |
| Formato da entrada | String ou binário OGA/Opus. |
| Saída | Inserção de linha via API / Mensagem de notificação. |
| Formato da saída | Nova linha no Google Sheets e payload de texto no Telegram. |

---

## 6. Limites do agente

_O que o agente consegue fazer e o que está fora do seu escopo?_

### O que o agente faz:
- Recebe inputs via Telegram

- Transcreve áudio. 

- Realiza inferência sobre a categoria e data da transação.

- Extrai e formata o JSON.

### O que o agente NÃO deve fazer:
- Modificar lançamentos anteriores (sem operação de Update).  

- Responder casualmente a perguntas não financeiras.

- Adicionar à planilha entradas que contém campos faltantes.
---

## 7. Critérios de aceitação

_Quando a missão pode ser considerada concluída com sucesso?_

[x] O fluxo processa mensagens de texto e insere no Sheets.  

[x] O fluxo processa áudios e insere no Sheets.  

[x] O fluxo rejeita ativamente mensagens com ausência de valor monetário e notifica o erro.

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Latência da transcrição | Média | Baixo | Uso da infraestrutura LPU do Groq para transcrição quase instantânea. |  

---

## 9. Evidências necessárias

_Quais evidências são necessárias para considerar a missão concluída?_

- [x] Exportação do workflow.json final.  

- [x] Capturas de tela (prints) de sucessos e falhas controladas no Telegram.  

- [x] Log de execuções do n8n validando a separação de rotas pelo nó Switch.
