# Mission Brief

> **Aluno(a):** Guilherme Westphall
> **Matrícula:** 211061805
> **Domínio:** Automação inteligente de emissão de notas fiscais com aprovação humana

---

## 1. Objetivo do agente

Projetar um agente de apoio à emissão de notas fiscais que valide dados extraídos do Productive.io, identifique possíveis inconsistências, gere uma mensagem interna de aprovação para o Telegram e prepare um e-mail profissional simples para envio ao contratante.

O agente deve atuar como componente de decisão dentro de um fluxo orquestrado no n8n. Ele não deve substituir cálculos determinísticos nem tomar decisões financeiras finais. A emissão e o envio da fatura só devem ocorrer após aprovação explícita do prestador de serviço responsável.

---

## 2. Problema que ele resolve

Prestadores de serviço que trabalham por hora frequentemente precisam emitir notas fiscais recorrentes para seus contratantes. Em um cenário comum, esse processo ocorre duas vezes por mês, normalmente nos dias 1 e 16, e envolve consultar horas trabalhadas em uma ferramenta de controle de tempo, calcular o total do período, atualizar uma planilha de fatura, exportar um PDF, redigir um e-mail e enviar a mensagem ao contratante.

Esse processo é repetitivo, sujeito a esquecimentos e erros operacionais, especialmente na definição do período correto, soma de horas, preparação da comunicação e rastreamento da aprovação. O agente resolve parte desse problema ao revisar os dados preparados pelo fluxo, sinalizar riscos práticos e solicitar aprovação humana antes de qualquer envio ao contratante.

---

## 3. Usuários-alvo

O usuário principal é um prestador de serviço que registra horas trabalhadas e precisa emitir notas fiscais recorrentes para seus contratantes.

Usuários indiretos:

- Representantes do contratante, destinatários previstos do e-mail com a fatura.
- Avaliadores do projeto, que devem conseguir auditar a automação, as decisões tomadas e as evidências de funcionamento.

---

## 4. Contexto de uso

O agente será utilizado em um fluxo automatizado no n8n, executado de forma agendada ou por acionamento manual. O fluxo deve calcular o período de faturamento, buscar entradas de tempo no Productive.io, consolidar horas e valor de forma determinística, submeter o rascunho ao agente de IA para validação e solicitar aprovação via Telegram.

O uso esperado ocorre nos ciclos quinzenais de faturamento:

- No dia 1 ou nos dias seguintes antes do dia 16, o período considerado deve ser do dia 16 ao último dia do mês anterior.
- No dia 16 ou nos dias seguintes do mesmo mês, o período considerado deve ser do dia 1 ao dia 15 do mês atual.
- Caso `period_start` e `period_end` sejam informados explicitamente, esses valores devem prevalecer.

O envio do e-mail e da fatura só deve acontecer após aprovação explícita do usuário humano.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Dados consolidados de faturamento gerados pelo fluxo, incluindo período, quantidade de entradas, total de minutos, total de horas, valor por hora, moeda, valor total, avisos e lista resumida de entradas de tempo. |
| **Formato da entrada** | JSON produzido pelo n8n após consulta ao Productive.io e consolidação em nó de código. Campos esperados: `period_start`, `period_end`, `period_source`, `entry_count`, `total_minutes`, `total_hours`, `hourly_rate`, `currency`, `amount`, `warnings`, `entries`. |
| **Saída** | Validação do rascunho da fatura, ação recomendada, lista de problemas detectados, resumo interno, mensagem de aprovação para Telegram, assunto e corpo do e-mail ao contratante. |
| **Formato da saída** | JSON minificado com campos: `confidence`, `recommended_action`, `summary`, `detected_issues`, `work_summary`, `telegram_message`, `email_subject`, `email_body`. |

---

## 6. Limites do agente

O agente deve apoiar a validação e a comunicação, mas a autoridade sobre dados financeiros, aprovação e envio pertence ao fluxo determinístico e ao usuário humano.

### O que o agente faz:

