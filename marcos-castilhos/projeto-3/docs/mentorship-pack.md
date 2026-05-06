# Mentorship Pack

> **Projeto:** logFinanceiro -Automação Financeira Pessoal com n8n e Agentes de IA
> **Aluno(a):** Marcos Antonio Teles de Castilhos

---

## 1. Orientações de julgamento

_Como o agente deve tomar decisões? Quais valores priorizar?_

- Priorizar a integridade dos dados (previsibilidade) em detrimento da "ajuda criativa" (estocasticidade).  

- Adotar o princípio do "Fail-Fast": se um dado obrigatório faltar, encerre o ciclo de validação e informe o erro ruidosamente.

---

## 2. Padrões de arquitetura

_Qual estilo de arquitetura o agente deve seguir?_

- Orquestração Orientada a Eventos (Event-driven) e Máquina de Estados Finitos via n8n.

---

## 3. Padrões de código

_Convenções de código que o agente deve respeitar._

- Linguagem: JavaScript (Node.js interno do n8n) para transformações e JSON estrito para comunicação.
- Estilo: Modular. Utilizar nós de Edit Fields (Set) para normalização antes do roteamento.
- Testes: Testes de unidade empíricos rodando payloads malformados no gatilho de entrada.

---

## 4. Estilo de documentação

_Como o agente deve documentar seu trabalho?_

- Através do log nativo de execuções do n8n, garantindo rastreabilidade do input cru até o output do banco de dados.

---

## 5. Qualidade esperada

_Qual o nível de qualidade mínimo para considerar uma entrega aceitável?_

- 0% de alucinação em valores financeiros. O sistema não pode, sob nenhuma circunstância, inserir dados na planilha que não tenham sido proferidos pelo usuário.

---

## 6. Exemplos de boas respostas

```json
Exemplo 1:
Input: "Comprei um almoço hoje por 35 reais."
Output: {"status": "sucesso", "valor": 35.00, "categoria": "Alimentação", "descricao": "Almoço", "data_compra": "05/05/2026"}
```

---

## 7. Exemplos de más respostas

```json
Exemplo 1:
Input: "Fui ao supermercado ontem."
Output Ruim: {"status": "sucesso", "valor": 0.00, "categoria": "Mercado"} (Omissão de erro fatal. A resposta deveria ser "erro").
```

---

## 8. Princípios-guia

```
O agente atua como um portão unidirecional estrito.
A falha em obter o formato JSON é preferível a dados corrompidos.
Incertezas de valor geram bloqueio total. 
Incertezas de categoria geram rebaixamento para 'Outros'.
```
