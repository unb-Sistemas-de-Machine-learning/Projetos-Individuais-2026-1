# Projeto Individual 3: Automação Inteligente de Processos com n8n e Agentes de IA

## Objetivo

Projetar e implementar um fluxo automatizado utilizando a ferramenta **n8n**, integrando **agentes de IA** para tomada de decisão, classificação e geração de conteúdo.

O foco está em:

- **Modelagem do processo**
- **Orquestração de serviços**
- **Uso de IA como componente do fluxo (não como fim em si)**


## Cenário proposto (pode ser adaptado)

### Triagem automática de demandas (ex: atendimento ou suporte)

Você deverá construir um sistema que:

1. Recebe uma entrada (ex: formulário, email ou webhook)
2. Usa um agente de IA para:
   - Classificar a demanda
   - Extrair informações relevantes
3. Decide automaticamente o fluxo a seguir
4. Executa ações (ex: notificar, armazenar, responder, escalar)


## Exemplo de fluxo esperado

```
Entrada → IA classifica → decisão → ação
```

Mais concretamente:

- Recebe mensagem (ex: "Meu acesso não funciona")
- IA classifica como: **suporte técnico**
- Extrai: tipo de problema, urgência
- n8n direciona:
  - Baixa urgência → base de conhecimento
  - Alta urgência → notificação (ex: Slack/email)


## Requisitos obrigatórios

### 1. Uso do n8n como orquestrador

- Workflow visual implementado
- Uso de múltiplos nós (inputs, lógica, integrações)

### 2. Uso de agente de IA

O agente deve ser responsável por alguma decisão não trivial, como:

- Classificação de texto
- Extração estruturada (ex: JSON)
- Sumarização
- Roteamento inteligente

> **Não é suficiente apenas chamar IA — ela deve influenciar o fluxo.**

### 3. Lógica de decisão

- Uso de condicionais (IF, Switch, etc.)
- Diferentes caminhos no fluxo
- Comportamento adaptativo baseado na IA

### 4. Integração com serviços

Pelo menos uma integração real:

- Email
- Google Sheets
- Slack / Telegram
- Banco de dados
- API externa

### 5. Persistência / rastreabilidade

- Armazenar entradas e decisões
- Permitir auditoria do fluxo

### 6. Tratamento de erros e limites

- Lidar com falhas da IA
- Tratar entradas inválidas
- Fallback quando a IA não tiver confiança


## Extensões (diferencial)

- Memória de contexto (ex: histórico do usuário)
- Multi-step reasoning (cadeia de decisões)
- Integração com base de conhecimento
- Uso de embeddings / busca semântica


## Entregas

- Workflow exportado do n8n (`.json`)
- Código/scripts auxiliares (se houver)
- Demonstração do fluxo funcionando (vídeo ou prints)
- Relatório técnico

> Utilize o template disponível em [`templates/relatorio-entrega.md`](templates/relatorio-entrega.md)


## Relatório técnico

Deve explicar:

- Problema escolhido
- Desenho do fluxo
- Papel do agente de IA
- Decisões de arquitetura
- Limitações do sistema
- Riscos (ex: erro de classificação)


## Critério central

> A avaliação prioriza **qualidade da automação e uso inteligente da IA dentro do fluxo**, não complexidade técnica isolada.


## Critérios de Avaliação

| Critério | Peso |
|----------|------|
| Fluxo no n8n (estrutura, clareza, modularidade) | 30% |
| Uso do agente de IA (decisão, não apenas resposta) | 25% |
| Lógica de decisão e caminhos condicionais | 15% |
| Integração com serviços externos | 10% |
| Tratamento de erros e limites | 10% |
| Relatório técnico e documentação | 10% |


## Sugestões de outros cenários (para variar)

- Automação de triagem de artigos científicos
- Classificação de propostas (ex: editais, projetos)
- Assistente de email inteligente
- Organização automática de tarefas
- Chatbot com roteamento interno


## Resumo do que se espera

Um bom trabalho deve demonstrar:

- Fluxo claro e bem estruturado no n8n
- IA sendo usada para **decidir, não só responder**
- Integração entre ferramentas
- Tratamento de erros e limitações




# Como implementar

O diferencial deste projeto está no **processo de construção**: o estudante deve seguir um framework de Engenharia de Software Agêntica, produzindo artefatos auditáveis em cada etapa — Mission Brief, Mentorship Pack, Workflow Runbook, Merge-Readiness Pack, além do padrão de "3 soluções descartáveis" e documentação de evidências.


## Exemplos de contexto

O estudante pode escolher livremente o domínio, desde que aprovado pela professora. Alguns exemplos:

- Agente para triagem de demandas públicas
- Apoio à análise de dados governamentais
- Assistente de revisão de requisitos
- Agente para suporte educacional
- Agente para análise de documentos jurídicos
- Agente para observabilidade de sistemas
- Agente para curadoria de dados
- Agente para apoio à pesquisa científica


## Estrutura obrigatória do repositório

