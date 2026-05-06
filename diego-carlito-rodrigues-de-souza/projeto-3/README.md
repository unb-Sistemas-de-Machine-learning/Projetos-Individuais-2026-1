# Projeto 3: Assistente de Monitoria Universitária Autônomo

Este projeto apresenta um assistente educacional automatizado orquestrado pelo **n8n**, utilizando inteligência artificial (Groq/Llama3) para realizar a triagem inteligente de dúvidas de alunos e aplicar o Método Socrático no ensino de programação, com interface direta via **Telegram**.

## A Solução Final (Maturidade C)
A implementação consolidada deste projeto é a **Solução C (Roteamento Híbrido)**, uma arquitetura agêntica que utiliza o LLM estritamente como um roteador semântico (gerando um JSON classificador de intenções) e o orquestrador (n8n) para executar ações determinísticas: aplicar tutoria técnica, registrar dúvidas burocráticas ou escalar exceções médicas e de infraestrutura.

## Estrutura do Repositório
- `docs/`: Documentação completa de engenharia, incluindo o Registro de Decisões Arquiteturais (`adr/`), o Relatório de Entrega (`relatorio-entrega.md`), o `merge-readiness-pack.md`, as diretrizes pedagógicas (`mentorship-pack.md`) e as comprovações de funcionamento (`evidence/`).
- `src/`: "Código-fonte" da orquestração, contendo o arquivo de fluxo final da Solução C (`workflow.json`) e ferramentas de automação/debug (`testar-bot.sh`).

## Como Executar
1. Clone este repositório para a sua máquina local.
2. Importe o arquivo `src/workflow.json` para o seu ambiente n8n (Cloud ou Local).
3. Configure as credenciais obrigatórias no n8n: **Telegram Account** (Token do BotFather) e **Groq API** (Chave de API).
4. Ative o workflow no canto superior direito do n8n.
5. Para testar, interaja diretamente com o bot criado no aplicativo Telegram, ou utilize o script de simulação rodando `./src/testar-bot.sh` no seu terminal.
