# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Alex Gabriel Alves Faustino   
> **Matrícula:** 200056603  
> **Domínio:** Cultura  
> **Função do agente:** Análise de   sentimento  
> **Restrição obrigatória:** Integração com API externa  

---

## 1. Problema e Contexto

A música afeta diretamente o estado emocional dos ouvintes, contudo, as plataformas de streaming e vídeo, como o YouTube, organizam o conteúdo primordialmente por gênero, artista ou algoritmo de popularidade. O problema a ser resolvido é a dificuldade de criar curadorias focadas estritamente no humor e no sentimento transmitido pelas canções. Este projeto implementa um agente que analisa o conteúdo semântico das letras de uma playlist do YouTube e a reorganiza em categorias emocionais, enriquecendo a experiência de escuta.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Usuário Final / Ouvinte | Consumidor | Encontrar rapidamente músicas de uma playlist que correspondam ao seu estado emocional atual. |
| Curador Musical / DJ | Criador | Automatizar a triagem semântica e a estruturação de grandes volumes de faixas para montagem de playlists temáticas. |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O sistema deve receber a URL de uma playlist pública do YouTube e extrair os títulos e canais dos vídeos via API. | Alta |
| RF02 | O sistema deve buscar a letra de cada música extraída utilizando a API externa do Genius. | Alta |
| RF03 | O sistema deve processar as letras com um LLM para inferir e classificar o sentimento predominante da faixa. | Alta |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O agente deve configurar parâmetros para minimizar bloqueios por filtros de segurança do LLM; o comportamento final depende das políticas do provedor. | Confiabilidade |
| RNF02 | O sistema deve higienizar os metadados do YouTube para otimizar as buscas por letras. | Usabilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Categorização Emocional de Playlist

- **Ator:** Usuário Final
- **Pré-condição:** O usuário fornece uma URL válida de uma playlist pública do YouTube contendo vídeos musicais.
- **Fluxo principal:**
  1. O usuário submete a URL da playlist ao agente pelo terminal.
  2. O agente conecta-se à API do YouTube para extrair os metadados brutos e realiza a limpeza de strings.
  3. O agente busca a letra correspondente na API do Genius para cada item iterado.
  4. O agente submete a letra ao modelo de linguagem, que devolve uma categoria de sentimento fechada.
- **Pós-condição:** O terminal exibe a playlist reordenada e agrupada pelas categorias emocionais identificadas.

---

## 6. Fluxo do Agente

```text
Entrada (URL da Playlist) → [Tool 1: YouTube API] → [Limpeza de Metadados] → [Tool 2: Genius API] → [LLM: Análise de Sentimento] → Saída (Relatório Agrupado)
```

## 7. Arquitetura do Sistema

- **Tipo de agente:** Pipeline sequencial com uso de ferramentas (Tool-using)
- **LLM utilizado:** Google Gemini (modelo padrão: `gemini-2.5-flash`)
- **Componentes principais:**
  - [x] Módulo de entrada
  - [x] Processamento / LLM
  - [x] Ferramentas externas (tools)
  - [ ] Memória
  - [x] Módulo de saída

---

## 8. Estratégia de Avaliação

- **Métricas definidas:** Taxa de sucesso na extração das letras (tolerância a metadados sujos) e resiliência a bloqueios de conteúdo explícito pelo LLM.
- **Conjunto de testes:** Playlists contendo gêneros diversos, incluindo Trap e Rap Nacional, para testar ativamente as restrições de segurança do modelo.
- **Método de avaliação:** Avaliação manual da saída gerada no terminal comparada com o conteúdo semântico real das músicas testadas.

---

## 9. Referências

1. Documentação da API do YouTube Data v3.
2. Documentação da API do Genius e biblioteca lyricsgenius.
3. Documentação oficial do Google Generative AI SDK para Python.