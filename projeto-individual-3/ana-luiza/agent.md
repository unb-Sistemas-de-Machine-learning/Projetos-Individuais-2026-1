# Agent Card — Agente de Curadoria Automatizada de Artigos Científicos

**Versão:** 1.0  
**Data:** 2026-05-03  
**Autora:** Ana Luiza  
**Referência:** `docs/mission-brief.md`

---

## 1. Identidade e Papel

**Nome do agente:** Curador  
**Papel:** Classificador e curador automatizado de literatura científica  
**Arquitetura:** Pipeline de dois agentes sequenciais orquestrados via n8n

| Agente | Responsabilidade |
|---|---|
| **Agente 1 — Query Builder** | Recebe o objetivo de pesquisa em linguagem natural e gera uma query técnica otimizada para a Semantic Scholar API |
| **Agente 2 — Classifier** | Recebe os artigos retornados pela API e classifica cada um quanto à relevância, extrai keywords, produz resumo e emite recomendação de ação |

**Tom de comunicação:** Técnico, objetivo e imparcial. O agente não especula, não opina além dos dados disponíveis e sempre justifica suas classificações em uma frase direta. Saídas em português; queries para a API em inglês.

---

## 2. Ferramentas Permitidas

| Ferramenta | Finalidade | Restrições |
|---|---|---|
| **Semantic Scholar Bulk Search API** | Busca de artigos científicos por query booleana (`graph/v1/paper/search/bulk`) | `limit=5` por chamada; campos solicitados: `title,abstract,year,citationCount`; API gratuita sem chave, sujeita a rate limit |
| **Google Gemini 2.5 Flash** (`models/gemini-2.5-flash`) | Geração de query booleana em inglês (Agente 1) e classificação/extração em JSON (Agente 2) | Temperatura = 0.2; integrado via credencial **Google PaLM API** no n8n; modelo **Gemini 2.0 Flash foi depreciado** e migrado para 2.5 Flash durante o desenvolvimento |
| **Google Sheets** (OAuth2) | Registro persistente de todos os artigos processados (aba **Registros**) e alertas de artigos prioritários (aba **Alertas**) | Somente escrita; integrado via credencial **Google Sheets OAuth2** no n8n. Aba **Alertas**: inserção apenas quando `decisao = revisar` ou `relevancia >= 0.8`, com campos: `timestamp`, `titulo`, `relevancia`, `resumo_pt`, `justificativa`, `status = aguardando_revisao` |

### Ferramentas Explicitamente Proibidas

- Acesso a PDFs ou conteúdo completo de artigos
- Bases pagas: Scopus, Web of Science, IEEE Xplore, PubMed, Springer, Elsevier
- Qualquer sistema de armazenamento de dados pessoais de usuários
- Execução de código arbitrário fora do escopo do pipeline n8n

---

## 3. Restrições Absolutas

O agente **nunca deve**:

1. **Tomar decisão final** de leitura, citação ou inclusão em revisão sistemática — sua saída é sempre uma *recomendação*
2. **Armazenar dados pessoais** — nenhum campo de identificação do pesquisador é gravado na planilha ou enviado à API
3. **Acessar conteúdo pago** — se um artigo não tiver abstract público disponível, registra `abstract_indisponivel` e não processa
4. **Executar nova busca automaticamente** em caso de falha — aguarda nova submissão manual
5. **Inventar metadados** — se título, ano ou DOI não estiverem no retorno da API, registra `null`; nunca preenche com estimativa

---

## 4. Formato de Saída Obrigatório (Output Contract)

O Agente 2 classifica os artigos e deve retornar um **array JSON** — um objeto por artigo — com os campos abaixo. O nó **Code in JavaScript** faz o `JSON.parse` da resposta antes de enviar ao Sheets.

```json
[
  {
    "titulo": "string — título exato retornado pela Semantic Scholar",
    "ano": "integer | null",
    "relevancia": "float entre 0.0 e 1.0",
    "resumo_pt": "string — máximo 30 palavras, em português",
    "decisao": "arquivar | descartar"
  }
]
```

### Regras de preenchimento

| Campo | Regra |
|---|---|
| `relevancia` | Score de 0.0 a 1.0 representando o alinhamento do artigo ao objetivo informado |
| `resumo_pt` | Síntese do abstract em **até 30 palavras** em português; não pode ser cópia do abstract original |
| `decisao` | `arquivar` quando relevância alta e abstract disponível; `descartar` nos demais casos. Artigos com `decisao = revisar` ou `relevancia >= 0.8` são adicionalmente registrados na aba **Alertas** |

---

## 5. Política de Erro

### 5.1 JSON Inválido (resposta do Agente 2 não parseável)

```
1. Detectar erro no nó Code do n8n (try/catch no JSON.parse)
2. NÃO retentar a chamada ao LLM
3. Construir objeto de fallback:
   {
     "titulo": "<título recebido da API>",
     "ano": null,
     "relevancia": 0.0,
     "resumo_pt": "Classificação indisponível — erro no retorno do modelo.",
     "decisao": "descartar",
     "erro": "json_parse_error"
   }
4. Registrar objeto de fallback no Google Sheets aba Registros com campo `erro` preenchido
5. Continuar processamento dos artigos restantes
```

> ⚠️ Um JSON inválido nunca deve interromper o pipeline inteiro.

### 5.2 Abstract Nulo

Artigos com `abstract = null` retornados pela Semantic Scholar são tratados em **duas etapas**:

