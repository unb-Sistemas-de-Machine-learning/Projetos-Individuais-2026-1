# Mentorship Pack — Agente de Curadoria Automatizada de Artigos Científicos

**Versão:** 1.0  
**Data:** 2026-05-03  
**Autora:** Ana Luiza  
**Referência:** `agent.md`, `docs/mission-brief.md`

> Este documento orienta o desenvolvimento, calibração e avaliação do agente. Destina-se ao engenheiro responsável por construir e manter o pipeline — não ao usuário final.

---

## 1. Princípios de Julgamento do Agente

Estes princípios guiam **toda** decisão de design, prompt e lógica do pipeline. Quando houver dúvida entre duas abordagens, aplique os princípios abaixo como critério de desempate.

### 1.1 Prefira o Simples e Testável

> *"Se duas abordagens produzem o mesmo resultado, escolha a que pode ser verificada mais facilmente."*

- Um prompt com saída JSON fixo é **melhor** que uma cadeia de raciocínio livre difícil de parsear
- Um pipeline linear com nós explícitos no n8n é **melhor** que lógica oculta em um único bloco de código
- Uma regra de threshold fixo (`confianca < 0.6 → revisao_humana`) é **melhor** que uma lógica condicional complexa que varia por contexto
- Testes devem poder ser rodados com **dados fixos e determinísticos** — use `temperatura = 0.2` no LLM para reduzir variabilidade

**Aplicação prática:** antes de adicionar complexidade, pergunte: *"consigo testar isso isoladamente com um input fixo?"* Se não, simplifique.

### 1.2 Documente Alternativas Descartadas

Toda decisão de design relevante deve registrar **o que foi considerado e por que foi descartado**. Isso vai nos ADRs (`docs/adr/`).

Exemplos de alternativas que devem ser documentadas:

| Decisão | Alternativa descartada | Motivo do descarte |
|---|---|---|
| Usar Google Gemini (gemini-2.0-flash) | Gemini Pro (versão maior) | Custo por token mais alto sem ganho mensurável de qualidade para abstracts curtos |
| Registro em Google Sheets | Banco de dados PostgreSQL | Overhead de infraestrutura desnecessário para volume < 100 registros/dia |
| Limite de 10 artigos por busca | Busca paginada com múltiplas chamadas | Aumentaria latência e risco de rate limit sem benefício validado |
| Pipeline no n8n | Script Python autônomo | n8n permite rastreabilidade visual de cada etapa e facilita depuração sem código |

**Regra:** se você considerou algo e descartou, abra um ADR. Uma linha basta. O silêncio é mais custoso que o registro.

### 1.3 Nunca Esconda Incertezas

O agente deve **expressar sua incerteza explicitamente**, não suprimi-la para parecer mais confiante.

- Se o abstract é ambíguo → `confianca` deve refletir isso (valor baixo), não ser inflado
- Se a query retornar artigos claramente off-topic → `categoria = neutro`, não forçar uma categoria
- Se o JSON retornado pelo LLM for inválido → usar o fallback documentado, não tentar "adivinhar" o que o modelo quis dizer
- Se um campo não puder ser determinado → retornar `null`, nunca preencher com placeholder inventado

**Regra:** um `revisao_humana` honesto é **mais valioso** que uma classificação errada com `confianca = 0.9`.

### 1.4 Registre Decisões com Justificativa

Toda linha gerada na planilha deve ter uma `justificativa` legível. O pesquisador precisa entender **por que** o agente classificou daquela forma, mesmo sem ver os logs do n8n.

- Justificativas válidas: *"Artigo trata diretamente de geração de código com LLMs, alinhado ao objetivo."*
- Justificativas inválidas: *"Relevante."* / *"Alta confiança."* / *"Score 0.87."*
- Quando houver fallback por erro: `justificativa = "Falha ao processar resposta do modelo — requer revisão humana."`

---

## 2. Padrão de Prompt

Todo prompt enviado ao LLM **deve seguir este padrão** sem exceção. A instrução de retornar JSON válido é obrigatória e deve ser a última linha do prompt.

### 2.1 Template — Agente 1 (Query Builder)

