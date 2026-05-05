# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Silas Neres de Souza  
> **Matrícula:** [200043536  
> **Data de entrega:** 05/05/2026  

---
## 1. Resumo do Projeto

Este projeto implementa um agente inteligente de triagem jurídica baseado no Código de Defesa do Consumidor (CDC). Utilizando o n8n como orquestrador e o Gemini como motor de decisão, o sistema automatiza a recepção, classificação e encaminhamento de reclamações. Casos de alta gravidade (como interrupção de serviços essenciais) disparam alertas em tempo real via Telegram, enquanto dúvidas sobre direitos (como arrependimento de compra) recebem orientações automáticas por e-mail, garantindo eficiência e conformidade legal.

## 2. Problema Escolhido

O problema escolhido foi a triagem ineficiente de demandas consumeristas. A demora na identificação de urgências gera prejuízos financeiros e danos morais. A automação é relevante pois utiliza IA para interpretar o relato informal do cidadão, convertendo-o em dados estruturados que acionam os canais corretos de resolução sem a necessidade de uma primeira leitura humana manual para cada caso.

## 3. Desenho do Fluxo

O fluxo segue uma estrutura lógica de validação e roteamento:

1. **Entrada:** Captura de dados via formulário.
2. **Validação:** Filtro por script para evitar entradas vazias.
3. **Inteligência:** O Agente de IA processa o texto e gera um objeto JSON.
4. **Decisão:** Um nó Switch direciona o fluxo com base na categoria da IA.
5. **Ação:** 
   - **Urgente:** Mensagem no Telegram.
   - **Dúvida:** E-mail via Gmail.
   - **Geral:** Apenas registro em planilha.
6. **Persistência:** Todos os casos são salvos no Google Sheets para auditoria.

## 4. Papel do Agente de IA

A IA atua como o motor de decisão do fluxo.
- **Modelo utilizado:** Gemini 3 Flash.
- **Tipo de decisão:** Classificação categórica, extração de artigos do CDC e avaliação de confiança.
- **Impacto no fluxo:** A saída da IA define qual "braço" do workflow será executado. Se a IA identificar um problema de saúde ou serviço essencial, o fluxo prioriza o canal de urgência (Telegram).

## 5. Lógica de Decisão

O fluxo possui dois pontos críticos de decisão:
- **Condição 1 (Técnica):** A entrada possui texto suficiente? Se não, encerra com erro amigável.
- **Condição 2 (Negócio):** Qual a categoria da reclamação? 
  - `URGENTE` -> Rota Telegram.
  - `DUVIDA` -> Rota Gmail.
  - `PADRAO` ou `INVALIDO` -> Rota Silenciosa (apenas Sheets).

## 6. Integrações e Persistência

- **Gemini:** Análise jurídica e estruturação de dados.
- **Google Sheets:** Funciona como a memória do sistema, registrando data, nome, relato, artigo do CDC e a decisão tomada.
- **Telegram/Gmail:** Canais de saída para comunicação ativa.

## 7. Tratamento de Erros e Limites

- **Fallback de IA:** Se a resposta da IA não for um JSON válido, o sistema utiliza um nó de tratamento para marcar o caso como "Revisão Humana Necessária".
- **Baixa Confiança:** Caso a confiança da IA seja inferior a 0.7, o sistema evita o envio automático de e-mails para não fornecer orientações erradas.

## 8. Diferenciais Implementados

- [x] **Multi-step reasoning:** O fluxo separa a validação da análise.
- [x] **Integração com base de conhecimento:** O prompt da IA inclui diretrizes específicas do CDC.
- [x] **Roteamento Multicanal:** Uso dinâmico de diferentes ferramentas de comunicação.

---
**Conclusão:** O projeto demonstra uma aplicação prática de agentes de IA para otimizar o atendimento jurídico inicial, priorizando o que é crítico e automatizando o que é informativo.