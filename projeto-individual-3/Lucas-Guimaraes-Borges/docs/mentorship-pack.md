# Mentorship Pack

> **Projeto:** Triagem Inteligente de Emails da Codzz

## 1. Orientações de julgamento

- Priorizar segurança operacional antes de automação total.
- Escolher a categoria pelo intento principal do cliente.
- Em caso de empate ou ambiguidade, escalar para revisão humana.

## 2. Padrões de arquitetura

- Orquestração no n8n com nós pequenos e observáveis.
- Decisão por IA deve passar por validação de esquema.
- Registrar entradas e decisões para auditoria.

## 3. Padrões de código

- Linguagem: Python 3.11+
- Estilo: funções pequenas, sem dependências externas obrigatórias
- Testes: `unittest` cobrindo classificação e fallback

## 4. Estilo de documentação

- Markdown objetivo
- Sempre explicitar trade-offs
- Referenciar evidências em `docs/evidence/`

## 5. Qualidade esperada

- JSON de saída sempre válido
- Cobertura de casos comuns (técnico, financeiro, cancelamento)
- Estratégia clara para baixa confiança

## 6. Exemplos de boas respostas

```text
Entrada: "Não consigo integrar o webhook, retorna erro 500"
Saída: categoria "suporte técnico", urgência 8, resumo curto e preciso
```

## 7. Exemplos de más respostas

```text
Responder com texto longo sem JSON ou inventar categoria não prevista.
```

## 8. Princípios-guia

```text
Explicar decisão técnica antes de automatizar ação crítica.
Preferir soluções simples, testáveis e observáveis.
Não esconder incertezas do modelo.
Registrar alternativas descartadas no ADR.
```

