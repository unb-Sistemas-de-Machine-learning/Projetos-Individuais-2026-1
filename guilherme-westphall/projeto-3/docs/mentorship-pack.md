# Mentorship Pack

> **Projeto:** Automação inteligente de emissão de notas fiscais com aprovação humana
> **Aluno(a):** Guilherme Westphall

---

## 1. Orientações de julgamento

O agente de apoio ao desenvolvimento deve tomar decisões priorizando segurança operacional, rastreabilidade e simplicidade. Como o domínio envolve emissão de notas fiscais e comunicação com contratantes, qualquer automação deve ser conservadora e manter aprovação humana explícita antes de ações externas.

- Priorizar cálculos determinísticos para valores financeiros, períodos, horas e totais.
- Usar IA apenas para validação, classificação de risco, recomendação de fluxo e geração controlada de mensagens.
- Preferir revisão manual quando houver ambiguidade, dados ausentes ou baixa confiança.
- Explicar decisões técnicas antes de implementar mudanças relevantes.
- Registrar alternativas consideradas, inclusive soluções descartadas.
- Evitar complexidade que não aumente a qualidade da automação, a auditabilidade ou a segurança do fluxo.
- Tratar credenciais e tokens como dados sensíveis, usando placeholders, variáveis de ambiente ou credenciais do n8n.

---

## 2. Padrões de arquitetura

A arquitetura deve seguir um modelo de orquestração por workflow, com separação clara entre cálculo determinístico, decisão assistida por IA, aprovação humana e execução de ações externas.

- O n8n deve ser o orquestrador principal do processo.
- O Productive.io deve ser tratado como fonte de dados das entradas de tempo.
- Nós de código devem calcular período, horas, valor por hora, total e avisos objetivos.
- O modelo de IA deve receber dados consolidados e retornar uma recomendação estruturada.
- Um nó de normalização deve validar ou corrigir a resposta da IA antes de qualquer condicional.
- Condicionais do n8n devem direcionar o fluxo entre aprovação, revisão manual e interrupção.
- Telegram deve ser usado como etapa de aprovação humana.
- Gmail e geração/exportação de nota fiscal devem ocorrer somente após aprovação explícita.
- Logs, prints e outputs relevantes devem ser salvos em `docs/evidence/`.

---

## 3. Padrões de código

Convenções de código que o agente deve respeitar.

- Linguagem: JavaScript em nós de código do n8n, com scripts auxiliares apenas se forem necessários para testes, simulação ou validação.
- Estilo: código simples, legível, com nomes explícitos e sem lógica financeira escondida em prompts.
- Testes: criar casos para cálculo de período, soma de entradas, tratamento de resposta malformada da IA, baixa confiança e bloqueio de envio sem aprovação.
- Dados sensíveis: não salvar tokens reais, IDs privados ou credenciais em arquivos versionados.
- Validação: toda saída de IA deve ser parseada e validada antes de influenciar o fluxo.
- Erros: falhas de API, entradas vazias e respostas inválidas devem encaminhar para revisão manual ou interrupção.
- Comentários: usar comentários curtos apenas para explicar decisões não óbvias, especialmente regras de período e fallback.

---

## 4. Estilo de documentação

O agente deve documentar o trabalho de forma objetiva, auditável e orientada a decisão.

- Escrever em português brasileiro com gramática e acentuação corretas.
- Usar linguagem técnica clara, sem exagerar na complexidade.
- Separar intenção, decisão, implementação, evidência e limitação.
- Registrar decisões arquiteturais em ADRs.
- Manter os artefatos coerentes entre si: `mission-brief.md`, `agent.md`, `mentorship-pack.md`, `workflow-runbook.md`, ADR, evidências e relatório final.
- Usar placeholders claros, como `[TO BE DEFINED]`, quando uma informação ainda não estiver confirmada.
- Não apresentar protótipos incompletos como solução final.
- Explicitar riscos conhecidos, especialmente segurança de credenciais, erro da IA e envio sem aprovação.

---

## 5. Qualidade esperada

Uma entrega aceitável deve demonstrar que a automação é funcional, auditável e segura o suficiente para um processo financeiro sensível.

- O fluxo deve deixar claro onde a IA influencia a decisão.
- A IA não deve ser responsável por cálculos financeiros.
- O envio ao contratante deve depender de aprovação humana explícita.
- Três soluções devem ser descritas, prototipadas ou demonstradas, mesmo que tenham níveis diferentes de maturidade.
- A solução escolhida deve ser justificada por comparação entre custo, complexidade, qualidade, riscos, manutenibilidade e adequação ao problema.
- Testes e evidências devem cobrir caminho feliz, baixa confiança, dados ausentes e resposta inválida da IA.
- O workflow exportado deve ser revisado para remover ou substituir credenciais reais.
- A documentação final deve permitir que um avaliador entenda o processo sem depender de explicações externas.

---

## 6. Exemplos de boas respostas

```text
Exemplo 1:
Decisão: manter o cálculo de horas e valor total em nó de código, antes da chamada ao modelo de IA.
Motivo: valores financeiros precisam ser reproduzíveis, auditáveis e não devem depender de geração probabilística.
Alternativas consideradas: calcular tudo no prompt; pedir que a IA confira e recalcule os totais.
Confiança: alta.
```

```text
Exemplo 2:
Decisão: encaminhar a execução para revisão manual quando `entry_count` for zero ou quando a IA retornar JSON inválido.
Motivo: nesses casos, o fluxo não tem evidência suficiente para solicitar aprovação normal ou enviar a nota fiscal.
Alternativas consideradas: continuar com aviso no e-mail; tentar inferir dados ausentes.
Confiança: alta.
```

```text
Exemplo 3:
Decisão: usar Telegram como etapa obrigatória de aprovação antes de Gmail.
Motivo: a emissão e o envio de nota fiscal têm impacto financeiro e reputacional; a aprovação humana reduz o risco de envio incorreto.
Alternativas consideradas: envio totalmente automático; aprovação apenas por logs internos.
Confiança: alta.
```

---

## 7. Exemplos de más respostas

```text
Exemplo 1:
"Vou pedir para a IA recalcular as horas e o valor total porque isso simplifica o fluxo."

Por que é ruim:
Transfere cálculo financeiro para um componente probabilístico, reduz auditabilidade e contradiz os limites definidos no mission brief e no agent.md.
```

```text
Exemplo 2:
"Se a IA retornar uma resposta inválida, o fluxo deve tentar enviar o e-mail mesmo assim."

Por que é ruim:
Uma resposta inválida elimina a confiabilidade da etapa de decisão. O caminho correto é revisão manual ou interrupção.
```

```text
Exemplo 3:
"O e-mail ao contratante pode mencionar que a IA validou a nota fiscal e que a aprovação está pendente."

Por que é ruim:
Expõe detalhes internos do processo, mistura comunicação externa com estado operacional e viola a regra de e-mail simples e profissional.
```

---

## 8. Princípios-guia

```text
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas.
O agente deve registrar alternativas descartadas.
O agente deve manter cálculos financeiros fora da IA.
O agente deve exigir aprovação humana antes de qualquer envio externo.
O agente deve tratar credenciais como segredos e nunca versionar tokens reais.
O agente deve transformar falhas, baixa confiança e dados ausentes em revisão manual ou interrupção segura.
```
