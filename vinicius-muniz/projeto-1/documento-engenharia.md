# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Vinícius Eduardo Muniz da Silva
> **Matrícula:** 211031870
> **Domínio:** Jogos
> **Função do agente:** Resolver labirinto
> **Restrição obrigatória:** Usar API de LLM externa

---

## 1. Problema e Contexto

O projeto aborda o problema de navegação autônoma em labirintos gerados aleatoriamente, comparando duas abordagens distintas: um algoritmo clássico de busca (BFS) e um agente baseado em Large Language Model (LLM) consumido via API externa (Groq).

Labirintos são um domínio clássico em inteligência artificial para estudar busca, planejamento e tomada de decisão. A relevância do projeto está em investigar se um LLM generalista — treinado em linguagem natural, não em pathfinding — consegue competir com um algoritmo determinístico projetado especificamente para o problema. Isso levanta questões práticas sobre quando utilizar LLMs versus algoritmos tradicionais.

O público-alvo são estudantes e pesquisadores de Machine Learning interessados em entender os limites e capacidades de agentes baseados em LLM aplicados a problemas de raciocínio espacial.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Estudante/Desenvolvedor | Autor e operador do sistema | Implementar, executar e analisar o desempenho comparativo dos agentes |
| Professor/Avaliador | Avaliador acadêmico | Verificar a aplicação correta de conceitos de IA, busca e uso de APIs de LLM |
| Comunidade acadêmica | Consumidora dos resultados | Compreender trade-offs entre abordagens clássicas e baseadas em LLM para problemas de navegação |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O sistema deve gerar labirintos aleatórios em grid com garantia de solução | Alta |
| RF02 | O sistema deve resolver labirintos utilizando o algoritmo BFS com visualização passo a passo | Alta |
| RF03 | O sistema deve resolver labirintos utilizando um agente LLM via API do Groq, que decide cada movimento individualmente | Alta |
| RF04 | O sistema deve exibir a contagem de movimentos explorados/realizados por cada agente | Alta |
| RF05 | O sistema deve apresentar uma comparação lado a lado dos resultados (passos, movimentos, sucesso/falha) | Média |
| RF06 | O sistema deve pausar entre cada etapa, aguardando confirmação do usuário para prosseguir | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O agente LLM deve responder em no máximo 5 segundos por movimento para manter fluidez na visualização | Desempenho |
| RNF02 | A chave de API deve ser carregada via variável de ambiente (.env), sem exposição no código-fonte | Segurança |
| RNF03 | O agente LLM deve ter um limite máximo de 300 tentativas para evitar loops infinitos e consumo excessivo de API | Confiabilidade |
| RNF04 | A visualização no terminal deve ser clara, com símbolos distintos para agente, objetivo, paredes e caminho | Usabilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Resolver labirinto com BFS

- **Ator:** Usuário (via terminal)
- **Pré-condição:** O programa foi iniciado e um labirinto solúvel foi gerado
- **Fluxo principal:**
  1. O sistema exibe o labirinto gerado com posição inicial (A) e objetivo (G)
  2. O usuário pressiona ENTER para iniciar a resolução via BFS
  3. O BFS explora o labirinto com visualização animada no terminal
  4. O sistema exibe o caminho encontrado e a contagem de nós explorados
- **Pós-condição:** O caminho ótimo é exibido no grid e as métricas são apresentadas

### Caso de uso 2: Resolver labirinto com Agente LLM

- **Ator:** Usuário (via terminal)
- **Pré-condição:** O BFS já resolveu o labirinto e o usuário pressionou ENTER para iniciar o agente LLM
- **Fluxo principal:**
  1. O agente LLM recebe o mapa completo, posição atual e vizinhos via prompt
  2. O LLM retorna um JSON com o movimento escolhido e seu raciocínio
  3. O sistema valida o movimento e atualiza a posição do agente no grid
  4. Os passos 1-3 se repetem até o agente alcançar o objetivo ou atingir o limite de tentativas
- **Pós-condição:** O resultado do agente LLM é exibido junto com a comparação de desempenho contra o BFS

---

## 6. Fluxo do Agente

