# Mentorship Pack

> **Projeto:** Curadoria Automática de Artigos Científicos
> **Aluno(a):** Carlos Eduardo Rodrigues

---

## 1. Orientações de julgamento

- Priorizar rastreabilidade antes de complexidade.
- Preferir respostas verificáveis em vez de respostas impressionantes.
- Registrar incerteza, alternativas e limites sempre que a decisão depender da IA.

---

## 2. Padrões de arquitetura

- Fluxo n8n orientado a eventos: entrada -> normalização -> IA -> validação -> decisão -> persistência.
- Usar um estágio de validação para evitar decisões baseadas em dados incompletos.

---

## 3. Padrões de código

- Linguagem: JSON do n8n e, se necessário, JavaScript simples em nós de função.
- Estilo: nomes claros para nós, dados estruturados e expressões curtas.
- Testes: casos com artigo relevante, artigo irrelevante, entrada incompleta e baixa confiança.

---

## 4. Estilo de documentação

- Explicar a decisão técnica antes de implementá-la.
- Explicitar a motivação de cada desvio do fluxo principal.
- Registrar evidências com data, entrada de teste e resultado.

---

## 5. Qualidade esperada

- O fluxo deve ser fácil de auditar.
- A decisão da IA deve alterar o caminho do fluxo de forma observável.
- As falhas devem ser tratadas sem derrubar toda a automação.

---

## 6. Exemplos de boas respostas

```text
Exemplo 1:
O artigo parece relevante, mas a confiança é 0.58 e o DOI não foi validado. Vou encaminhar para revisão humana e registrar a ausência de metadados.
```

---

## 7. Exemplos de más respostas

```text
Exemplo 1:
Este artigo é excelente e está aprovado para o acervo.
Motivo: confio no modelo.
```

Isso é inadequado porque ignora limites, não registra evidência e confunde triagem com decisão editorial.

---

## 8. Princípios-guia

```text
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas.
O agente deve registrar alternativas descartadas.
```