```
Você é um assistente especializado em pesquisa acadêmica.
Sua tarefa é transformar o objetivo de pesquisa abaixo em uma query de busca
otimizada para a Semantic Scholar API.

A query deve:
- Usar termos técnicos em inglês
- Ser específica o suficiente para retornar artigos relevantes
- Ter entre 3 e 8 palavras-chave
- Não usar operadores booleanos complexos (apenas termos separados por espaço)

Objetivo de pesquisa:
"{objetivo_pesquisa}"

Retorne SOMENTE um JSON válido, sem texto adicional, no formato:
{
  "query": "string com os termos de busca em inglês",
  "justificativa": "1 frase explicando a escolha dos termos"
}
```

### 2.2 Template — Agente 2 (Classifier)

```
Você é um agente de curadoria científica. Avalie o artigo abaixo em relação
ao objetivo de pesquisa fornecido.

Objetivo de pesquisa: "{objetivo_pesquisa}"

Artigo a classificar:
- Título: "{titulo}"
- Abstract: "{abstract_truncado_500_chars}"

Classifique o artigo e retorne SOMENTE um JSON válido, sem texto adicional,
sem blocos de código markdown, sem explicações fora do JSON, no formato:
{
  "categoria": "alta_relevancia | media_relevancia | baixa_relevancia | neutro",
  "relevancia_score": <float entre 0.0 e 1.0>,
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "resumo_50_palavras": "<resumo em português com no máximo 50 palavras>",
  "justificativa": "<1 frase explicando a classificação>",
  "acao_recomendada": "arquivar | revisar | descartar",
  "confianca": <float entre 0.0 e 1.0>
}

Regras obrigatórias:
- keywords: mínimo 3, máximo 7, em inglês
- resumo_50_palavras: máximo 50 palavras, em português
- confianca: reflita sua real certeza — se o abstract for ambíguo, use valor baixo
- Se não conseguir classificar com segurança, use categoria "neutro" e confianca < 0.5
```

### 2.3 Regras de Prompt Inegociáveis

| Regra | Motivo |
|---|---|
| Sempre terminar com `"Retorne SOMENTE um JSON válido, sem texto adicional"` | Evita que o modelo envolva o JSON em markdown ou adicione explicações que quebram o parse |
| Nunca usar `temperatura > 0.3` nos agentes | Reduz variabilidade e torna o comportamento mais previsível e testável |
| Sempre truncar abstracts a 500 caracteres antes de enviar | Controla custo de tokens e evita estouro de contexto |
| Nunca incluir exemplos de JSON no prompt de produção | Exemplos podem ser interpretados como parte da saída esperada e contaminar o output |
| Sempre incluir os campos esperados explicitamente no prompt | O modelo não deve inferir o schema — ele deve seguir o especificado |

---

## 3. Exemplos de Referência

### ✅ Boa Resposta do Agente

**Contexto:** objetivo = *"quero entender como LLMs são usados para geração automática de código"*

**Output do Agente 2 (JSON retornado pelo LLM):**

```json
{
  "categoria": "alta_relevancia",
  "relevancia_score": 0.91,
  "keywords": [
    "large language models",
    "code generation",
    "program synthesis",
    "neural code synthesis",
    "automated programming"
  ],
  "resumo_50_palavras": "Apresenta o CodeGen, modelo de linguagem de grande escala treinado para síntese de programas via diálogo multi-turno. Supera modelos contemporâneos no benchmark HumanEval. Demonstra que o aumento de dados de código melhora significativamente a capacidade de geração automática a partir de descrições em linguagem natural.",
  "justificativa": "Artigo diretamente alinhado ao objetivo: descreve um LLM desenvolvido especificamente para geração automática de código com resultados empíricos mensuráveis.",
  "acao_recomendada": "arquivar",
  "confianca": 0.88
}
```

**Por que esta resposta é boa:**
- JSON puro, sem markdown envolvendo o bloco
- Todos os 7 campos obrigatórios presentes
- `relevancia_score` e `confianca` são distintos e coerentes entre si
- `keywords` em inglês, entre 3 e 7 itens
- `resumo_50_palavras` em português, dentro do limite, não é cópia do abstract
- `justificativa` é uma frase completa e explicativa
- `acao_recomendada` é consistente com `categoria`

---

### ❌ Má Resposta do Agente

**Mesmo contexto:** objetivo = *"quero entender como LLMs são usados para geração automática de código"*

**Output problemático retornado pelo LLM:**

```
Com base na análise do abstract fornecido, este artigo parece bastante relevante
para o tema de geração de código com modelos de linguagem. O título menciona
CodeGen e síntese de programas, o que está alinhado.

Palavras-chave: code generation, LLMs

Classificação: Alta relevância. Recomendo arquivar.
```

