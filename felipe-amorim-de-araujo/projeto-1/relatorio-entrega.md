# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Felipe Amorim de Araujo
> **Matrícula:** 221022275
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

Leitores brasileiros enfrentam dois problemas recorrentes: dificuldade em descobrir novos livros compatíveis com seu gosto e falta de visibilidade sobre preços nas livrarias. O agente construído resolve os dois em um único fluxo.

O usuário informa os títulos que já leu em um formulário. O agente busca os metadados desses livros via Open Library, constrói uma consulta de similaridade e recupera candidatos de um catálogo vetorial (ChromaDB). Os candidatos têm seus preços verificados em tempo real nas livrarias Mercado Livre, Amazon BR e Estante Virtual, e recebem justificativas geradas pela API Gemini (Google) explicando a relação com o histórico de leitura. O usuário pode salvar títulos em uma lista de desejos e verificar preços sob demanda.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Cultura |
| **Função do agente** | Recomendação |
| **Restrição obrigatória** | Integração com API externa |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

Lista de títulos de livros já lidos pelo usuário, informada via formulário de texto (um título por linha). O usuário também seleciona a quantidade de recomendações desejadas (1 a 10).

### 3.2 Processamento (Pipeline)

```
Formulário (livros lidos)
    |
    v
book_fetcher: Open Library Search API → metadados + work_key
    |
    v
book_fetcher: Open Library Works API → descrição completa + subjects
    |
    v
rag: ChromaDB → busca por similaridade de embedding (exclui livros já lidos)
    |
    v
price_checker: Mercado Livre API + Amazon BR + Estante Virtual → preços por loja
    |
    v
agent._justify_all: Gemini API (gemini-3.1-flash-lite-preview) → justificativas em pt-BR em chamada única
    |
    v
Saída: recomendações com justificativa, preço mínimo e ofertas por loja
```

### 3.3 Decisão

O agente não toma uma decisão única centralizada. O pipeline é sequencial e cada etapa tem responsabilidade clara:

- A **seleção de candidatos** é feita por similaridade de embedding no ChromaDB: os vetores dos livros lidos são usados para construir uma consulta que recupera os livros mais próximos no espaço semântico.
- A **justificativa** é gerada pela Gemini API em uma única chamada para todos os candidatos. O prompt informa os livros lidos (título, autores, gêneros) e a lista de candidatos, solicitando 1 a 2 frases em português por livro. Não há ranqueamento por LLM: a ordenação vem da distância de embedding.
- A **verificação de preços** é feita por ferramentas externas (tools) chamadas de forma independente por loja, com falha silenciosa por fonte.

### 3.4 Saída (Output)

Lista de recomendações exibida na interface Streamlit, onde cada item contém:

- Título do livro
- Justificativa em português (1 a 2 frases)
- Menor preço encontrado e respectiva loja
- Lista completa de ofertas com link por loja
- Botão para adicionar à lista de desejos

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.13 | Linguagem principal |
| Streamlit | 1.41+ | Interface web |
| Gemini API (gemini-3.1-flash-lite-preview) | Google AI | Geração de justificativas em pt-BR |
| ChromaDB | 1.5+ | Catálogo vetorial (RAG) |
| sentence-transformers | 3.3+ | Embeddings multilíngues (paraphrase-multilingual-MiniLM-L12-v2) |
| Open Library API | pública | Metadados de livros (Search, Works, Subjects) |
| Mercado Livre API | pública | Preços de livros (API oficial) |

### 4.2 Estrutura do código

```
projeto-1/
├── src/
│   ├── app.py              # Interface Streamlit
│   ├── agent.py            # Orquestrador do pipeline
│   ├── book_fetcher.py     # Open Library Search + Works API
│   ├── catalog_builder.py  # Build do catálogo RAG via Subjects API
│   ├── rag.py              # Wrapper ChromaDB + embeddings
│   ├── price_checker.py    # Verificação de preços nas livrarias
│   └── wishlist.py         # Lista de desejos local (JSON)
├── data/
│   ├── chroma_db/          # Catálogo vetorial persistido
│   └── wishlist.json       # Lista de desejos do usuário
├── documento-engenharia.md
├── relatorio-entrega.md
├── .env.example
├── requirements.txt
└── README.md
```

### 4.3 Como executar

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar a chave da Gemini API no arquivo .env
# GEMINI_API_KEY=sua_chave_aqui

# 4. Construir o catálogo RAG (executar uma vez)
python src/catalog_builder.py

# Para um build reduzido durante testes:
python src/catalog_builder.py --limit 20

