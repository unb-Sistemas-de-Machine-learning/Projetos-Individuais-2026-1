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


## Como submeter

**Data limite de entrega: a definir**

1. Dentro da sua pasta pessoal (ex: `maria-silva/`), crie a subpasta `projeto-3/`
2. Coloque todos os entregáveis dentro dessa subpasta
3. Abra um **Pull Request** para submissão
