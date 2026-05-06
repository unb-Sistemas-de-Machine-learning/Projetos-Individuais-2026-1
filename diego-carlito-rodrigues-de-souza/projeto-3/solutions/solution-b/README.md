# Solution B: Integração com Base de Conhecimento - RAG

## Visão Geral
A evolução lógica da Solution A. Aqui, tentamos resolver a alucinação do modelo conectando o n8n a uma fonte de dados externa.

## Fluxo Lógico (n8n)
1. **Webhook Trigger:** Recebe a dúvida do aluno.
2. **LLM Node (Extractor):** O modelo é forçado a extrair apenas uma palavra-chave (ex: `prazo`, `nota`, `duvida_codigo`).
3. **Google Sheets Node (Lookup):** O n8n pega a palavra-chave e busca a resposta "oficial" do professor na planilha da disciplina.
4. **LLM Node (Generator):** Lê a resposta dura da planilha e reescreve em tom socrático e educado.
5. **Webhook Response:** Devolve ao aluno.

## Avaliação Rápida
- **Prós:** Zera a chance de o LLM dar uma data de prova errada, pois ele lê o calendário oficial.
- **Contras (O porquê de ser descartada):** Alta complexidade de manutenção (o professor precisa manter o Sheets perfeitamente atualizado). Além disso, não possui caminhos de roteamento (Switch). Todo ticket passa por todo o fluxo, consumindo tokens desnecessários em mensagens de spam.

## Status:
❌ Descartada por não possuir nós de decisão estrutural (Switch/If).
