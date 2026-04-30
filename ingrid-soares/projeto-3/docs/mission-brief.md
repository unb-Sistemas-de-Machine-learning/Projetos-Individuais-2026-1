# Mission Brief

> **Aluno(a):** Ingrid Soares
> **Matrícula:** [Sua matrícula]
> **Domínio:** Cibersegurança - Multi-Agent Red Team Framework

---

## 1. Objetivo do agente
Projetar e implementar um sistema multiagente orquestrado pelo n8n que automatize o ciclo de Red Team (Reconhecimento, Validação de Vulnerabilidades e Relatório) para testes contínuos de segurança em ambientes autorizados.

---

## 2. Problema que ele resolve
A execução de testes de intrusão (Pentest) é frequentemente manual e pontual. Este sistema resolve a falta de automação na verificação de superfícies de ataque, permitindo que analistas de segurança validem vulnerabilidades de forma contínua e estruturada, reduzindo o tempo entre a exposição e a detecção.

---

## 3. Usuários-alvo
Analistas de Red Team, profissionais de segurança ofensiva e DevSecOps.

---

## 4. Contexto de uso
Execução automática de "reconhecimento e validação de superfície de ataque" em ambientes controlados (Sandbox) ou CI/CD, antes de deploy em produção.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Domínio ou endpoint alvo com escopo autorizado |
| **Formato da entrada** | Texto (JSON via Webhook) |
| **Saída** | Relatório de vulnerabilidades confirmadas e recomendações |
| **Formato da saída** | JSON estruturado (com severidade, descrição e evidências) |

---

## 6. Limites do agente

### O que o agente faz:
- **Agente Reconhecedor:** Enumera subdomínios e endpoints.
- **Agente Analista (LLM):** Decide o vetor de ataque (Red Team tactics) e avalia riscos.
- **Agente Executor:** Orquestra ferramentas (scripts/APIs) para validação.
- **Agente Relator:** Consolida evidências.

### O que o agente NÃO deve fazer:
- Realizar ataques em alvos não autorizados ou fora do escopo definido.
- Executar ataques de negação de serviço (DoS) que impactem a disponibilidade do alvo.
- Exfiltrar dados reais; o objetivo é a prova de conceito (PoC).

---

## 7. Critérios de aceitação
- [ ] Fluxo multiagente implementado no n8n.
- [ ] IA capaz de decidir o próximo passo (ex: se encontrou subdomínio, validar arquivos sensíveis).
- [ ] Integração com ao menos uma ferramenta de varredura ou API de inteligência de ameaças.
- [ ] Logs auditáveis das decisões tomadas pelo "cabeça" (Agente Analista).

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Execução fora do escopo | Baixa | Altíssimo | Regras rígidas de "scope control" no n8n e nos scripts |
| Falsos positivos no Pentest | Média | Médio | Validação lógica multi-etapas antes da confirmação da vulnerabilidade |

---

## 9. Evidências necessárias
- [ ] Diagrama do fluxo multiagente no n8n.
- [ ] Relatório técnico comparando as 3 soluções (A, B, C).
- [ ] Logs de execução demonstrando a cadeia de decisão (Chain-of-Thought).
