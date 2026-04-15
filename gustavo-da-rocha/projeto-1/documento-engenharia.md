# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** [Gustavo da Rocha Machado Quirino]
> **Matrícula:** [251021321]
> **Domínio:** [8. Justiça]
> **Função do agente:** [8. Geração de respostas (Simplificação)]
> **Restrição obrigatória:** [4. Explicabilidade]

---

## 1. Problema e Contexto

_Dificuldade de compreensão de decisões judiciais por cidadãos leigos devido ao uso de termos técnicos complexos ("juridiquês"). O agente traduz esses termos garantindo a rastreabilidade da informação para todos os públicos._

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Cidadão Comum (Leigo)| Usuário final e principal beneficiário|Compreender o andamento de seus processos judiciais sem a barreira do "juridiquês", garantindo autonomia e transparência. |
|Advogados |Facilitador da comunicação com o cliente | Reduzir o tempo gasto em explicar termos processuais básicos e repetitivos, focando em tarefas de maior valor estratégico.|

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O agente deve processar textos jurídicos (sentenças/despachos) e gerar uma versão em linguagem simples.| Alta  |
| RF02 |O agente deve incluir, para cada explicação, o trecho original correspondente entre parênteses para fins de auditoria. |Alta |
| RF03 | O agente deve classificar o desfecho da decisão (ex: procedência, improcedência ou decisão interlocutória).|Média |
| RF04 | O agente deve permitir a entrada de novos textos via terminal em um loop contínuo de interação.|Baixa |


---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O processamento deve ser 100% offline, garantindo a privacidade dos dados sensíveis do usuário.| Privacidade / Segurança / |
| RNF02 |O tempo de resposta para uma sentença de até 2.000 caracteres não deve ultrapassar 15 segundos. |Desempenho |
| RNF03 | A saída deve ser formatada em Markdown para garantir a legibilidade das citações e negritos.|Usabilidade |

---

## 5. Casos de Uso


### Caso de uso 1: 

- **Ator:** Usuário leigo
- **Pré-condição:** 
- **Fluxo principal:**
  1. Cola sentença 
  2. IA processa localmente
  3. Exibe resumo citado. 

---

## 6. Fluxo do Agente


```
Entrada → Prompt Estruturado → Inferência LLM Local → Saída com Citações.
```

---

## 7. Arquitetura do Sistema


- **Tipo de agente:** Pipeline Sequencial.
- **LLM utilizado:** Llama3 8B
- **Componentes principais:**
  - [X] Módulo de entrada - pyrhon
  - [X] Processamento / LLM
  - [X] Módulo de saída

---

## 8. Estratégia de Avaliação

- **Métricas definidas:** Presença de citações (Explicabilidade) e tempo de resposta.
- **Conjunto de testes:** 5 sentenças reais de tribunais brasileiros, exemplos tirados da internet.
- **Método de avaliação:** manual

---

## 9. Referências


1. CONSELHO NACIONAL DE JUSTIÇA (CNJ). Resolução nº 332 de 21/08/2020.
2. OPENAI. OpenAI Python Library v2.30.0 Documentation. Disponível em: https://github.com/openai/openai-python. (Referência da biblioteca de integração utilizada no código).
3. Guia de Local LLMs: https://lmstudio.ai