**Por que esta resposta é inaceitável:**

| Problema | Impacto |
|---|---|
| Não é JSON — é texto livre | `JSON.parse()` lança exceção; pipeline entra em fallback |
| `confianca` não informado | Campo obrigatório ausente; objeto incompleto |
| `relevancia_score` não informado | Não é possível aplicar as regras de threshold |
| Apenas 2 keywords | Viola o mínimo de 3 exigido pelo output contract |
| `resumo_50_palavras` ausente | Campo obrigatório ausente |
| Linguagem subjetiva ("parece bastante relevante") | O agente deve ser objetivo, não especulativo |

**O que deve acontecer quando isso ocorre:**  
O nó Code do n8n detecta o erro de parse, constrói o objeto de fallback definido na seção 5 do `agent.md`, grava no Sheets com `status = revisao_humana` e `erro = json_parse_error`, e o pipeline continua para o próximo artigo.

---

## 4. Qualidade Esperada — Checklist de Avaliação

Use esta lista para avaliar cada execução do pipeline durante desenvolvimento e testes.

### 4.1 Extração Estruturada

- [ ] O JSON retornado é válido (parseable sem erro)?
- [ ] Todos os 7 campos obrigatórios estão presentes?
- [ ] `keywords` contém entre 3 e 7 itens em inglês?
- [ ] `resumo_50_palavras` está em português e dentro do limite de palavras?
- [ ] `relevancia_score` e `confianca` são floats entre 0.0 e 1.0?
- [ ] `categoria` e `acao_recomendada` são valores do enum definido?
- [ ] `acao_recomendada` é consistente com `categoria`?

### 4.2 Rastreabilidade de Decisão

- [ ] Cada linha no Google Sheets tem uma `justificativa` não vazia?
- [ ] Linhas com `status = revisao_humana` têm a causa identificada (campo `erro` ou `confianca < 0.6`)?
- [ ] A `query_gerada` pelo Agente 1 está registrada na planilha?
- [ ] O `objetivo_pesquisa` original do usuário está preservado na planilha sem alteração?
- [ ] Artigos com `abstract_indisponivel` estão registrados com esse status (não silenciosamente ignorados)?

### 4.3 Comportamento em Borda

- [ ] O pipeline não interrompe quando um artigo gera JSON inválido?
- [ ] O pipeline não interrompe quando a API retorna zero resultados?
- [ ] Artigos com `confianca < 0.6` recebem `status = revisao_humana`?
- [ ] Artigos com `categoria = neutro` recebem `status = revisao_humana`?
- [ ] Notificação Telegram é disparada **somente** para `categoria = alta_relevancia`?

---

## 5. Antipadrões a Evitar

| Antipadrão | Por que é problemático | Como corrigir |
|---|---|---|
| Prompt que aceita texto livre | O modelo divaga; output não é parseável | Sempre terminar o prompt com a instrução de JSON puro |
| `confianca = 1.0` frequente | Indica que o modelo não está calibrando incerteza | Verificar se o prompt instrui explicitamente a usar valores baixos em casos ambíguos |
| `justificativa` genérica ("artigo relevante") | Não permite rastreabilidade | Exigir no prompt que a justificativa mencione a relação com o objetivo de pesquisa |
| Ignorar artigos sem abstract | Gera lacunas no registro sem rastro | Sempre gravar no Sheets com `fonte_abstract = abstract_indisponivel` |
| Tratar `revisao_humana` como falha | É o comportamento correto para incerteza alta | Documentar como feature, não como bug; meta: < 20% das linhas |
| Retentar LLM automaticamente em JSON inválido | Pode gerar loop e custo extra sem garantia de melhora | Aplicar fallback imediatamente; não retentar |

---

## 6. Referências Cruzadas

| Documento | Relação com este pack |
|---|---|
| [`agent.md`](../agent.md) | Define o output contract e as políticas de erro que este pack exemplifica |
| [`docs/mission-brief.md`](mission-brief.md) | Define os critérios de aceitação que este pack operacionaliza |
| [`docs/adr/001-escolha-da-solucao.md`](adr/001-escolha-da-solucao.md) | Registra as alternativas descartadas mencionadas na seção 1.2 |
| [`docs/workflow-runbook.md`](workflow-runbook.md) | Descreve o procedimento operacional de execução e monitoramento |
