# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Carlos Eduardo Rodrigues
> **Matrícula:** 221031265
> **Domínio:** 4 - Compras públicas
> **Função do agente:** 9 - Detecção de anomalias
> **Restrição obrigatória:** 8 - Integração com API externa (Gemini)

---

## 1. Problema e Contexto

No contexto de compras públicas, muitos avisos, extratos e termos de licitação são publicados com alta variabilidade de formato e qualidade. Essa característica dificulta a triagem manual de riscos por equipes de controle, auditoria e gestão.

O problema tratado neste projeto é a detecção inicial de inconsistências em textos de licitações, com foco em quatro sinais: inexigibilidade suspeita, menções a aditivos, valores elevados e descrições vagas de objeto. O objetivo não é emitir julgamento final, mas gerar alertas para priorização de análise humana.

O público-alvo inclui analistas de controle interno municipal, servidores de comissões de licitação e pessoas interessadas em transparência pública.

Os dados textuais utilizados foram extraídos a partir do projeto Licitaiba (repositório: https://github.com/unb-mds/2023-2-Squad04/), que automatiza a coleta e o acompanhamento de informações de licitações públicas do Diário Oficial da Paraíba.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Analista de controle interno | Usuário principal do agente | Identificar rapidamente textos com maior risco potencial |
| Comissão de licitação | Produtora e consumidora de documentos | Melhorar qualidade descritiva e reduzir inconsistências recorrentes |
| Gestor público | Tomador de decisão | Acompanhar indicadores de risco e priorizar auditorias |
| Cidadão e órgãos de controle social | Interessado indireto | Ampliar transparência e rastreabilidade da análise |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | Ler registros de entrada em JSON contendo o texto extraído dos diários oficiais, a data e o municipio | Alta |
| RF02 | Pré-processar o texto para normalização antes da análise por LLM | Alta |
| RF03 | Consultar a API do Gemini e retornar análise em JSON estruturado | Alta |
| RF04 | Aplicar regras determinísticas (limite legal de dispensa, dados insuficientes e sinais heurísticos) para ajuste de risco/confiança | Alta |
| RF05 | Exibir saída por registro indicando se tem ou não anomalia, nível de risco e justificativa | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | Uso obrigatório de variável de ambiente GEMINI_API_KEY | Segurança |
| RNF02 | Código modular e legível em Python, com separação entre configuração, agente e execução | Manutenibilidade |
| RNF03 | Pipeline determinístico e reproduzível (mesmas etapas para toda entrada) | Confiabilidade |
| RNF04 | Resposta final sempre no mesmo schema JSON | Robustez |
| RNF05 | Baixa complexidade de implantação local via requirements.txt | Portabilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Triagem automatizada de risco documental

- **Ator:** Analista de controle interno
- **Pré-condição:** Arquivo data.json disponível e GEMINI_API_KEY configurada
- **Fluxo principal:**
  1. O analista executa o sistema em linha de comando.
  2. O sistema lê os textos de licitação e processa cada item no pipeline.
  3. O sistema retorna saída estruturada com sinalização de anomalia e confiança.
- **Pós-condição:** Lista de registros classificados para priorização de revisão humana

### Caso de uso 2: Fiscalização de transparência por cidadão e ONG

- **Ator:** Cidadão interessado, ONG de transparência ou órgão de controle social
- **Pré-condição:** GEMINI_API_KEY configurada; arquivo JSON com um único registro (edital ou aviso suspeito)
- **Fluxo principal:**
  1. O cidadão identifica um edital/aviso potencialmente fraude em um Diário Oficial (ex.: valor próximo ao limite legal, objeto vago, indicadores de irregularidade).
  2. O cidadão extrai o texto e o prepara em um arquivo JSON.
  3. O cidadão executa o pipeline.
  4. O sistema retorna análise detalhada: classificação de risco, categoria de anomalia detectada, nível de confiança e justificativa explícita.
  5. O cidadão utiliza a resposta para fundamentar denúncia formal junto a órgãos de controle com evidências estruturadas e explicações técnicas.
- **Pós-condição:** Cidadão obtém parecer estruturado; se anomalia confirmada, dispõe de justificativa técnica baseada em regras legais e análise de IA.

---

## 6. Fluxo do Agente

Fluxo textual do agente:

```text
Entrada (JSON)
  -> Pre-processamento (normalização de texto)
  -> Extração de features (valor, modalidade, limites, sinais de incerteza)
  -> Hard rules (decisão objetiva quando houver violação legal clara)
  -> LLM Gemini (classificação e justificativa, quando necessário)
  -> Regras de composição de risco
  -> Saída estruturada (tem_anomalia, nivel_risco, categoria, tipo, justificativa, confianca)
```

---

## 7. Arquitetura do Sistema

Arquitetura escolhida baseada em pipeline sequencial com uso de API externa.

- **Tipo de agente:** Pipeline sequencial tool-using (chamada externa para LLM)
- **LLM utilizado:** Gemini 2.5 Flash (google-genai)
- **Componentes principais:**
  - [x] Módulo de entrada
  - [x] Processamento / LLM
  - [x] Ferramentas externas (tools)
  - [ ] Memória
  - [x] Módulo de saída

---

## 8. Estratégia de Avaliação

Plano de avaliação do agente:

- **Métricas definidas:**
  - Cobertura de schema: % de respostas com 6 campos obrigatórios (tem_anomalia, nivel_risco, categoria, tipo, justificativa, confianca)
  - Latência média: tempo médio por documento processado
- **Conjunto de testes:** 
  - UC1: amostra de documentos públicos em português presentes em data/data_small.json (3 registros estratificados por risco)
- **Método de avaliação:** validação de presença dos 6 campos no JSON de saída; análise qualitativa de conservadorismo na classificação (não marcar anomalia por proximidade isolada ou falta de dados); verificação de clareza e pertinência das justificativas em português

---

## 9. Referências

1. Google AI for Developers. Gemini API Documentation.
2. unb-mds/2023-2-Squad04. "Licitaiba - Extrator de Licitações do Diário Oficial da Paraíba". Disponível em: https://github.com/unb-mds/2023-2-Squad04/
