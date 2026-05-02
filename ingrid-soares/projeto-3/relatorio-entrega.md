# Relatório Técnico: Multi-Agent Red Team Framework

## 1. Problema Escolhido
Automatização do ciclo de Red Team (Reconhecimento, Validação e Relatório) para testes contínuos de segurança. O problema central é a alta dependência de execução manual e a falta de padronização nas respostas de segurança em ambientes de desenvolvimento/staging.

## 2. Desenho do Fluxo (Abordagem de Maturidade)
O projeto adota uma arquitetura em três camadas (Soluções A, B e C), utilizando o **n8n** como orquestrador central e o **Gemini** (LLM) como o motor de decisão inteligente.
- **Solution A:** Foco em planejamento tático via prompts.
- **Solution B:** Foco em validação prática via integração de APIs externas (DNS/VirusTotal).
- **Solution C:** Foco em autonomia total com orquestração multiagente.

## 3. Papel do Agente de IA
O agente de IA atua em diferentes níveis de responsabilidade:
- **Planner:** Define a estratégia de ataque baseada no alvo.
- **Analista:** Avalia dados brutos (logs/APIs) e toma a decisão final de risco.
- **Relator:** Traduz a linguagem técnica em relatórios estruturados para o SOC.

## 4. Decisões de Arquitetura
- **Uso de n8n:** Orquestração visual e modular, permitindo fácil integração de nós de erro e políticas de retry.
- **Abordagem Agêntica:** Implementação baseada no framework de Engenharia de Software Agêntica, com separação clara de responsabilidades (Mission Brief, Mentorship Pack).
- **Rastreabilidade:** Todos os fluxos contam com logs de auditoria e diretrizes de resiliência configuradas.

## 5. Implementação e Orquestração (n8n)
A Solution A foi implementada como um workflow no n8n. O fluxo utiliza um nó `Webhook` (gatilho), `HTTP Request` (chamada ao Gemini) e `Code` (validação de resposta).

### 5.1 Diferença entre URL de Teste e Produção
- **Test URL (`/webhook-test/`):** Utilizada durante a edição. Requer que o modo "Test" seja ativado manualmente no n8n antes de disparar a requisição.
- **Production URL (`/webhook/`):** Utilizada após o workflow ser marcado como "Active" e salvo. O fluxo roda em segundo plano e registra execuções na aba "Executions".

### 5.2 Procedimento de Teste (ReqBin)
Para verificar a integração, utilizamos o ReqBin:
1. **Método:** POST.
2. **URL:** URL de produção ou teste (conforme o status do workflow).
3. **Payload (JSON):** 
   ```json
   {
     "alvo": "exemplo.com"
   }
   ```
4. **Resultado Esperado:** HTTP 200 OK com a resposta: `{"message": "Workflow was started"}`. As execuções bem-sucedidas são confirmadas na aba "Executions" do n8n, onde o nó final exibe o resultado do processamento.

## 6. Limitações do Sistema
- Dependência de limites de API (rate limits) de serviços de terceiros.
- Não determinismo inerente aos modelos de linguagem em tarefas críticas de segurança.
- Necessidade de configuração de infraestrutura de rede para execução de ferramentas externas.

## 7. Análise de Performance e Custo
Para garantir a sustentabilidade do framework, consideramos os seguintes aspectos:
- **Consumo de IA:** Estimamos um consumo moderado de tokens, otimizado pelo uso de prompts estruturados e JSON.
- **Estratégias de Otimização:** Implementação de cache local (n8n DB) para resultados de APIs, minimizando chamadas redundantes e custos operacionais.
- **Latência:** Latência projetada de 5-15s por ciclo, com foco principal em chamadas de I/O de rede e processamento de IA.

