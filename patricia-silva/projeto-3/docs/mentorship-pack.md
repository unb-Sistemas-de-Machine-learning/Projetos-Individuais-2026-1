# Mentorship Pack

> **Projeto:** Triagem de suporte técnico (n8n + IA)
> **Aluno(a):** Patricia Helena Macedo da Silva
> **Matrícula:** 221037993

---

## 1. Orientações de julgamento

*Como o agente deve tomar decisões? Quais valores priorizar?*

- Priorizar segurança operacional: em cenário ambíguo, preferir revisão humana a uma resposta confiante porém incorreta.
- Priorizar rastreabilidade: toda decisão importante deve aparecer nos campos estruturados e no registro em planilha.
- Priorizar clareza de impacto: a saída da IA deve alterar o caminho do fluxo (IF/Switch), não apenas gerar texto adicional.
- Priorizar robustez: manter fallback explícito para falhas de API, baixa confiança e entrada inválida.

---

## 2. Padrões de arquitetura

*Qual estilo de arquitetura o agente deve seguir?*

- n8n como orquestrador principal, com separação clara por etapa (entrada, decisão, validação, persistência e resposta).
- IA (Gemini) usada como componente de decisão estruturada e geração contextual.
- Solução final B com padrão RAG leve: recuperar contexto no FAQ (Sheets), combinar com classificação e então gerar orientação.
- Fluxo sempre auditável: entrada, decisão de rota e saída final registradas em `Tickets`.

---

## 3. Padrões de código

*Convenções de código que o agente deve respeitar.*

- Linguagem: JavaScript nos nós Code do n8n.
- Estilo: parse defensivo (`try/catch`), defaults explícitos (`categoria=outro`, `confianca=baixa`), sem assumir JSON perfeito da IA.
- Testes: executar casos válidos e inválidos para A/B/C, registrar saída HTTP, execução no n8n e linha em planilha.

---

## 4. Estilo de documentação

*Como o agente deve documentar seu trabalho?*

- Manter alinhamento entre workflow real e documentação (`docs/`, `solutions/`, `tests/`).
- Registrar decisão arquitetural no ADR com comparação de alternativas e trade-offs.
- Referenciar evidências por solução em `docs/evidence/` com nomenclatura padronizada (`A-`*, `B-`*, `C-*`).
- Atualizar documentação sempre que mudar modelo da IA, mapeamento do Sheets, webhook path ou regras de roteamento.

---

## 5. Qualidade esperada

*Qual o nível de qualidade mínimo para considerar uma entrega aceitável?*

- Três soluções demonstráveis (A/B/C), com comparação objetiva no runbook/ADR.
- Solução final operando ponta a ponta com decisão por IA, persistência e tratamento de erro.
- Evidências visuais suficientes para reproduzir a avaliação (execução, resposta, planilha, caso inválido).
- Workflows exportados e documentação coerente com o comportamento observado nos testes.

---

## 6. Exemplos de boas respostas

```
Exemplo 1:
Entrada: "O sistema caiu para todo mundo do setor."
Boa decisão: classificar com urgência alta, encaminhar para rota de escalação e registrar execução no Sheets.
Motivo: reduz risco operacional e atende prioridade do incidente.
```

---

## 7. Exemplos de más respostas

```
Exemplo 1:
Entrada: "ajuda"
Má decisão: assumir categoria específica e confiança alta sem contexto.
Correto: marcar confiança baixa e encaminhar para revisão humana (ou solicitar mais detalhes).
```

---

## 8. Princípios-guia

```
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas.
O agente deve registrar alternativas descartadas.
O agente deve tratar erro como parte do design, não como exceção rara.
```

