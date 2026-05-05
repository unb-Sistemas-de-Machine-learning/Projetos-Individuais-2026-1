# Projeto Individual 3 — Agente de Triagem Jurídica (CDC)

## Identificação

- **Aluna:** Aline Narumi Mizuta Kishita  
- **Projeto:** Projeto Individual 3 — Automação Inteligente de Processos com n8n e Agentes de IA  
- **Tema:** Agente de Triagem e Classificação de Reclamações (Código de Defesa do Consumidor)

---

## Descrição

Este projeto implementa uma automação no n8n integrada ao modelo Gemini para realizar a triagem inteligente de reclamações de consumo.

O fluxo recebe relatos de problemas via formulário, utiliza IA para identificar o embasamento legal no Código de Defesa do Consumidor (CDC), classifica a gravidade da demanda e executa ações automáticas, como notificações de urgência e registros de auditoria.

---

## Problema abordado

O volume de reclamações em canais digitais pode sobrecarregar equipes de atendimento e escritórios de advocacia. Demandas críticas (como corte indevido de serviços essenciais) podem ser perdidas entre dúvidas simples de garantia.

O agente resolve esse gargalo ao realizar uma triagem técnica inicial, priorizando casos urgentes e fornecendo embasamento legal imediato para a equipe de resolução.

---

## Objetivo

Criar um fluxo automatizado que:

- Receba relatos detalhados de problemas de consumo  
- Valide se a descrição possui conteúdo suficiente para análise jurídica  
- Use IA para classificar a urgência e identificar o artigo do CDC violado  
- Tome decisões condicionais no n8n (encaminhamento para canais de urgência ou dúvidas)  
- Registre o resultado completo em Google Sheets para persistência e auditoria  

---

## Solução final

A solução escolhida foi a **Solution C — Fluxo Agêntico Multicanal**.

O fluxo final opera da seguinte forma:

- **Entrada:** Formulário (n8n Form) com nome, contato e relato  
- **Validação:** Nó de código verifica se o texto é inteligível  
- **Análise de IA (Gemini):** Extrai artigos do CDC, categoria e nível de urgência  
- **Normalização:** Limpa a resposta da IA para campos estruturados  
- **Decisão (Switch/IF):**
  - **Urgente:** Dispara notificação imediata via Telegram  
  - **Dúvida:** Gera rascunho de resposta via Gmail  
  - **Geral:** Apenas registra o log na planilha  
- **Persistência:** Registro final em Google Sheets  

---

## Tecnologias utilizadas

- n8n (Orquestração de workflow)  
- Gemini (Inteligência Artificial / Análise Jurídica)  
- Google Sheets (Persistência e Log)  
- Telegram (Alertas de urgência)  
- Gmail (Comunicação com o cliente)  

---

## Estrutura do projeto
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


---

## Como testar o workflow no n8n

### 1. Importar o workflow

- Abra o n8n  
- Clique em **Import from File**  
- Selecione o arquivo `SRC/agente-triagem-cdc.json`  

---

### 2. Configurar Credenciais

- **Gemini:** Crie sua API Key no Google AI Studio e configure no nó de IA  
- **Google Sheets:** Configure o acesso à planilha de auditoria  
- **Telegram (Opcional):** Configure o token do bot para alertas de urgência  

---

### 3. Planilha de Auditoria

Crie uma planilha com as seguintes colunas:
data_hora | nome_consumidor | relato | categoria | artigo_cdc | resumo_juridico | urgencia | confianca | acao_executada


---

## Limitações e Riscos

- A precisão depende da clareza do relato do consumidor  
- A classificação jurídica da IA é informativa e não substitui um advogado  
- Falhas de conexão com APIs externas podem impactar o fluxo  

---

## Resultado

O projeto demonstra como uma automação com IA pode transformar relatos informais em dados estruturados, permitindo que empresas e órgãos de defesa do consumidor priorizem demandas críticas e respondam com maior precisão jurídica.