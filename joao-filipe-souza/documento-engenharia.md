# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** João Filipe de Oliveira Souza
> **Matrícula:** 231035141
> **Domínio:** Educação
> **Função do agente:** Analise de Sentimento
> **Restrição obrigatória:** Privacidade (LGPD)

---

## 1. Problema e Contexto

Com o aumento do uso de plataformas digitais na educação, instituições de ensino recebem uma grande quantidade de feedbacks de alunos sobre aulas, professores e disciplinas. No entanto, analisar manualmente esses comentários é um processo demorado e sujeito a erros.
Além disso, é necessário garantir a privacidade dos alunos, evitando o armazenamento ou exposição de dados pessoais, em conformidade com a Lei Geral de Proteção de Dados (LGPD).
Dessa forma, surge a necessidade de um agente de IA capaz de analisar automaticamente os comentários dos alunos, classificando o sentimento (positivo, negativo ou neutro) e fornecendo uma explicação simples, sem armazenar dados sensíveis.
O público-alvo são professores, coordenadores e instituições de ensino que desejam entender melhor a percepção dos alunos de forma rápida e segura.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
|Professores| Usuário final | Entender o feedback dos alunos |
|Coordeadores|Gestores| Tomar decisões com base nos feedbacks|

---

## 3. Requisitos Funcionais (RF)
| ID   | Descrição                                               | Prioridade |
| ---- | ------------------------------------------------------- | ---------- |
| RF01 | Receber comentários de alunos como entrada              | Alta       |
| RF02 | Classificar o sentimento (positivo, negativo ou neutro) | Alta       |
| RF03 | Gerar uma explicação simples para a classificação       | Alta       |
| RF04 | Processar múltiplos comentários em sequência            | Média      |
| RF05 | Exibir os resultados de forma clara ao usuário          | Média      |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID    | Descrição                                                  | Categoria        |
| ----- | ---------------------------------------------------------- | ---------------- |
| RNF01 | Não armazenar dados pessoais dos usuários                  | Segurança (LGPD) |
| RNF02 | Garantir resposta em tempo aceitável (< 3s por comentário) | Desempenho       |
| RNF03 | Interface simples e fácil de usar                          | Usabilidade      |
| RNF04 | Baixo custo de execução (uso otimizado de API)             | Econômico        |

---

## 5. Casos de Uso

### Caso de uso 1: Análise de feedback individual

- **Ator:** Professor
- **Pré-condição:** Comentário de aluno disponível no sistema.
- **Fluxo principal:**
  1. O professor insere o texto do comentário.
  2. O agente processa o texto localmente via Ollama.
  3. O sistema exibe a classificação (Positivo/Negativo/Neutro) e a justificativa.
- **Pós-condição:** O sentimento do feedback é identificado sem envio de dados para nuvem.

### Caso de uso 2: [Nome]

- **Ator:** Coordenador
- **Pré-condição:** Lista de comentários disponível
- **Fluxo principal:**
  1. O usuário envia vários comentários
  2. O sistema processa cada um individualmente
  3. O agente retorna classificação para cada comentário
  4. O sistema apresenta os resultados organizados
- **Pós-condição:** Todos os comentários são analisados com sucesso
---

## 6. Fluxo do Agente

```
Comentário → Pré-processamento → LLM → Classificação → Explicação → Saída
```

---

## 7. Arquitetura do Sistema

- **Tipo de agente:** Pipeline sequencial de inferência local.
- **LLM utilizado:** Ollama (modelo Llama 3 ou Mistral).
- **Componentes principais:**
  - [x] Módulo de entrada: Leitura de arquivo JSON ou input de texto.
  - [x] Processamento / LLM: Orquestração via biblioteca `ollama-python`.
  - [ ] Ferramentas externas (tools)
  - [ ] Memória
  - [x] Módulo de saída: Terminal ou arquivo formatado.

A escolha do Ollama justifica-se pelo **RNF01 (LGPD)**, garantindo que os dados dos alunos nunca saiam da infraestrutura local.

---

## 8. Estratégia de Avaliação

- **Métricas definidas:** Acurácia da classificação e latência de inferência local.
- **Conjunto de testes:** 10 exemplos reais baseados no arquivo `comentarios.json`.
- **Método de avaliação:** Comparação manual entre o rótulo esperado e a saída da IA.

---

## 9. Referências

1. Documentação Oficial Ollama: https://github.com/ollama/ollama
2. Repositório da biblioteca Python `ollama`: https://pypi.org/project/ollama/
