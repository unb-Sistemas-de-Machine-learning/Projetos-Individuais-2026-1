# Mission Brief — Agente de Curadoria Automatizada de Artigos Científicos

**Versão:** 1.0  
**Data:** 2026-05-03  
**Autora:** Ana Luiza  
**Status:** Draft

---

## 1. Objetivo do Agente

O agente tem como objetivo tranformar a necessidade e objetivo do usuário em uma query de pesquisa para a API Semantic Schoolar API que, irá retornar artigos recentes e, posteriormente, o agente de IA irá fazer uma triagem classificando os artigos, usando o como base o abstract e as key-words, dentre as categorias de  alta relevância, média-relevância, baixa-relevância e neutro, onde o neutro foi quando o agente não conseguiu classificar o artigo, sendo necessário uma posterior revisão humana.

**Frase-missão:** *"Dado um objetivo de pesquisa, crie uma string de busca para a Semantic Schoolar API, encontre o que é relevante, extraia o que importa e decida o que merece atenção — sem ler o que não precisa ser lido."*

---

## 2. Problema que o Agente Resolve

Pesquisadores e estudantes perdem tempo significativo na etapa de triagem inicial de literatura: abrir artigo por artigo, ler títulos e abstracts, decidir manualmente o que é relevante. Esse processo é repetitivo, suscetível a viés de atenção e não escala quando o volume de resultados é grande. O agente elimina essa etapa manual ao automatizar a busca, 
a interpretação da intenção de pesquisa e a classificação inicial — entregando ao pesquisador apenas o que já passou por um primeiro filtro fundamentado.

---

## 3. Usuários-Alvo

| Perfil | Descrição |
|---|---|
| **Pesquisador acadêmico** | Utiliza o agente para triagem de literatura em revisões sistemáticas ou mapeamentos |
| **Estudante de pós-** | Usa para explorar o estado da arte de um tema rapidamente |
| **Grupo de pesquisa** | Alimenta uma base compartilhada de artigos curados por múltiplos membros |
| **Estudantes de Graduação** | Procura, muitas vezes sem experiência, artigos para servirem de base teórica para a produção de outros artigos ou trabalhos de conclusão de curso |

**Necessidade central:** receber uma recomendação estruturada (com justificativa e confiança) sem precisar ler cada artigo individualmente no primeiro momento.

---

## 4. Contexto de Uso

O agente é acionado quando um pesquisador tem uma **intenção de busca em linguagem natural** mas ainda não sabe exatamente quais termos técnicos usar na API. Ele opera de forma assíncrona: o usuário submete o objetivo, o agente processa e entrega os resultados classificados em uma planilha e, quando relevante, notifica via Telegram.

O agente **não substitui** a leitura crítica dos artigos — ele reduz o 
esforço da triagem inicial para que o pesquisador foque onde importa.

---

## 5. Entradas e Saídas Esperadas

### Entrada
| Campo | Tipo | Exemplo |
|---|---|---|
| `objetivo_pesquisa` | Texto livre (linguagem natural) | "quero entender como LLMs são usados para geração automática de código" |

### Saídas
| Campo | Tipo | Descrição |
|---|---|---|
| `query_gerada` | string | Query otimizada enviada à Semantic Scholar |
| `titulo` | string | Título do artigo encontrado |
| `ano` | número | Ano de publicação |
| `citacoes` | número | Número de citações na Semantic Scholar |
| `classificacao` | enum | `alta_relevancia`, `media_relevancia`, `baixa_relevancia`, `neutro` |
| `relevancia_score` | float (0–1) | Score numérico de relevância ao objetivo |
| `keywords_extraidas` | lista | Mínimo 3 keywords identificadas no abstract |
| `resumo` | string | Resumo do artigo em até 50 palavras |
| `justificativa` | string | 1 frase explicando a classificação atribuída |
| `confianca` | float (0–1) | Confiança do agente na classificação |
| `acao` | enum | `arquivar`, `revisar`, `descartar` |
| `status` | string | `processado`, `revisao_humana` |

---

## 6. Limites do Agente

- Processa no máximo **10 artigos por execução** (limite da busca na API)
- Classifica com base **apenas em título e abstract** — não acessa o PDF
- Depende da disponibilidade da **Semantic Scholar API** (externa, sem SLA garantido)
- Não realiza buscas em **múltiplas fontes simultâneas**
- Não suporta entrada em **outros idiomas** além do português e inglês
- Não possui **memória entre execuções** — cada busca é independente

---

## 7. O que o Agente NÃO Deve Fazer

- Não acessa PDFs nem o conteúdo completo dos artigos
- Não acessa bases pagas (Scopus, Web of Science, IEEE Xplore, PubMed)
- Não toma decisão final de leitura, citação ou rejeição — apenas recomenda
- Não executa busca sem um objetivo de pesquisa explicitamente fornecido
- Não armazena dados pessoais dos pesquisadores
- Não envia notificação para artigos classificados como `baixa_relevancia` ou `descartar`
- Não re-executa automaticamente em caso de falha — aguarda nova submissão

---

## 8. Critérios de Aceitação

| # | Critério | Como verificar |
|---|---|---|
| CA-01 | O agente gera uma query coerente com o objetivo informado | Comparar objetivo vs query no log do nó OpenAI |
| CA-02 | A Semantic Scholar retorna ao menos 3 artigos por busca | Verificar output do nó HTTP Request |
| CA-03 | Cada artigo recebe classificação, score, keywords e justificativa | Verificar JSON retornado pelo nó de classificação |
| CA-04 | Artigos `neutro` ou confiança < 0.6 geram linha com status `revisao_humana` no Sheets | Verificar planilha após execução com artigo ambíguo |
| CA-05 | Artigos `alta_relevancia` geram notificação no Telegram | Verificar mensagem recebida no bot |
| CA-06 | Todos os artigos processados são registrados no Google Sheets | Conferir planilha após execução completa |
| CA-07 | Falha na API Semantic Scholar não derruba o fluxo — aciona mensagem de erro no Sheets | Testar com query inválida |

---

## 9. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Semantic Scholar API fora do ar | Baixa | Alto | Nó de erro no n8n registra falha no Sheets com status `api_indisponivel` |
| IA retorna JSON malformado | Média | Alto | Nó Code com try/catch — fallback para `revisao_humana` |
| Query gerada pelo agente é genérica demais | Média | Médio | Prompt do Agente 1 instrui a usar termos técnicos em inglês |
| Artigos retornados são irrelevantes ao tema | Média | Médio | Score de confiança baixo aciona revisão humana automaticamente |
| Limite de tokens da API OpenAI | Baixa | Baixo | Abstracts truncados a 500 caracteres antes de enviar |

---

## 10. Evidências para Considerar a Missão Concluída

- [ ] Print do fluxo completo no n8n com todos os nós conectados
- [ ] Print de execução real mostrando query gerada pelo Agente 1
- [ ] Print do retorno da Semantic Scholar com artigos encontrados
- [ ] Print do JSON de classificação gerado pelo Agente 2
- [ ] Print da planilha Google Sheets com ao menos 5 artigos registrados
- [ ] Print da notificação Telegram recebida para artigo de alta relevância
- [ ] Print de execução com artigo `neutro` mostrando fallback para `revisao_humana`
- [ ] Arquivo `workflow-solution-b.json` exportado do n8n no repositório