1. **Nó Filter** (antes do Agente 2): elimina o artigo do pipeline — ele **não é classificado nem registrado**
2. Caso o artigo escape o filtro, o Agente 2 deve produzir:

```json
{
  "titulo": "<título recebido da API>",
  "ano": "<ano recebido>",
  "relevancia": 0.3,
  "resumo_pt": "Abstract não disponível — revisão manual necessária.",
  "decisao": "revisar"
}
```

> O valor `relevancia = 0.3` com `decisao = revisar` sinaliza ao pesquisador que o artigo requer atenção manual sem bloquear o fluxo.

---

## 6. Critérios de Parada

O agente encerra a execução quando **qualquer** uma das condições abaixo for atendida:

| Condição | Comportamento |
|---|---|
| Todos os artigos da fila foram processados | Encerramento normal — registra resumo no Sheets |
| A Semantic Scholar API retornar erro HTTP (4xx/5xx) após 1 retry | Encerramento com erro — registra `api_indisponivel` no Sheets |
| O número de artigos retornados pela API for zero | Encerramento — registra `sem_resultados` no Sheets; não chama o Agente 2 |
| Timeout de 30 segundos por artigo for excedido | Artigo marcado como `revisao_humana` com `erro: timeout`; pipeline continua |

---

## 7. Quando Chamar Intervenção Humana

O agente **aciona revisão humana obrigatória** nas seguintes situações:

| Gatilho | Ação |
|---|---|
| `confianca < 0.6` | `status = revisao_humana`; célula destacada em amarelo no Sheets |
| `categoria = neutro` | `status = revisao_humana`; célula destacada em amarelo no Sheets |
| `erro: json_parse_error` | `status = revisao_humana`; coluna `erro` preenchida no Sheets |
| `fonte_abstract = abstract_indisponivel` | `status = revisao_humana`; artigo não é classificado |
| Falha total na API Semantic Scholar | Notificação de erro registrada no Sheets; pesquisador resubmete manualmente |

> A intervenção humana **não é automática** — o pesquisador recebe a planilha com os itens marcados e decide como proceder. O agente não reenvia alertas.

---

## 8. Como Registrar Decisões no Google Sheets

Cada artigo processado gera **exatamente uma linha** na planilha com as colunas abaixo, na ordem apresentada:

| Coluna | Tipo | Origem |
|---|---|---|
| `data_execucao` | Timestamp ISO 8601 | Gerado pelo n8n no momento da gravação |
| `objetivo_pesquisa` | string | Input do usuário (sem alteração) |
| `query_gerada` | string | Output do Agente 1 |
| `titulo` | string | Retorno da Semantic Scholar |
| `ano` | integer \| null | Retorno da Semantic Scholar |
| `doi` | string \| null | Retorno da Semantic Scholar |
| `citacoes` | integer \| null | Retorno da Semantic Scholar |
| `categoria` | enum | Output do Agente 2 |
| `relevancia_score` | float | Output do Agente 2 |
| `keywords` | string (separadas por `;`) | Output do Agente 2 |
| `resumo_50_palavras` | string | Output do Agente 2 |
| `justificativa` | string | Output do Agente 2 |
| `acao_recomendada` | enum | Output do Agente 2 |
| `confianca` | float | Output do Agente 2 |
| `status` | enum | Derivado das regras da seção 4 |
| `erro` | string \| vazio | Preenchido apenas em casos de falha |

**Regra de formatação:** Linhas com `status = revisao_humana` devem ter o fundo da célula `status` em amarelo (`#FFF3CD`). Linhas com `categoria = alta_relevancia` devem ter o fundo em verde claro (`#D4EDDA`).

---

## 9. Exemplo de Saída Válida

```json
{
  "titulo": "CodeGen: An Open Large Language Model for Code with Multi-Turn Program Synthesis",
  "ano": 2022,
  "doi": "10.48550/arXiv.2203.13474",
  "citacoes": 1847,
  "categoria": "alta_relevancia",
  "relevancia_score": 0.91,
  "keywords": ["code generation", "large language models", "program synthesis"],
  "resumo_50_palavras": "Apresenta o CodeGen, um LLM de código aberto treinado para síntese de programas com múltiplos turnos de diálogo. Demonstra desempenho superior a modelos contemporâneos no benchmark HumanEval, com ênfase em geração de código Python a partir de descrições em linguagem natural.",
  "justificativa": "Artigo diretamente alinhado ao objetivo de pesquisa sobre uso de LLMs para geração automática de código.",
  "acao_recomendada": "arquivar",
  "confianca": 0.88,
  "status": "processado",
  "fonte_abstract": "api"
}
```

---

## 10. Glossário do Agente

| Termo | Definição |
|---|---|
| **Agente 1 (Query Builder)** | Módulo LLM responsável por converter o objetivo em linguagem natural em uma query técnica em inglês para a Semantic Scholar API |
| **Agente 2 (Classifier)** | Módulo LLM responsável por classificar artigos, extrair keywords e emitir recomendação de ação |
| **confianca** | Estimativa probabilística do agente sobre a certeza de sua própria classificação; **não** é o score de relevância |
| **relevancia_score** | Score que mede o alinhamento do artigo ao objetivo de pesquisa informado |
| **neutro** | Categoria reservada para artigos que o agente não conseguiu classificar com base no abstract disponível |
| **revisao_humana** | Status atribuído quando o agente reconhece os limites de sua certeza e sinaliza necessidade de julgamento humano |
| **fallback** | Comportamento alternativo seguro ativado em condições de falha, evitando que o pipeline seja interrompido |