```
Gerar labirinto aleatório
        │
        ▼
Validar solução via BFS (descartar se impossível)
        │
        ▼
Exibir labirinto ao usuário
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
   AGENTE BFS                        AGENTE LLM
        │                                  │
  Explorar vizinhos               Enviar estado do mapa
  em largura (FIFO)               para Groq API (Llama 3.3)
        │                                  │
  Marcar visitados                 Receber JSON com
  e expandir fila                  movimento + raciocínio
        │                                  │
  Encontrar caminho                Validar e executar
  ótimo                            movimento no grid
        │                                  │
        ▼                                  ▼
   Exibir resultado                Exibir resultado
        │                                  │
        └──────────┬───────────────────────┘
                   ▼
         Comparação de métricas
         (passos, movimentos, sucesso)
                   │
                   ▼
         Aguardar ENTER para próximo labirinto
```

---

## 7. Arquitetura do Sistema

- **Tipo de agente:** Pipeline sequencial com agente tool-using (LLM decide ações a cada passo)
- **LLM utilizado:** Llama 3.3 70B Versatile, servido via API do Groq
- **Componentes principais:**
  - [x] **Módulo de entrada:** Gerador de labirintos aleatórios com validação de solubilidade (`labirintos.py`)
  - [x] **Processamento / LLM:** Agente BFS (algoritmo clássico) e Agente LLM (chamadas à API Groq a cada movimento)
  - [x] **Ferramentas externas (tools):** API do Groq para inferência do Llama 3.3 70B
  - [x] **Memória:** Lista de posições já visitadas enviada ao LLM a cada turno + detecção de loops com backtracking assistido por mini-BFS
  - [x] **Módulo de saída:** Visualização animada no terminal + tabela comparativa de métricas

```
┌─────────────────────────────────────────────────┐
│                agente_labirinto.py              │
│                                                 │
│  ┌──────────────┐       ┌────────────────────┐  │
│  │ labirintos.py│       │    API Groq        │  │
│  │ (geração +   │       │  (Llama 3.3 70B)   │  │
│  │  validação)  │       └────────┬───────────┘  │
│  └──────┬───────┘                │              │
│         │                        │              │
│         ▼                        ▼              │
│  ┌─────────────┐      ┌──────────────────┐      │
│  │  Agente BFS │      │   Agente LLM     │      │
│  │ (busca em   │      │ (prompt → JSON   │      │
│  │  largura)   │      │  → movimento)    │      │
│  └──────┬──────┘      └────────┬─────────┘      │
│         │                      │                │
│         └──────────┬───────────┘                │
│                    ▼                            │
│           ┌───────────────┐                     │
│           │  Comparação   │                     │
│           │  de métricas  │                     │
│           └───────────────┘                     │
└─────────────────────────────────────────────────┘
```

---

## 8. Estratégia de Avaliação

- **Métricas definidas:**
  - **Passos no caminho final:** comprimento do caminho da origem ao destino (quanto menor, melhor)
  - **Movimentos explorados / chamadas à API:** custo computacional de cada abordagem
  - **Taxa de sucesso:** percentual de labirintos resolvidos com sucesso pelo agente LLM (BFS sempre resolve se há solução)
  - **Qualidade do caminho:** razão entre o caminho do LLM e o caminho ótimo do BFS (1.0 = ótimo)

- **Conjunto de testes:** 3 labirintos 7x7 gerados aleatoriamente por execução, com ~25% de paredes e garantia de solução

- **Método de avaliação:** Comparativo e visual — ambos os agentes resolvem o mesmo labirinto e os resultados são apresentados lado a lado no terminal, permitindo análise direta de eficiência e comportamento

---

## 9. Referências

1. Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4th ed.) — Capítulos sobre busca em espaço de estados e agentes racionais
2. Documentação da API Groq — https://console.groq.com/docs/quickstart
3. Documentação do modelo Llama 3.3 — https://ai.meta.com/blog/llama-3-3/
4. Algoritmo BFS (Breadth-First Search) — https://en.wikipedia.org/wiki/Breadth-first_search
5. Python `collections.deque` — https://docs.python.org/3/library/collections.html#collections.deque
