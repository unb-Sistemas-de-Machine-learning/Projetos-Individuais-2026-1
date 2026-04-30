# ADR 001: Definição das Estratégias de Prototipagem (Red Team Framework)

## Contexto
Necessidade de automatizar o ciclo de Red Team (Reconhecimento, Validação e Relatório) usando n8n e Agentes de IA. Devemos comparar três níveis de maturidade/complexidade.

## Abordagens Propostas

### Solution A: Abordagem Baseada em Prompt (Simples)
- **Foco:** IA atua como um planejador tático.
- **n8n:** Fluxo linear onde o LLM recebe o alvo e gera um plano de ataque (passos teóricos).
- **Complexidade:** Baixa.

### Solution B: Abordagem com Ferramentas Externas (RAG/APIs)
- **Foco:** Validação prática de vulnerabilidades.
- **n8n:** Integração com APIs externas (ex: VirusTotal, ferramentas de scan de DNS) para coletar evidências reais.
- **Complexidade:** Média.

### Solution C: Multi-Agente Autônomo (Complexa)
- **Foco:** Orquestração de tarefas e automação completa.
- **n8n:** Fluxo com agentes especializados (Reconhecedor, Executor, Relator) que se comunicam entre si.
- **Complexidade:** Alta.

## Status
Em exploração (Prototipagem).
