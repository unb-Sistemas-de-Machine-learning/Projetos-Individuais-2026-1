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

O agente é acionado quando um pesquisador tem uma **intenção de busca em linguagem natural** mas ainda não sabe exatamente quais termos técnicos usar na API. Ele opera de forma assíncrona via n8n: o usuário preenche o campo `objetivo_pesquisa` no nó **Edit Fields**, o **Agente 1** (Google Gemini 2.5 Flash) converte o objetivo em uma query booleana em inglês (formato `("termo1" OR "termo2") +campo`), a **Semantic Scholar Bulk Search API** retorna até 5 artigos, um nó **Filter** elimina artigos sem abstract, e o **Agente 2** (Google Gemini 2.5 Flash) classifica cada artigo retornando um JSON estruturado. Os resultados são gravados na aba **Registros** do Google Sheets; artigos com `acao = revisar` ou `relevancia_score >= 0.8` recebem também um registro na aba **Alertas**.

O agente **não substitui** a leitura crítica dos artigos — ele reduz o esforço da triagem inicial para que o pesquisador foque onde importa.

---

## 5. Entradas e Saídas Esperadas

### Entrada
| Campo | Tipo | Exemplo |
|---|---|---|
| `objetivo_pesquisa` | Texto livre (linguagem natural) | "Como os celulares impactam nas escolas" |

### Saídas — Agente 1 (Query Builder)
| Campo | Tipo | Descrição |
|---|---|---|
| `query_gerada` | string | Query booleana em inglês gerada pelo Agente 1; ex: `("smartphone" OR "mobile phone") +school +learning` |

### Saídas — Agente 2 (Classifier), por artigo
| Campo | Tipo | Descrição |
|---|---|---|
| `titulo` | string | Título do artigo retornado pela Semantic Scholar |
| `ano` | integer \| null | Ano de publicação |
| `relevancia` | float (0–1) | Score numérico de relevância ao objetivo (`relevancia_score`) |
| `resumo_pt` | string | Resumo do artigo em até 30 palavras, em português |
| `decisao` | enum | `arquivar` ou `descartar` |

### Saídas — Google Sheets
| Aba | Conteúdo |
|---|---|
| **Registros** | Todos os artigos processados com todos os campos acima |
| **Alertas** | Artigos com `decisao = revisar` ou `relevancia >= 0.8`; campos: `timestamp`, `titulo`, `relevancia`, `resumo_pt`, `justificativa`, `status = aguardando_revisao` |

---

## 6. Limites do Agente

- Processa no máximo **5 artigos por execução** (parâmetro `limit=5` no nó HTTP Request, imposto pelo rate limit da Semantic Scholar sem chave de API)
- Artigos com **abstract nulo** são eliminados antes da classificação pelo nó Filter — não são registrados no Sheets
- Classifica com base **apenas em título e abstract** — não acessa o PDF
- Depende da disponibilidade da **Semantic Scholar Bulk Search API** (gratuita, sem SLA garantido)
- Abstract nulo aciona classificação com `confianca = 0.3` e `decisao = revisar` quando o filtro não elimina o artigo
- Não realiza buscas em **múltiplas fontes simultâneas**
- Não suporta entrada em **outros idiomas** além do português e inglês
- Não possui **memória entre execuções** — cada busca é independente
- Modelo **Gemini 2.0 Flash foi depreciado** durante o desenvolvimento; implementação migrada para **Gemini 2.5 Flash**

---

## 7. O que o Agente NÃO Deve Fazer

- Não acessa PDFs nem o conteúdo completo dos artigos
- Não acessa bases pagas (Scopus, Web of Science, IEEE Xplore, PubMed)
- Não toma decisão final de leitura, citação ou rejeição — apenas recomenda
- Não executa busca sem um objetivo de pesquisa explicitamente fornecido
- Não armazena dados pessoais dos pesquisadores
- Não envia notificação para artigos classificados como `baixa_relevancia` ou `descartar`
- Não envia notificações externas por mensageiro (Telegram, WhatsApp, email)
- Não re-executa automaticamente em caso de falha — aguarda nova submissão

---

## 8. Critérios de Aceitação

| # | Critério | Como verificar |
|---|---|---|
| CA-01 | O agente gera uma query coerente com o objetivo informado | Comparar objetivo vs query no log do nó Google Gemini |
| CA-02 | A Semantic Scholar retorna ao menos 3 artigos por busca | Verificar output do nó HTTP Request |
| CA-03 | Cada artigo recebe classificação, score, keywords e justificativa | Verificar JSON retornado pelo nó de classificação |
| CA-04 | Artigos `neutro` ou confiança < 0.6 geram linha com status `revisao_humana` no Sheets | Verificar planilha após execução com artigo ambíguo |
| CA-05 | Artigos com `acao = revisar` ou `relevancia_score >= 0.8` geram linha na aba **Alertas** com `status = aguardando_revisao` | Verificar aba Alertas no Google Sheets após execução |
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
| Limite de tokens da API Google Gemini | Baixa | Baixo | Abstracts truncados a 500 caracteres antes de enviar |

---

## 10. Evidências para Considerar a Missão Concluída

- [x] Print do fluxo completo no n8n com todos os nós conectados (Manual Trigger → Edit Fields → Agente 1 → HTTP Request → Split Out → Filter → Limit → Agente 2 → Code → IF → Switch → Google Sheets Registros / Alertas)
- [x] Print de execução real mostrando query booleana gerada pelo Agente 1
- [x] Print do retorno da Semantic Scholar Bulk Search API com artigos encontrados
- [x] Print do JSON de classificação gerado pelo Agente 2 (campos: `titulo`, `ano`, `relevancia`, `resumo_pt`, `decisao`)
- [x] Print da aba **Registros** no Google Sheets com artigos processados
- [x] Print da aba **Alertas** no Google Sheets com ao menos 1 artigo com `status = aguardando_revisao`
- [x] Arquivo `workflow-solution-b.json` exportado do n8n no repositório (`src/workflow-solution-b.json`)