# ADR-001: Escolha da abordagem de automação da nota fiscal

> **Data:** 05/05/2026
> **Status:** Aceita

---

## Contexto

O projeto exige a escolha de uma abordagem para automatizar a emissão recorrente de notas fiscais com apoio de agente de IA. O fluxo deve calcular horas e valor de forma determinística, usar a IA para validar e redigir mensagens influenciando o caminho do workflow e exigir aprovação humana explícita antes de qualquer envio externo.

Três abordagens foram comparadas. O critério central é a combinação entre segurança do processo financeiro, qualidade do conteúdo gerado e demonstração clara do uso de IA como componente de decisão.

---

## Alternativas consideradas

### Alternativa A: Agente único baseado em prompt

- **Descrição:** Um único agente de IA recebe o JSON consolidado com dados da nota fiscal e retorna em uma única chamada a validação, a ação recomendada (`recommended_action`), a mensagem de aprovação para o Telegram e o rascunho do e-mail ao contratante. O fluxo n8n aplica um Switch baseado no valor retornado para decidir o próximo passo.
- **Prós:** Simples de implementar; menor número de chamadas ao modelo; fácil de depurar; já implementada e testada com dados reais.
- **Contras:** Sem camada de revisão do conteúdo gerado; o e-mail pode conter problemas de tom ou dados internos sem que o fluxo perceba antes da aprovação humana.

### Alternativa B: Agente com base de conhecimento histórica

- **Descrição:** Antes de acionar o agente, o fluxo consulta uma base de conhecimento com registros de notas fiscais e e-mails anteriores. O agente recebe o contexto histórico para comparar padrões e detectar anomalias, como desvios de horas ou variações de estilo em relação a ciclos anteriores.
- **Prós:** Detecção de anomalias históricas; estilo de e-mail mais consistente com aprovações anteriores; base para memória de longo prazo.
- **Contras:** Exige infraestrutura adicional (base de dados ou vector store); nos primeiros ciclos a base está vazia e o benefício é mínimo; maior complexidade de manutenção; não implementada neste ciclo.

### Alternativa C: Dois agentes — Rascunhador e Revisor

- **Descrição:** O Agente Rascunhador gera o rascunho inicial do e-mail e a mensagem de aprovação. O Agente Revisor recebe o rascunho e valida o conteúdo quanto a tom, profissionalismo e ausência de dados internos sigilosos ou conteúdo inadequado. O usuário pode solicitar revisão pelo Telegram com o comando `edit` antes de aprovar o envio.
- **Prós:** Separação de responsabilidades entre geração e revisão; camada de validação de conteúdo antes da aprovação humana; loop de edição via Telegram oferece controle sem intervenção técnica; implementada e testada de ponta a ponta.
- **Contras:** Maior número de chamadas ao modelo por execução; maior latência; complexidade adicional no workflow n8n.

---

## Decisão

**Alternativa C — dois agentes (Rascunhador e Revisor).**

A abordagem com dois agentes foi escolhida como solução final pelos seguintes motivos:

1. **Separação de responsabilidades**: gerar e revisar são tarefas com critérios distintos. Separá-las em agentes independentes reduz a chance de problemas no e-mail passarem para a aprovação humana sem detecção.

2. **Camada de segurança de conteúdo**: o Agente Revisor valida o e-mail antes da aprovação humana, detectando problemas de tom, conteúdo inadequado ou vazamento de dados internos — um risco real em sistemas com um único agente.

3. **Controle do usuário**: o comando `edit` no Telegram permite solicitar revisão sem intervir no fluxo técnico. Isso foi demonstrado na execução real, resultando em um e-mail com reformatação de tom e estrutura.

4. **Implementação demonstrável**: o workflow foi testado de ponta a ponta, incluindo o fluxo de edição, e as evidências estão documentadas em `docs/evidences/`.

A Solution A (agente único) permanece como baseline implementada e pode ser usada quando se prioriza simplicidade operacional. A Solution B não foi implementada por exigir infraestrutura adicional fora do escopo deste ciclo.

---

## Consequências

- O workflow final exportado é `automation-invoice-two-agent-review-ngrok.json`.
- O workflow `automation-invoice-complete-ngrok.json` permanece como referência da Solution A (baseline).
- O número de chamadas ao modelo por execução é maior (dois agentes), mas o custo é absorvido pelo uso do Ollama local.
- A manutenção do fluxo exige documentar as responsabilidades de cada agente separadamente para facilitar depuração.
- O comando `edit` deve ser tratado como caminho de revisão controlado. Em uso real, recomenda-se limitar o número de iterações para evitar loops indefinidos.

---

## Referências

- [Mission Brief](../mission-brief.md)
- [Agent.md](../../agent.md)
- [Solution A](../../solutions/solution-a/README.md)
- [Solution B](../../solutions/solution-b/README.md)
- [Solution C](../../solutions/solution-c/README.md)
- [Evidências](../evidences/)