- Verifica se o rascunho de fatura contém informações suficientes para revisão.
- Identifica anomalias práticas, como período ausente, ausência de entradas, zero horas, valor ausente, avisos prévios ou volumes de horas incomuns.
- Recomenda uma das ações: solicitar aprovação, pedir revisão manual ou interromper o fluxo.
- Gera uma mensagem interna para o prestador de serviço revisar e aprovar pelo Telegram.
- Gera um e-mail profissional, breve e simples, do prestador de serviço para os representantes do contratante.
- Expõe incertezas por meio dos campos `confidence`, `recommended_action` e `detected_issues`.

### O que o agente NÃO deve fazer:

- Recalcular horas, valor por hora ou valor total da fatura.
- Alterar dados financeiros calculados pelo fluxo.
- Aprovar notas fiscais em nome do prestador de serviço.
- Enviar e-mails ou acionar serviços externos diretamente.
- Inventar links, nomes de arquivos, números de fatura ou anexos inexistentes.
- Incluir no e-mail ao contratante detalhes internos como horas trabalhadas, valor total, período, validação, aprovação, automação ou uso de IA.
- Usar campos internos do Productive.io, como `approved`, `invoiced` ou `rejected`, como critério de confiança ou decisão para este processo.

---

## 7. Critérios de aceitação

- [ ] O fluxo no n8n calcula o período de faturamento correto para execuções agendadas e manuais.
- [ ] O fluxo busca entradas de tempo no Productive.io usando `person_id` e filtros de data.
- [ ] As horas, o valor por hora e o valor total são calculados de forma determinística fora do agente de IA.
- [ ] O agente recebe os dados consolidados e retorna JSON válido no formato especificado.
- [ ] A decisão do agente influencia o fluxo por meio de caminhos condicionais, como aprovação, revisão manual ou interrupção.
- [ ] O envio da fatura depende de aprovação explícita via Telegram.
- [ ] Entradas inválidas, baixa confiança ou resposta malformada da IA acionam fallback para revisão manual.
- [ ] As decisões relevantes e resultados de execução são registrados para auditoria.
- [ ] O workflow exportado do n8n, evidências, relatório técnico e demais artefatos obrigatórios são incluídos no repositório.

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| O agente retornar JSON inválido ou texto fora do formato esperado. | Média | Médio | Adicionar nó de normalização/parsing após a IA e encaminhar falhas para revisão manual. |
| A IA sugerir uma ação inadequada por interpretar mal os dados. | Média | Alto | Manter cálculos financeiros fora da IA e exigir aprovação humana antes do envio. |
| Período de faturamento calculado incorretamente. | Baixa | Alto | Testar os cenários dos dias 1, 16 e execuções manuais com `period_start` e `period_end`. |
| Falha na API do Productive.io ou ausência de dados. | Média | Médio | Detectar resposta vazia ou erro HTTP, registrar o problema e solicitar revisão manual. |
| Token ou credencial exposta no workflow exportado. | Média | Alto | Usar credenciais do n8n ou variáveis de ambiente e substituir segredos por placeholders antes da entrega. |
| Envio de e-mail sem aprovação humana. | Baixa | Alto | Implementar bloqueio condicional obrigatório baseado em confirmação explícita via Telegram. |
| E-mail ao contratante conter detalhes internos ou financeiros indesejados. | Média | Médio | Definir regras rígidas no `agent.md` e validar o corpo do e-mail antes do envio. |
| Falta de evidências suficientes para auditoria do projeto. | Média | Médio | Registrar prints, logs e outputs em `docs/evidence/` durante cada etapa relevante. |

---

## 9. Evidências necessárias

- [ ] Exportação do workflow n8n em JSON.
- [ ] Print ou log do cálculo do período de faturamento.
- [ ] Print ou log da consulta ao Productive.io com entradas retornadas.
- [ ] Evidência da consolidação determinística de horas e valor total.
- [ ] Exemplo de resposta válida do agente de IA em JSON.
- [ ] Evidência de tratamento de resposta inválida ou baixa confiança da IA.
- [ ] Print ou log da mensagem de aprovação enviada via Telegram.
- [ ] Evidência de que o envio de e-mail só ocorre após aprovação explícita.
- [ ] Registro de execução, decisão e resultado para rastreabilidade.
- [ ] Relatório técnico final preenchido.
