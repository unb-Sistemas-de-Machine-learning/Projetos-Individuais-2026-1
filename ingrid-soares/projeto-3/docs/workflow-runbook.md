# Workflow Runbook: Multi-Agent Red Team Framework

Este documento descreve o processo obrigatório de execução para o desenvolvimento do framework.

---

## Passo a Passo do Desenvolvimento

1.  **Leitura e Alinhamento:** Revisar o *Mission Brief* e o *Mentorship Pack* para garantir que todos os artefatos estejam alinhados com os objetivos éticos e técnicos.
2.  **Proposta de Soluções:** Propor três abordagens distintas para a automação do ciclo de Red Team (Reconhecimento, Validação, Reporte).
3.  **Registro de Soluções:** Criar pastas `solutions/solution-a`, `solutions/solution-b` e `solutions/solution-c`.
4.  **Prototipagem Mínima:** Implementar protótipos funcionais para cada abordagem no n8n.
5.  **Testes e Evidências:** Validar cada protótipo contra um alvo controlado.
6.  **Comparação (ADR):** Avaliar as três soluções em relação a custo, complexidade, qualidade de resposta, riscos e manutenibilidade.
7.  **Decisão Final:** Registrar a decisão da solução escolhida em `docs/adr/001-escolha-da-solucao.md`.
8.  **Merge-Readiness:** Gerar o `docs/merge-readiness-pack.md` para consolidar o estado de prontidão para entrega.
9.  **Consolidação:** Integrar a solução final na pasta `src/` e limpar o projeto.

---

## Regras de Execução

- **Commits Atômicos:** Cada etapa do runbook deve corresponder a um ou mais commits com mensagem clara e racionalidade técnica.
- **Rastreabilidade:** Toda decisão que alterar o comportamento do framework deve ser documentada em um novo arquivo de ADR dentro de `docs/adr/`.
- **Validação:** Não avance para a fase de implementação da solução final sem ter comparado as três alternativas propostas.
