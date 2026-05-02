# Mentorship Pack

> **Projeto:** Security Validation & Automation Framework
> **Aluno(a):** Ingrid Soares

---

## 1. Princípios da Arquitetura Híbrida
O framework evoluiu para um modelo híbrido que prioriza a precisão técnica e a sustentabilidade financeira:

- **Camada Determinística:** O uso de APIs de Threat Intelligence (ex: VirusTotal) é obrigatório para garantir validações factuais antes de qualquer análise estratégica.
- **Camada de Inteligência (LLM):** O uso de IA (Groq/Llama-3) é reservado para análise contextual e geração de relatórios, não para decisões binárias críticas.
- **Custo Zero:** A arquitetura é otimizada para o uso de *tiers* gratuitos, garantindo execução contínua sem custos.

## 2. Orientações de Desenvolvimento
- **Segurança sobre Velocidade:** A precisão na identificação de vulnerabilidades é superior à velocidade de execução.
- **Automação de Testes:** A implementação de testes automatizados (Solution D) é um requisito para manter o sistema em nível de maturidade 10.0.
- **Observabilidade:** O uso da aba "Executions" no n8n é essencial para auditoria e depuração de falhas.

## 3. Padrões de Código e Integração
- **Linguagem:** n8n (workflows), Python (scripts de teste e integração).
- **Interface:** Toda integração deve seguir o padrão de payload JSON estruturado.
- **Testes:** Qualquer alteração no fluxo de trabalho deve ser validada pelo script de teste (`test_framework.py`).

## 4. Estilo de documentação
- Toda alteração deve ser registrada no `relatorio-entrega.md` e, se necessário, documentada no `ADR-001`.
- A arquitetura final deve sempre manter a separação entre o orquestrador (C) e as soluções modulares (A, B, D).
