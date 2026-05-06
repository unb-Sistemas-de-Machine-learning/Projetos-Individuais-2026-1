# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Marcos Antonio Teles de Castilhos <br>
> **Matrícula:** 221008300 <br>
> **Data de entrega:** 30/03/2026

### 1. Problema e Contexto
Um dos gargalos das ouvidorias municipais de zeladoria urbana é a triagem manual de relatos informais e desestruturados enviados por cidadãos. O tempo gasto por servidores públicos para ler, interpretar e reencaminhar queixas simples atrasa a alocação de recursos críticos. O agente propõe automatizar essa camada inicial, traduzindo linguagem natural ruidosa em dados categóricos estruturados para despacho imediato.

### 2. Stakeholders
| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Cidadão | Usuário Final | Resolução rápida de problemas urbanos que afetam sua localidade. |
| Operador de Ouvidoria | Triador | Redução da carga cognitiva e do volume de leitura de queixas não padronizadas. |
| Gestor de Zeladoria | Tomador de Decisão | Acesso a métricas estruturadas e categorizadas em tempo real para priorização de equipes. |

### 3. Requisitos Funcionais (RF)
| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O agente deve receber textos desestruturados e informais relatando problemas urbanos. | Alta |
| RF02 | O sistema deve classificar a demanda em categorias estritas (Infraestrutura, Iluminação, Saneamento, Trânsito, Outros). | Alta |
| RF03 | O sistema deve extrair e classificar a urgência do problema (Alta, Média, Baixa) com base em regras predefinidas. | Alta |

### 4. Requisitos Não-Funcionais (RNF)
| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O sistema deve operar a custo zero (Baixo Custo), utilizando APIs em tiers gratuitos devido à ausência de infraestrutura local com aceleração de hardware (GPU). | Restrição de Negócio |
| RNF02 | A saída do modelo deve ser estritamente em formato JSON para garantir a estabilidade do pipeline de dados, sem caracteres de formatação adicionais. | Interoperabilidade |

### 5. Casos de Uso
#### Caso de uso 1: Triagem de Queixa

    Ator: Cidadão / Sistema Automático de Mensageria.

    Pré-condição: O cidadão envia um texto legível sobre um problema da cidade.

    Fluxo principal:

        O texto é capturado e enviado ao agente.

        O agente processa a semântica do texto sob a restrição do System Prompt.

        O agente converte a intenção em um dicionário de dados (Categoria e Urgência).

    Pós-condição: Um objeto JSON validado é salvo no banco de dados da prefeitura para despacho.

### 6. Fluxo do Agente

O sistema evoluiu para uma arquitetura multi-agente para separar a carga cognitiva de avaliação de risco da formatação de dados.

    Entrada (Texto Bruto) → Agente 1: Analista de Risco (Busca perigos ocultos) → Prompt Combinado (Texto + Parecer) → Agente 2: Despachante (Aplica taxonomia e força JSON Schema) → Saída (JSON Estruturado)

### 7. Arquitetura do Sistema

Tipo de agente: Pipeline Multi-Agente sequencial com imposição de Structured Output.

LLM utilizado: Llama 3.1 8b (via API Groq). Nota: O projeto pivotou para o ecossistema Groq após a API original do Google apresentar instabilidade (Erro 503).

Componentes principais:

    [x] Módulo de entrada

    [x] Processamento / LLM (Dois agentes independentes)

    [ ] Ferramentas externas (tools)

    [ ] Memória

    [x] Módulo de saída

### 8. Estratégia de Avaliação

Métricas definidas: Acurácia global (Taxa de acerto conjunto de Categoria e Urgência) e resiliência de formatação (Taxa de sucesso no parsing do JSON).

Conjunto de testes: 51 exemplos simulando linguagem informal, gírias e problemas reais de zeladoria urbana.

Método de avaliação: Avaliação empírica com Ground Truth manual. A saída dos agentes foi exportada rotineiramente para um arquivo CSV e as predições de categoria e urgência foram confrontadas uma a uma com a classificação ideal humana.