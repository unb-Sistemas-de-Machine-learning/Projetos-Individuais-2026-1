# Mentorship Pack

> **Projeto:** Assistente de Monitoria Universitária Autônomo
> **Aluno(a):** Diego Carlito Rodrigues de Souza

---

## 1. Orientações de julgamento

- Priorizar a confiabilidade determinística (n8n) sobre a flexibilidade do LLM em decisões críticas de roteamento.
- A segurança acadêmica é a prioridade máxima: o agente nunca deve conceder exceções (como prazos e notas) ou resolver trabalhos inteiros para o aluno.
- Priorizar a sustentabilidade financeira, garantindo que o fluxo opere dentro de limites de APIs gratuitas (ex: Groq/Llama-3).

---

## 2. Padrões de arquitetura

- **Arquitetura Híbrida:** A inteligência artificial (LLM) atua apenas na extração de intenção (NLU) e geração de respostas educacionais. O controle de fluxo, roteamento e integrações externas (ex: banco de dados, Slack) devem ser obrigatoriamente feitos por nós nativos do n8n.
- **Fail-Fast:** Requisições inválidas, mensagens vazias ou spam devem ser descartadas nos primeiros nós lógicos, sem acionar as APIs de LLM.

---

## 3. Padrões de código

- **Linguagem:** Fluxos visuais em n8n (exportados via JSON) e formatação estrita em JSON para respostas do LLM ao orquestrador.
- **Estilo:** `snake_case` obrigatório para todas as chaves JSON (ex: `route_to`, `tipo_duvida`).
- **Testes:** Toda alteração no fluxo de trabalho deve ser validada testando manualmente os três caminhos lógicos do roteamento: Dúvida Técnica, Administrativa e Exceção.

---

## 4. Estilo de documentação

- As soluções arquiteturais finais devem ser documentadas mantendo a separação explícita entre a responsabilidade do orquestrador (n8n) e as instruções do Agente (Prompt).
- Toda alteração significativa que impacte custo ou latência no fluxo deve ser formalizada em um ADR (Architecture Decision Record).

---

## 5. Qualidade esperada

- Zero tolerância a alucinações estruturais: o LLM classificador deve retornar exclusivamente um objeto JSON válido, sem prefixos ou formatações Markdown ao redor do código (ex: sem blocos \`\`\`json).
- O arquivo `.json` exportado do workflow n8n não deve conter credenciais, senhas ou tokens de API em plain text.

---

## 6. Exemplos de boas respostas
```
Decisão: Utilizar o nó "Switch" nativo do n8n para rotear o fluxo após o output do LLM.
Motivo: Delegar o roteamento para um nó determinístico evita que o LLM precise disparar webhooks manualmente, reduzindo falhas por alucinação, facilitando a observabilidade visual e mantendo o custo computacional baixo.
```


---

## 7. Exemplos de más respostas

```
Resposta gerada pela IA: "Entendo que você esteja doente. O prazo foi adiado para você. Aqui está a resolução completa da função em Python: [código final]."

Por que é ruim: Fere criticamente as restrições arquiteturais. A IA usurpou a autoridade do professor titular ao tentar alterar prazos e quebrou o modelo educacional Socrático ao entregar o código pronto em vez de fazer perguntas guiadoras.
```

## 8. Princípios-guia

```
O agente deve sempre explicar a racionalidade técnica antes de implementar uma mudança.
O agente deve preferir soluções simples, testáveis e com alta observabilidade.
O agente nunca deve mascarar incertezas; casos ambíguos devem escalar para revisão humana.
O agente deve registrar o motivo pelo qual alternativas concorrentes foram descartadas.
```