# 5. Executar a aplicação
streamlit run src/app.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Relevância das recomendações | Proporção de recomendações compatíveis com o gênero e histórico de leitura do perfil (avaliação manual: 0 = irrelevante, 1 = relevante) | 3,4 / 5 (média dos 5 perfis: 2, 3, 4, 5, 3) |
| Qualidade da justificativa | Avaliação manual de coerência (escala 1 a 5): 1 = genérica ou incorreta; 3 = conecta ao gênero mas sem referência aos livros lidos; 5 = menciona livros lidos, conecta tematicamente ao candidato e está inteiramente em pt-BR | 4 / 5 — média dos 5 perfis; justificativas referenciam títulos do histórico e estão em português sem trocas de idioma; pontuação reduzida por justificativas ocasionalmente genéricas em perfis com metadados escassos |
| Cobertura de preços | Percentual de recomendações com ao menos um preço encontrado | 100% |
| Latência | Tempo total de resposta do pipeline por requisição | ~57 s (média dos 5 perfis) |

### 5.2 Exemplos de teste

#### Teste 1 — Perfil: Ficção Científica

- **Entrada:** Duna (Frank Herbert), Fundação (Isaac Asimov), Neuromancer (William Gibson), Fahrenheit 451 (Ray Bradbury)
- **Saída esperada:** Recomendações de ficção científica com temas de distopia, tecnologia ou civilizações futuras; justificativas referenciando os temas de expansão galáctica, inteligência artificial ou controle social; ao menos um preço encontrado por recomendação
- **Saída obtida:** Dune (Frank Herbert), The Islander, On the Beach (Nevil Shute), Foundation (Isaac Asimov), Breakdown — todas com preço encontrado
- **Resultado:** Parcial — 2/5 relevantes; Dune (= Duna) e Foundation (= Fundação) são os livros já lidos retornados em inglês, não filtrados por diferença de idioma no título; On the Beach é um clássico de ficção científica pós-apocalíptica compatível com o perfil; Breakdown é distopia compatível; The Islander não possui aderência clara ao gênero; justificativas coerentes

#### Teste 2 — Perfil: Literatura Brasileira

- **Entrada:** Dom Casmurro (Machado de Assis), A Hora da Estrela (Clarice Lispector), Vidas Secas (Graciliano Ramos)
- **Saída esperada:** Recomendações de literatura brasileira ou latino-americana; justificativas que reconheçam o realismo, a crítica social ou o estilo introspectivo dos livros lidos; preços verificados nas livrarias
- **Saída obtida:** A paixão segundo G.H. (Clarice Lispector), Sobre héroes y tumbas (Ernesto Sábato), Brida (Paulo Coelho), Memórias póstumas de Brás Cubas (Machado de Assis), Maria (Jorge Isaacs) — todas com preço encontrado
- **Resultado:** Parcial — 3/5 relevantes; A paixão segundo G.H., Brida e Memórias póstumas são obras brasileiras com boa aderência; Sobre héroes y tumbas e Maria são obras latino-americanas em espanhol, fora do escopo esperado; justificativas adequadas

#### Teste 3 — Perfil: Mistério e Thriller

- **Entrada:** O Nome da Rosa (Umberto Eco), O Silêncio dos Inocentes (Thomas Harris), Garota Exemplar (Gillian Flynn), O Código Da Vinci (Dan Brown)
- **Saída esperada:** Recomendações de mistério, thriller ou suspense; justificativas que conectem com investigação, narrativa de tensão ou revelação gradual; ao menos dois preços encontrados entre as recomendações
- **Saída obtida:** Saving Faith (David Baldacci), Dead Man's Ransom (Ellis Peters), The Sicilian (Mario Puzo), The Middle Temple Murder (J.S. Fletcher), Journal d'un curé de campagne (Bernanos) — todas com preço encontrado
- **Resultado:** Bom — 4/5 relevantes; Saving Faith, Dead Man's Ransom, The Sicilian e The Middle Temple Murder são adequados ao perfil de mistério e thriller; Journal d'un curé de campagne é literatura francesa sem relação com o gênero; justificativas bem contextualizadas, referenciando livros lidos específicos

#### Teste 4 — Perfil: Filosofia

- **Entrada:** O Mundo de Sofia (Jostein Gaarder), A República (Platão), Assim Falou Zaratustra (Nietzsche)
- **Saída esperada:** Recomendações de filosofia, ensaio ou não-ficção reflexiva; justificativas que referenciem pensamento crítico, ética ou questões existenciais; ao menos um preço encontrado
- **Saída obtida:** De republica (Cícero), Prince (Maquiavel), Common Sense (Thomas Paine), Two Treatises on Government (John Locke), Selections (Aristóteles, coletânea de textos filosóficos) — todas com preço encontrado
- **Resultado:** Excelente — 5/5 recomendações são obras filosóficas ou de filosofia política com forte aderência ao perfil; cobertura de preços 100%; justificativas precisas e bem fundamentadas

#### Teste 5 — Perfil: Fantasia

