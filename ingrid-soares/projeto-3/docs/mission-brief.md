# Mission Brief

> **Projeto:** Security Validation & Automation Framework
> **Aluno(a):** Ingrid Soares

---

## 1. Objetivo do Projeto
Projetar e implementar um framework de segurança híbrido (Determinístico + LLM) orquestrado pelo n8n que automatiza o ciclo de Red Team (Reconhecimento, Validação e Relatório) de forma contínua e gratuita.

---

## 2. Problema que ele resolve
A execução de testes de segurança é frequentemente manual e cara. Este framework automatiza a verificação de superfícies de ataque, combinando fatos determinísticos (VirusTotal) com inteligência contextual (LLM via Groq) para entregar relatórios precisos sem custo operacional.

---

## 3. Arquitetura do Framework
- **Soluções Modulares:** A (Planejamento), B (Validação), C (Orquestração), D (Testes Automatizados).
- **Entrada:** JSON via Webhook.
- **Saída:** Relatório de severidade e evidências técnicas.

---

## 4. O que o sistema faz:
- **Agente Analista (LLM/Groq):** Realiza análise tática e estratégica baseada nos resultados validados.
- **Motor Determinístico (API VT):** Executa verificações factuais de reputação de ativos.
- **Infraestrutura de QA (D):** Pipeline automatizado de testes de integração.

---

## 5. Critérios de aceitação
- [x] Arquitetura híbrida (Determinística + LLM) implementada.
- [x] Integração de API gratuita (VirusTotal e Groq Cloud).
- [x] Orquestração assíncrona funcional (Solution C).
- [x] Testes automatizados (Solution D) validados.
