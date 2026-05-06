# Mentorship Pack

> **Projeto:** Triagem Inteligente de Demandas Academicas
> **Aluno(a):** Carlos Henrique Souza Bispo

---

## 1. Orientacoes de julgamento

Como o agente deve tomar decisoes:

- Priorizar seguranca operacional antes de automacao agressiva
- Explicitar incerteza e preferir escalonamento humano em baixa confianca
- Favorecer solucoes simples de manter e auditar
- Registrar racionalidade de cada decisao tecnica relevante

---

## 2. Padroes de arquitetura

Arquitetura orientada a fluxo (n8n), com separacao de responsabilidades:

- camada de entrada/normalizacao
- camada de decisao com IA
- camada de regras e validacao
- camada de roteamento/integracao
- camada de observabilidade/persistencia

---

## 3. Padroes de codigo

Convencoes que o agente deve respeitar:

- Linguagem: Python 3.11+
- Estilo: funcoes pequenas, nomes explicitos, sem efeitos colaterais ocultos
- Testes: pytest com casos para classificacao, fallback e regressao basica

---

## 4. Estilo de documentacao

- Escrever em portugues tecnico e objetivo
- Explicar o motivo da decisao antes da implementacao final
- Manter rastreabilidade entre runbook, ADR, evidencias e merge-pack

---

## 5. Qualidade esperada

Entrega aceitavel exige:

- tres solucoes demonstraveis
- testes passando
- decisao final justificada por comparacao objetiva
- evidencias reproduziveis de funcionamento

---

## 6. Exemplos de boas respostas

```text
Exemplo 1:
"A entrada foi classificada como financeiro com confianca 0.82.
Como o RA foi identificado e a urgencia e alta, a decisao e notificar o time financeiro de plantao.
Alternativas descartadas: resposta automatica direta (risco de erro) e escalonamento manual (custo alto)."
```

---

## 7. Exemplos de mas respostas

```text
Exemplo 1:
"Encaminhei para financeiro porque pareceu certo."

Problemas:
- nao informa confianca
- nao registra dados extraidos
- nao lista alternativa nem risco
```

---

## 8. Principios-guia

```text
O agente deve sempre explicar a decisao tecnica antes de implementar.
O agente deve preferir solucoes simples, testaveis e observaveis.
O agente nao deve esconder incertezas.
O agente deve registrar alternativas descartadas.
```
