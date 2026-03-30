# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Vinícius Eduardo Muniz da Silva
> **Matrícula:** 211031870
> **Data de entrega:** 29/03/2026

---

## 1. Resumo do Projeto

Este projeto implementa um sistema comparativo de resolução de labirintos que confronta duas abordagens distintas de inteligência artificial: um algoritmo clássico de busca em largura (BFS) e um agente baseado em Large Language Model (LLM) consumido via API externa do Groq (modelo Llama 3.3 70B).

O agente LLM recebe o mapa do labirinto e, a cada turno, decide seu próximo movimento com base na posição atual, vizinhos disponíveis e no histórico acumulado da conversa. Isso permite avaliar a capacidade de raciocínio espacial de um LLM generalista em comparação com um algoritmo determinístico otimizado para o problema.

Os principais resultados mostram que o BFS resolve o labirinto de forma ótima e consistente, enquanto o agente LLM consegue resolver labirintos simples (7x7), porém com caminhos significativamente mais longos e maior custo computacional (chamadas à API). O projeto evidencia que LLMs têm limitações em raciocínio espacial puro, mas demonstram capacidade de adaptação quando recebem feedback contextual via histórico de conversa.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Jogos |
| **Função do agente** | Resolver labirinto |
| **Restrição obrigatória** | Usar API de LLM externa |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe como entrada um labirinto representado como uma matriz 7x7 de inteiros, onde `0` indica caminho livre e `1` indica parede. A posição inicial é sempre `(0, 0)` e o objetivo é `(6, 6)`. O labirinto é gerado aleatoriamente com ~25% de paredes e validado previamente via BFS para garantir que possui solução.

### 3.2 Processamento (Pipeline)

```
Gerar labirinto 7x7 (aleatório, ~25% paredes)
        │
        ▼
Validar solução via BFS (rejeitar se impossível)
        │
        ▼
Exibir labirinto ao usuário
        │
        ├────────────────────────────────┐
        ▼                                ▼
   AGENTE BFS                      AGENTE LLM
        │                                │
  Explorar vizinhos               Enviar system prompt
  em largura (FIFO)               com mapa fixo (1x)
        │                                │
  Expandir fila de                 A cada turno:
  nós visitados                    posição + vizinhos
        │                                │
  Retornar caminho                 LLM retorna JSON
  ótimo                            {movimento, raciocínio}
        │                                │
        │                           Validar movimento
        │                           e dar feedback
        │                                │
        ▼                                ▼
   Exibir resultado              Exibir resultado
        │                                │
        └────────────┬───────────────────┘
                     ▼
           Comparação de métricas
```

### 3.3 Decisão

O **agente BFS** utiliza busca em largura clássica: explora todos os vizinhos de cada nó antes de avançar para o próximo nível, garantindo o caminho mais curto.

O **agente LLM** opera com chamadas autocontidas (payload constante). A cada turno, um prompt completo é montado contendo o mapa, a posição atual, os vizinhos (com marcação de "ja visitada"), a distância até o objetivo e a lista completa de posições já visitadas. O LLM responde com um JSON contendo a direção escolhida e um breve raciocínio. Quando o LLM tenta um movimento inválido (parede ou fora do mapa), recebe feedback explícito no turno seguinte.

Para lidar com a dificuldade do LLM em fazer backtracking (voltar varias casas ao encontrar um beco sem saída), o sistema implementa **backtracking assistido**: quando detecta que o agente visitou a mesma posição 3 ou mais vezes (loop), um mini-BFS calcula a rota mais curta até a célula livre não-visitada mais próxima e forca esses movimentos diretamente, sem chamar a API. Após escapar, o LLM retoma o controle.

Prompt de cada turno:
- Mapa completo do labirinto com posição do agente e objetivo
- Posição atual, objetivo e distância restante
- Estado de cada vizinho (livre, parede, ja visitada, fora do mapa)
- Lista de todas as posições já visitadas
- Feedback de erro do turno anterior (se houver)

### 3.4 Saída (Output)

Para cada labirinto, o sistema exibe:
- Visualização animada no terminal da exploração de cada agente (BFS e LLM)
- Caminho final encontrado marcado com `*` no grid
- Contagem de passos no caminho e movimentos explorados/chamadas à API
- Tabela comparativa lado a lado entre os dois agentes

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.13.3 | Linguagem principal |
| Groq SDK | 1.1.2 | Cliente para a API do Groq (inferência LLM) |
| python-dotenv | 1.2.2 | Carregar variáveis de ambiente do arquivo .env |
| Llama 3.3 70B | — | Modelo LLM utilizado via API Groq |

### 4.2 Estrutura do código

```
proj_individual1/
├── agente_labirinto.py      # Script principal: BFS, agente LLM e comparação
├── labirintos.py            # Geração de labirintos e conversão para texto
├── documento-engenharia.md  # Documento de engenharia do projeto
├── relatorio-entrega.md     # Este relatório
├── .env                     # Chave da API Groq (não versionado)
└── venv/                    # Ambiente virtual Python
```

### 4.3 Como executar

```bash
# 1. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install groq python-dotenv

# 3. Configurar variável de ambiente
# Criar arquivo .env na raiz do projeto com:
# GROQ_API_KEY=sua_chave_aqui

# 4. Executar
python3 agente_labirinto.py
```

