# Relatório Técnico: Multi-Agent Red Team Framework

## 1. Problema Escolhido
Automatização do ciclo de Red Team (Reconhecimento, Validação e Relatório) para testes contínuos de segurança. O problema central é a alta dependência de execução manual e a falta de padronização nas respostas de segurança em ambientes de desenvolvimento/staging.

## 2. Desenho do Fluxo (Abordagem de Maturidade)
O projeto adota uma arquitetura em três camadas (Soluções A, B e C), utilizando o **n8n** como orquestrador central e o **Gemini** (LLM) como o motor de decisão inteligente.
- **Solution A:** Foco em planejamento tático via prompts.
- **Solution B:** Foco em validação prática via integração de APIs externas (VirusTotal).
- **Solution C:** Foco em autonomia total com orquestração multiagente.

## 3. Papel do Agente de IA
O agente de IA atua em diferentes níveis de responsabilidade:
- **Planner:** Define a estratégia de ataque baseada no alvo.
- **Analista:** Avalia dados brutos (logs/APIs) e toma a decisão final de risco.
- **Relator:** Traduz a linguagem técnica em relatórios estruturados para o SOC.

## 4. Decisões de Arquitetura
- **Uso de n8n:** Orquestração visual e modular, permitindo fácil integração de nós de erro e políticas de retry.
- **Autenticação:** Utilização de headers seguros (`x-apikey`) para integração com serviços terceiros como VirusTotal.
- **Rastreabilidade:** Todos os fluxos contam com logs de auditoria e diretrizes de resiliência configuradas.

## 5. Implementação e Orquestração (n8n)
A estrutura do projeto foi dividida em workflows independentes:

### 5.1 Solution A (Planejamento)
Utiliza Gemini para gerar o plano de ataque.
- **Trigger:** Webhook.
- **Processing:** `HTTP Request` (Gemini API) -> `Validator Code`.

### 5.2 Solution B (Validação)
Utiliza VirusTotal para verificar a reputação do alvo.
- **Trigger:** Webhook.
- **Processing:** `HTTP Request` (VirusTotal API v3 com header `x-apikey`) -> `Code` (Normalização).

### 5.3 Diferença entre URL de Teste e Produção
- **Test URL (`/webhook-test/`):** Utilizada durante o desenvolvimento e depuração.
- **Production URL (`/webhook/`):** Utilizada após ativação do workflow (`Active`), rodando em segundo plano.

## 6. Procedimento de Teste (ReqBin)
Utilizamos requisições POST com payload JSON (`{"alvo": "exemplo.com"}`) para validar ambos os fluxos, confirmando o status 200 OK em ambos os endpoints.

## 7. Próximos Passos
- Integração automática: Disparar Solution B após a conclusão da Solution A.
- Expansão de APIs: Adição de consultas a Shodan/DNS.
- Deploy final: Monitoramento das execuções em produção.

