# ADR-001: Escolha da solução final (suporte técnico)

> **Data:** 05/05/2026
> **Status:** aceita

---

## Contexto

O projeto exige que a automação em n8n demonstre, de forma auditável, os seguintes pontos centrais:

- IA usada como mecanismo de **decisão**, não apenas geração de texto;
- lógica condicional com caminhos distintos;
- integração real com serviço externo;
- persistência para auditoria;
- comparação entre três abordagens.

No domínio escolhido (triagem de suporte técnico), a decisão arquitetural precisava equilibrar três objetivos que competem entre si:

1. **Confiabilidade operacional** (responder com consistência e cair em fallback seguro em caso de falha),
2. **Qualidade de orientação ao usuário** (não só classificar; orientar com conteúdo útil),
3. **Viabilidade de implementação no prazo** (complexidade e custo de execução).

---

## Alternativas consideradas

### Alternativa A: Prompt simples + classificação JSON

- **Descrição:** uma única chamada de IA para classificação (`categoria`, `urgencia`, `confianca`, `resumo_curto`) e roteamento via Switch.
- **Prós:**
  - menor custo e menor latência;
  - menor superfície de falha;
  - implementação e depuração mais simples.
- **Contras:**
  - resposta final ao usuário tende a ser genérica;
  - não explora base de conhecimento externa;
  - entrega menos evidência de “contextualização inteligente”.

### Alternativa B: FAQ no Google Sheets + segunda chamada contextual (RAG leve)

- **Descrição:** primeira IA classifica; o fluxo lê FAQ em Google Sheets; segunda IA gera orientação contextual baseada no FAQ; roteamento e auditoria permanecem no n8n.
- **Prós:**
  - atende diretamente ao requisito de integração com serviço real (Sheets leitura + escrita);
  - demonstra recuperação de contexto externo antes da geração (RAG leve);
  - melhora a utilidade da resposta sem abandonar controle por regras (`Switch`);
  - reforça rastreabilidade (o que entrou, como foi classificado e como foi respondido).
- **Contras:**
  - maior latência e consumo de tokens;
  - depende da qualidade e manutenção da planilha FAQ;
  - risco maior de rate limit por usar duas chamadas de IA por execução.

### Alternativa C: Pipeline multi-etapas (classificar -> redigir -> validar rota)

- **Descrição:** duas chamadas de IA com responsabilidades separadas (classificação e redação), seguidas de validação por regras no fluxo.
- **Prós:**
  - excelente separação de responsabilidades por etapa;
  - atende bem ao critério de multi-step reasoning;
  - facilita tuning de prompt por fase.
- **Contras:**
  - maior custo e maior tempo por execução;
  - duas etapas de IA aumentam pontos de falha;
  - sem base externa por padrão, entrega menos benefício de conhecimento institucional do que B.

---

## Decisão

A alternativa escolhida foi a **B** (`src/workflows/solution-b-faq-sheets.json`).

### Fundamentação detalhada

A escolha foi orientada por aderência à rubrica e valor prático para o cenário de suporte:

1. **Melhor cobertura dos critérios com maior peso**
  A Solução B mantém fluxo claro em n8n, usa decisão por IA com impacto real no roteamento e adiciona contextualização por base externa. Isso reforça simultaneamente os critérios de fluxo, uso de IA e lógica de decisão.
2. **Equilíbrio entre sofisticação e operabilidade**
  A solução A é robusta e barata, mas simplifica demais a orientação final. A C é tecnicamente forte em multi-etapas, porém mais custosa e sem o mesmo ganho de base de conhecimento. A B ficou no meio-termo com melhor relação valor/complexidade para entrega acadêmica.
3. **Maior aderência ao problema de suporte técnico**
  Em suporte, boa parte dos chamados recorrentes pode ser tratada com instruções padronizadas. A leitura da FAQ aproxima a automação da prática real de service desk, com respostas mais úteis e consistentes.
4. **Rastreabilidade e auditabilidade mais ricas**
  A arquitetura B facilita explicar, no relatório e na banca, de onde veio a resposta: entrada do usuário + classificação + contexto recuperado + rota aplicada + registro em planilha.
5. **Capacidade de fallback preservada**
  Mesmo com duas etapas de IA, o fluxo mantém comportamento conservador (`revisao`) em baixa confiança ou falha de API, reduzindo risco de automação incorreta.

Em resumo, a alternativa B foi escolhida por entregar o melhor compromisso entre qualidade da automação, evidência de uso inteligente de IA e viabilidade de implementação no prazo do projeto.

---

## Consequências

### Positivas

- Respostas mais contextualizadas para chamados comuns;
- maior qualidade de demonstração em vídeo/prints;
- narrativa técnica forte no relatório (RAG leve + regras de negócio + auditoria).

### Custos e riscos assumidos

- Maior dependência da estabilidade da API de IA e de limites de uso;
- necessidade de manutenção contínua da FAQ;
- maior atenção à configuração do nó Merge e ao mapeamento de colunas no Sheets.

### Mitigações adotadas

- Rota de fallback para revisão humana em baixa confiança/falha;
- documentação operacional detalhada em `docs/N8N_INSTRUCOES.md` e `docs/PASSO-A-PASSO-SOLUCAO-B.md`;
- manutenção das soluções A e C como referência comparativa e plano alternativo.

---

## Referências

- `src/workflows/solution-a-prompt-simples.json`
- `src/workflows/solution-b-faq-sheets.json`
- `src/workflows/solution-c-multietapas.json`
- `docs/workflow-runbook.md`
- `docs/merge-readiness-pack.md`