- **Entrada:** O Senhor dos Anéis (Tolkien), Harry Potter e a Pedra Filosofal (Rowling), O Nome do Vento (Patrick Rothfuss), As Crônicas de Nárnia (C.S. Lewis)
- **Saída esperada:** Recomendações de fantasia épica ou fantasia jovem-adulto; justificativas que conectem com mundos imaginários, magia ou jornada do herói; ao menos um preço encontrado por recomendação
- **Saída obtida:** The Magician's Nephew (C.S. Lewis), Catching Fire (Suzanne Collins), The Vampire Lestat (Anne Rice), The Vampyre (John Polidori), Coraline (Neil Gaiman) — todas com preço encontrado
- **Resultado:** Parcial — 3/5 relevantes; Coraline (Neil Gaiman), The Vampire Lestat (Anne Rice) e The Vampyre (Polidori) são obras de fantasia ou fantasia sombria com aderência ao perfil; The Magician's Nephew pertence à série As Crônicas de Nárnia já lida pelo usuário; Catching Fire é distopia, não fantasia épica; justificativas adequadas

### 5.3 Análise dos resultados

Os testes revelaram desempenho heterogêneo entre perfis. O perfil de Filosofia obteve resultado perfeito (5/5), com recomendações coerentes de filosofia política clássica. Mistério e Thriller (4/5) e Literatura Brasileira (3/5) apresentaram resultados parciais mas satisfatórios. O perfil de Ficção Científica (2/5) foi o mais prejudicado, devido à limitação de exclusão de livros já lidos entre idiomas: Duna e Fundação foram recomendados como Dune e Foundation respectivamente, pois a normalização de títulos implementada opera por correspondência textual e não detecta equivalências entre traduções.

Do ponto de vista operacional, a cobertura de preços de 100% indica que ao menos uma loja retornou resultado para cada recomendação; cabe notar que o scraping da Amazon BR é instável e os valores obtidos por essa fonte podem ser imprecisos. A latência média de ~57 s está dentro do RNF02 (60 s); a maior parte desse tempo é consumida pela consulta de preços nas livrarias (chamadas HTTP sequenciais por candidato) e pela busca de metadados via Open Library, não pela chamada à Gemini API, que representa uma fração pequena do tempo total.

Durante o desenvolvimento, o modelo local qwen2.5:7b (via Ollama) gerava justificativas ocasionalmente em chinês ao processar títulos em inglês, tornando os resultados inutilizáveis. A substituição pela Gemini API (gemini-3.1-flash-lite-preview) resolveu o problema de idioma e reduziu a latência em aproximadamente 70% em relação ao modelo local.

A principal limitação de qualidade identificada é a cobertura desigual do catálogo RAG: a Open Library indexa de forma inconsistente os assuntos por idioma e região, o que faz com que obras não relacionadas ao gênero consultado apareçam como candidatos em alguns perfis.

---

## 6. Diferenciais implementados

- [x] RAG com base externa (ChromaDB + Open Library Subjects API)
- [ ] Múltiplos agentes
- [x] Uso de ferramentas (tools) (price_checker com 3 fontes, book_fetcher com 2 endpoints)
- [x] Memória persistente (catálogo ChromaDB em disco + wishlist.json)
- [x] Explicabilidade (justificativa em linguagem natural para cada recomendação)
- [x] Análise crítica de limitações (seção 7)

---

## 7. Limitações e Trabalhos Futuros

**Limitações identificadas:**

- O scraping de preços da Amazon BR é instável devido a medidas anti-bot. O preço pode não ser retornado
- O catálogo RAG depende de uma etapa de build manual. Se o catálogo estiver desatualizado, livros recentes não aparecem nas recomendações.
- A qualidade dos metadados da Open Library é inconsistente: muitos livros não possuem descrição (`first_sentence` ou `description` ausentes), o que empobrece o embedding e pode prejudicar a similaridade.
- A Gemini API ocasionalmente gera justificativas genéricas quando os metadados do candidato são escassos (ausência de descrição ou subjects no catálogo).
- Não há personalização persistente: o histórico de leitura do usuário não é armazenado entre sessões.

**Trabalhos futuros:**

- Substituir o scraping da Amazon por uma fonte com API oficial (ex: Google Books API para preços, ou parceria com livraria nacional).
- Implementar atualização incremental do catálogo sem reconstrução completa.
- Armazenar o histórico de leitura do usuário entre sessões para recomendações progressivamente mais precisas.
- Adicionar filtros na interface (idioma, gênero, faixa de preço).
- Avaliar modelos alternativos para justificativas (ex: Gemini 1.5 Pro, Claude Haiku).

---

## 8. Referências

1. Open Library API Documentation — https://openlibrary.org/developers/api
2. Mercado Livre API — Busca de itens: https://developers.mercadolivre.com.br/pt_br/itens-e-buscas
3. ChromaDB Documentation — https://docs.trychroma.com
4. Sentence Transformers — `paraphrase-multilingual-MiniLM-L12-v2`: https://www.sbert.net
5. Google Gemini API — https://ai.google.dev/gemini-api/docs

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto
