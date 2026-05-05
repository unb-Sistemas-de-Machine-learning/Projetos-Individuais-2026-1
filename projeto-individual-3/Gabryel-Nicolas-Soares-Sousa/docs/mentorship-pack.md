# Mentorship Pack

> **Projeto:** Triagem Inteligente de Chamados de Suporte
> **Aluno(a):** Gabryel Nicolas Soares de Sousa

---

## 1. Orientações de julgamento

- Prefira a solução mais simples que atenda aos critérios de aceitação — complexidade sem benefício é um risco, não um diferencial
- Quando houver dúvida entre duas abordagens, escolha a mais observável e testável
- Declare incertezas explicitamente em vez de mascarar com complexidade técnica
- Registre alternativas descartadas com justificativa — a decisão documentada vale tanto quanto a decisão certa

---

## 2. Padrões de arquitetura

- O fluxo no n8n deve ser linear e legível: cada nó com uma responsabilidade clara
- A IA deve influenciar o **caminho do fluxo**, não apenas gerar texto decorativo
- Tratamento de erro deve ser explícito, com nó dedicado — nunca deixar falhas silenciosas
- Credenciais sempre configuradas via sistema de credenciais do n8n, nunca hardcoded

---

## 3. Padrões de código

- **Linguagem:** JavaScript (nós Code do n8n)
- **Estilo:** funções curtas, com comentários explicando o propósito de cada bloco
- **Testes:** ao menos um caso de teste por caminho do fluxo (alta urgência, baixa urgência, fallback)

---

## 4. Estilo de documentação

- Documentos escritos em português claro e direto
- Tabelas para comparações, listas para sequências, parágrafos para explicações contextuais
- Evidências nomeadas de forma descritiva: `teste-alta-urgencia.png`, não `screenshot1.png`
- Cada arquivo começa com cabeçalho identificando projeto e aluno

---

## 5. Qualidade esperada

- Fluxo no n8n com nós nomeados e legíveis — sem nós genéricos como "HTTP Request 1"
- Classificação da IA correta em ≥ 80% dos casos de teste documentados
- Todos os caminhos do Switch testados e com evidência registrada
- Documentação coerente com o que foi de fato implementado

---

## 6. Exemplos de boas respostas

```
Entrada: "Não consigo fazer login no sistema desde esta manhã, preciso urgente para acessar relatórios do cliente"

Saída esperada:
{"categoria": "suporte_tecnico", "urgencia": "alta", "resumo": "Usuário sem acesso ao sistema, impacto em relatórios de cliente", "confianca": "alta"}

Por quê é boa: categoria correta, urgência justificada pelo contexto, resumo objetivo, confiança coerente com a clareza da mensagem.
```

---

## 7. Exemplos de más respostas

```
Entrada: "Não consigo fazer login no sistema desde esta manhã"

Saída ruim:
"Claro! Entendi que você está com problemas de acesso. Aqui está minha análise:
{"categoria": "suporte_tecnico", "urgencia": "alta", ...}"

Por quê é ruim: incluiu texto fora do JSON, o que quebra o parse automático no nó Code do n8n e derruba o fluxo.
```

```
Entrada: "oi"

Saída ruim:
{"categoria": "suporte_tecnico", "urgencia": "alta", "resumo": "Usuário com problema urgente", "confianca": "alta"}

Por quê é ruim: inventou categoria e urgência sem base na mensagem. O correto seria confianca: "baixa" e categoria: "outros".
```

---

## 8. Princípios-guia

```
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas.
O agente deve registrar alternativas descartadas.
```
