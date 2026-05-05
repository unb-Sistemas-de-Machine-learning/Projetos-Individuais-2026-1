# ADR-001: Escolha da solução de triagem de chamados

> **Data:** 05/05/2025
> **Status:** aceita

---

## Contexto

Foram propostas e prototipadas três abordagens para o problema de triagem automática de chamados de suporte. A escolha da solução final precisava equilibrar qualidade da classificação, complexidade de implementação, custo de tokens e adequação ao escopo do projeto.

---

## Alternativas consideradas

### Alternativa A: Prompt simples (solution-a)

- **Descrição:** Uma única chamada à API da OpenAI por chamado. A mensagem é enviada com um prompt de sistema que instrui o modelo a retornar JSON estruturado com categoria, urgência, resumo e confiança. O n8n roteia com base nos campos retornados.
- **Prós:** Simples de implementar e manter; custo baixo (uma chamada por request); fluxo linear e fácil de depurar; já atende todos os requisitos obrigatórios.
- **Contras:** Sem enriquecimento das respostas automáticas; depende 100% da qualidade do prompt.

### Alternativa B: Com base de conhecimento / FAQ (solution-b)

- **Descrição:** Igual à solution-a, mas chamados de baixa urgência consultam uma planilha de FAQ no Google Sheets antes de enviar resposta automática ao usuário.
- **Prós:** Respostas automáticas mais úteis para o usuário final; reduz necessidade de intervenção humana em casos simples.
- **Contras:** Depende de manutenção contínua da base de FAQ; maior complexidade no fluxo; FAQ desatualizado gera respostas incorretas.

### Alternativa C: Fluxo multi-etapas com validação e retry (solution-c)

- **Descrição:** Igual à solution-b, mas com validação explícita do JSON retornado pela IA e retry automático (até 2x) quando `confianca` for `"baixa"` ou o JSON vier malformado.
- **Prós:** Mais robusto; menor taxa de falsos fallbacks; melhor rastreabilidade por etapa.
- **Contras:** Mais nós no fluxo, mais difícil de manter; maior custo de tokens (retry = chamadas extras); complexidade desnecessária para o volume do projeto.

---

## Decisão

**Alternativa escolhida: Solution-A**, com incorporação do tratamento de erro explícito da solution-c (nó `onError` no HTTP Request e caminho de fallback no Switch).

A solution-a atende todos os requisitos obrigatórios com a menor complexidade possível. A incorporação do tratamento de erro não aumenta significativamente a complexidade, mas elimina o principal risco da abordagem simples. A solution-b foi descartada por exigir manutenção externa ao escopo. A solution-c foi descartada por adicionar complexidade e custo desproporcional ao benefício.

---

## Consequências

- O fluxo final é composto por: Webhook → IF (validação) → HTTP Request (OpenAI) → Code (parse JSON) → Switch (urgência + confiança) → Gmail / Google Sheets / Fallback
- A solução é auditável via Google Sheets, onde todos os chamados são registrados com timestamp e caminho executado
- Manutenção futura requer apenas atualização do prompt e reautenticação das credenciais OAuth

---

## Referências

- Documentação do n8n — Switch node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.switch/
- OpenAI API Reference: https://platform.openai.com/docs/api-reference/chat
