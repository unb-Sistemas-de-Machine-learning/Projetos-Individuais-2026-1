# Workflow Runbook: Security Validation & Automation Framework

Este documento descreve o processo de execução e desenvolvimento do framework de segurança híbrido.

---

## Passo a Passo do Desenvolvimento

1. **Alinhamento:** Revisar os requisitos do framework híbrido (Determinístico + LLM).
2. **Implementação de Soluções:**
   - **Solution A:** Planejamento tático com IA (Llama-3 via Groq).
   - **Solution B:** Validação determinística (VirusTotal API).
   - **Solution C:** Orquestrador assíncrono para integração A+B.
   - **Solution D:** Infraestrutura de testes automatizados (Python/Pytest).
3. **Validação:** Rodar scripts em `solutions/solution-d/tests/` para garantir a integridade.
4. **Consolidação:** Integrar os fluxos e realizar o deploy em modo "Active" no n8n.

---

## Regras de Operação

- **Commits Atômicos:** Cada fase deve ser documentada e commitada individualmente.
- **Rastreabilidade:** Todas as decisões arquiteturais (como a transição para Groq Cloud) estão registradas em ADRs dentro de `docs/adr/`.
- **QA:** A versão de produção (`Active`) depende do disparo bem-sucedido do script de testes da Solution D.
- **Sustentabilidade:** Priorizar o uso de APIs com tiers gratuitos (VirusTotal/Groq) para manter custo zero.