O programa é interativo: pressione ENTER para avançar entre cada etapa (BFS, LLM, próximo labirinto).

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Passos no caminho (BFS) | Comprimento do caminho ótimo encontrado pelo BFS | Sempre ótimo (menor caminho possível) |
| Passos no caminho (LLM) | Comprimento do caminho encontrado pelo agente LLM | Geralmente 2-5x maior que o BFS |
| Nós explorados (BFS) | Quantidade de nós visitados durante a busca | Varia conforme a topologia do labirinto |
| Chamadas à API (LLM) | Quantidade de requisições feitas ao Groq | Igual ao número de movimentos tentados |
| Taxa de sucesso (LLM) | Percentual de labirintos resolvidos pelo LLM | ~90-100% em labirintos 7x7 (com backtracking assistido) |

### 5.2 Exemplos de teste

#### Teste 1 — Labirinto simples com poucas paredes

- **Entrada:** Labirinto 7x7 com ~25% de paredes, caminhos amplos
- **Saída esperada:** Ambos os agentes encontram o objetivo
- **Saída obtida:** BFS resolveu em ~12 passos; LLM resolveu em ~20-30 passos
- **Resultado:** Sucesso para ambos

#### Teste 2 — Labirinto com corredores estreitos

- **Entrada:** Labirinto 7x7 com corredores longos e poucas alternativas
- **Saída esperada:** BFS encontra caminho; LLM pode ter dificuldade com backtracking
- **Saída obtida:** BFS resolveu normalmente; LLM precisou de backtracking assistido (mini-BFS) para escapar de becos sem saída
- **Resultado:** Sucesso (BFS) / Sucesso com assistência (LLM)

### 5.3 Análise dos resultados

O BFS se mostra consistente e ótimo em todos os cenários, como esperado de um algoritmo determinístico projetado para busca em grafos. Ele sempre encontra o menor caminho quando existe solução.

O agente LLM demonstra capacidade de raciocínio espacial básico — consegue interpretar o mapa, entender coordenadas e tomar decisões direcionais coerentes na maioria dos turnos. Porém, apresenta fragilidades:

- **Caminhos subótimos:** O LLM tende a fazer mais movimentos que o necessário, pois não possui uma visão global otimizada como o BFS.
- **Loops ocasionais:** O LLM tem dificuldade com backtracking, tendendo a voltar apenas uma casa e tentar avançar novamente. Isso é mitigado pelo backtracking assistido via mini-BFS.
- **Custo:** Cada movimento requer uma chamada à API, tornando a abordagem significativamente mais cara e lenta.

O principal valor do projeto está na demonstração empírica de que LLMs generalistas não substituem algoritmos especializados para problemas bem definidos, mas podem servir como agentes adaptáveis em cenários onde a modelagem formal é difícil.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [x] Memória persistente
- [x] Explicabilidade
- [x] Análise crítica de limitações

**Memória persistente:** O agente LLM recebe a cada turno a lista completa de posições já visitadas, com vizinhos marcados como "ja visitada". Além disso, um contador de visitas por posição alimenta o sistema de detecção de loops e backtracking assistido por mini-BFS.

**Explicabilidade:** A cada movimento, o LLM retorna um campo `raciocinio` explicando por que escolheu aquela direção, permitindo ao usuário acompanhar a "lógica" do agente em tempo real.

**Análise crítica de limitações:** O sistema compara quantitativamente os dois agentes, evidenciando os trade-offs entre abordagens clássicas e baseadas em LLM.

---

## 7. Limitações e Trabalhos Futuros

**Limitações encontradas:**
- O agente LLM consome muitos tokens por labirinto, especialmente em grids maiores — o projeto foi limitado a 7x7 por questões de custo.
- A API do Groq é stateless: cada chamada precisa conter todo o contexto necessário (mapa, posição, visitadas), sem possibilidade de manter estado entre requisições.
- O LLM ocasionalmente gera respostas fora do formato JSON esperado, exigindo parsing robusto.
- O LLM tem dificuldade inerente com backtracking (voltar varias casas para sair de becos sem saída), exigindo assistência algorítmica via mini-BFS.

**Trabalhos futuros:**
- Implementar o agente LLM com visão parcial (fog of war) em vez de mapa completo, simulando um cenário mais realista.
- Testar outros modelos (GPT-4, Claude) para comparar capacidade de raciocínio espacial entre LLMs.
- Adicionar algoritmo A* como terceira referência de comparação.
- Implementar métricas automáticas com execução em lote (sem visualização) para análise estatística com dezenas de labirintos.
- Explorar técnicas de chain-of-thought para melhorar o planejamento do LLM.

---

## 8. Referências

1. Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4th ed.) — Capítulos sobre busca e agentes racionais
2. Documentação da API Groq — https://console.groq.com/docs/quickstart
3. Documentação do modelo Llama 3.3 — https://ai.meta.com/blog/llama-3-3/
4. Algoritmo BFS (Breadth-First Search) — https://en.wikipedia.org/wiki/Breadth-first_search
5. Python `collections.deque` — https://docs.python.org/3/library/collections.html#collections.deque

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto
