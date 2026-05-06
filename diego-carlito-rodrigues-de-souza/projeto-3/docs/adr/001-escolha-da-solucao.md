# ADR-001: Adoção de Arquitetura Agêntica Híbrida para Triagem

> **Data:** 05/05/2026
> **Status:** aceita

---

## Contexto

Precisamos de um sistema para triar automaticamente as dúvidas dos alunos de monitoria acadêmica. O problema central é que modelos de linguagem (LLMs), se deixados livres, tendem a "agradar" o usuário, o que na academia significa entregar código pronto (trapaça) ou inventar extensões de prazos (alucinação burocrática). A automação precisa ser segura, de baixo custo e separar questões técnicas de exceções que exigem o professor.

---

## Alternativas consideradas

### Alternativa A: Abordagem Reativa Simples (LLM Direto)

- **Descrição:** O n8n recebe a mensagem via Webhook, passa para o LLM responder diretamente e devolve ao aluno.
- **Prós:** Desenvolvimento rápido e latência mínima.
- **Contras:** Falta de governança. O LLM não toma decisões de roteamento, ele apenas responde a tudo, correndo o risco de atuar fora de seus limites acadêmicos.

### Alternativa B: RAG com Base de Conhecimento

- **Descrição:** O LLM extrai o tema, o n8n busca a resposta oficial em uma planilha, e o LLM reescreve a resposta.
- **Prós:** Evita alucinações de datas e notas.
- **Contras:** Não resolve o roteamento de emergências/exceções. Gastaria tokens do LLM processando mensagens de spam ou ofensas que não existem na planilha.

### Alternativa C: Agente Híbrido com Roteamento Determinístico

- **Descrição:** Uso de NLU (Natural Language Understanding) em duas etapas. O Primeiro LLM atua apenas para gerar um JSON classificando a intenção. Um nó determinístico (`Switch`) do n8n lê o JSON e roteia a ação (Responder tecnicamente vs. Salvar em Log vs. Escalar no Slack).
- **Prós:** Risco quase zero de alucinação em demandas burocráticas. Cumpre o critério de "IA usada para decidir".
- **Contras:** Maior tempo de setup no n8n (exigência de configuração fina de Error Triggers e JSON Parsers).

---

## Decisão

**A Alternativa C foi escolhida.** 
Ela foi selecionada porque isola o comportamento probabilístico do LLM das ações críticas do sistema. O LLM ganha o papel de "Roteador" (cérebro analítico), enquanto o n8n atua como "Executor" (músculo determinístico).

---

## Consequências

- **Impacto Positivo:** O sistema garante segurança acadêmica, garantindo que o professor receba alertas imediatos para casos excepcionais (ex: atestados médicos), enquanto dúvidas de código recebem mentoria socrática.
- **Impacto Técnico:** Obriga a criação de "System Prompts" altamente restritivos para garantir que o LLM 1 retorne sempre um JSON válido, caso contrário, o nó `Switch` do n8n falhará.

---

## Referências

- [Mission Brief do Projeto](../mission-brief.md)
- [Padrões de Arquitetura do Mentorship Pack](../mentorship-pack.md)