```
projeto-4/
├── agent.md
├── docs/
│   ├── mission-brief.md
│   ├── mentorship-pack.md
│   ├── workflow-runbook.md
│   ├── merge-readiness-pack.md
│   ├── adr/
│   │   └── 001-escolha-da-solucao.md
│   └── evidence/
│       └── (prints, logs, métricas)
├── solutions/
│   ├── solution-a/
│   ├── solution-b/
│   └── solution-c/
├── src/
├── tests/
└── README.md
```

> Utilize os templates disponíveis em [`templates/`](templates/) para cada artefato.


## Entregas obrigatórias

### 1. Mission Brief

O `mission-brief.md` define o contrato entre humano e agente. Deve conter:

- Objetivo do agente
- Problema que ele resolve
- Usuários-alvo
- Contexto de uso
- Entradas e saídas esperadas
- Limites do agente
- O que o agente **não** deve fazer
- Critérios de aceitação
- Riscos
- Evidências necessárias para considerar a missão concluída

### 2. Agent.md

O `agent.md` especifica como o agente deve se comportar. Deve incluir:

- Papel do agente
- Tom de resposta
- Ferramentas que pode usar
- Restrições
- Formato de saída
- Critérios de parada
- Política de erro
- Como registrar decisões
- Como lidar com incerteza
- Quando pedir intervenção humana

### 3. Mentorship Pack

O `mentorship-pack.md` ensina o agente a trabalhar no estilo esperado pelo projeto. Deve conter orientações de julgamento, arquitetura, padrões de código, estilo de documentação, qualidade esperada e exemplos de boas e más respostas.

Exemplo de conteúdo:

```
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas.
O agente deve registrar alternativas descartadas.
```

### 4. Workflow Runbook

O `workflow-runbook.md` descreve o processo obrigatório de execução:

```
1. Ler o mission brief.
2. Propor três soluções possíveis.
3. Registrar cada solução em uma pasta separada.
4. Implementar protótipos mínimos.
5. Executar testes.
6. Comparar as soluções.
7. Escolher uma solução final.
8. Registrar a decisão em ADR.
9. Gerar o Merge-Readiness Pack.
10. Fazer commits separados por etapa.
```

### 5. Três soluções possíveis

Cada estudante deve obrigatoriamente implementar ou prototipar **três abordagens diferentes** para o mesmo problema:

| Solução | Abordagem |
|---------|-----------|
| **solution-a** | Abordagem simples baseada em prompt |
| **solution-b** | Abordagem com RAG, ferramenta externa ou base de conhecimento |
| **solution-c** | Abordagem com fluxo multi-etapas, validação ou agente com ferramentas |

As três soluções não precisam ter o mesmo nível de maturidade, mas todas devem ser **executáveis ou demonstráveis**. O estudante deve comparar: custo, complexidade, qualidade da resposta, riscos, manutenibilidade e adequação ao problema.

### 6. Commits obrigatórios com apoio do Copilot

O estudante deve usar o Copilot para apoiar a construção e registrar commits por etapa. Cada commit deve conter **mensagem clara e racionalidade**.

Sequência mínima esperada:

| # | Commit |
|---|--------|
| 1 | Cria mission brief inicial |
| 2 | Adiciona agent.md com regras de comportamento |
| 3 | Cria mentorship pack e workflow runbook |
| 4 | Implementa solution-a |
| 5 | Implementa solution-b |
| 6 | Implementa solution-c |
| 7 | Adiciona testes e evidências |
| 8 | Registra ADR com comparação das soluções |
| 9 | Adiciona merge-readiness pack |
| 10 | Consolida solução final |

> Cada commit deve incluir, no corpo da mensagem ou em arquivo de log, a **racionalidade da decisão** tomada pelo agente/Copilot.

### 7. Merge-Readiness Pack

O `merge-readiness-pack.md` reúne as evidências de que a solução está pronta para revisão:

- Resumo da solução escolhida
- Comparação entre as três alternativas
- Testes executados
- Evidências de funcionamento
- Limitações conhecidas
- Riscos
- Decisões arquiteturais
- Instruções de execução
- Checklist de revisão
- Justificativa para merge


## Critérios de Avaliação

| Critério | Peso |
|----------|-----:|
| Clareza do Mission Brief | 15% |
| Qualidade do `agent.md` | 15% |
| Qualidade do Mentorship Pack e Workflow Runbook | 20% |
| Implementação das três soluções | 20% |
| Testes, evidências e rastreabilidade | 15% |
| Qualidade dos commits e racionalidade registrada | 10% |
| Merge-Readiness Pack | 5% |


## Resultado esperado

Ao final, o estudante deverá demonstrar não apenas um agente funcionando, mas um **processo auditável de construção de software com IA**. A entrega deve evidenciar:

- **Intenção humana** — decisões deliberadas e justificadas
- **Execução orientada por artefatos** — cada etapa guiada por documentos
- **Comparação entre alternativas** — três soluções avaliadas
- **Rastreabilidade das decisões** — ADRs e commits documentados
- **Critérios claros de confiança** — evidências e testes


## Como submeter

**Data limite de entrega: 05.05**

1. Dentro da sua pasta pessoal (ex: `maria-silva/`), crie a subpasta `projeto-4/`
2. Siga a estrutura obrigatória descrita acima
3. Coloque todos os entregáveis dentro dessa subpasta
4. Abra um **Pull Request** para submissão

