# ADR 001 — Escolha da Solução Final

## Status

Aceita

## Contexto

O Projeto Individual 3 exige a construção de uma automação inteligente utilizando n8n e agente de IA.

O problema escolhido foi a validação automatizada de entregas acadêmicas. A proposta é receber uma descrição da entrega, usar IA para classificar o status da entrega e registrar o resultado em uma planilha para rastreabilidade.

O fluxo final utiliza:

- Webhook para entrada;
- validação de entrada com nó Code;
- agente de IA com Gemini;
- normalização da resposta da IA;
- condicionais IF para separar os caminhos;
- Google Sheets para persistência e auditoria.

## Problema

Entregas acadêmicas podem conter muitos artefatos obrigatórios, como README, relatório técnico, evidências, workflow exportado, testes, ADR e documentação. O risco é o aluno submeter uma entrega incompleta sem perceber.

A automação busca reduzir esse risco por meio de uma triagem inicial feita por IA.

## Alternativas consideradas

### Solution A — Prompt simples

A primeira solução usa apenas uma chamada de IA com prompt simples.

Vantagens:

- implementação rápida;
- baixo custo;
- fácil de demonstrar;
- poucos nós no n8n.

Desvantagens:

- maior dependência da qualidade do prompt;
- menor controle sobre critérios obrigatórios;
- pouca robustez em caso de saída malformada;
- menor rastreabilidade da decisão.

### Solution B — Base de conhecimento

A segunda solução adiciona uma base de checklist com itens esperados da entrega.

Vantagens:

- mais aderente aos requisitos;
- reduz risco de esquecer itens obrigatórios;
- melhora a consistência da avaliação;
- facilita explicação dos critérios.

Desvantagens:

- exige manutenção da base;
- ainda depende de uma chamada principal de IA;
- não resolve sozinha problemas de parsing ou saída inválida.

### Solution C — Fluxo multi-etapas simplificado

A terceira solução usa validação de entrada, IA, normalização da saída, decisão condicional e persistência em Google Sheets.

Vantagens:

- usa n8n como orquestrador;
- usa IA para tomada de decisão;
- possui tratamento de entrada inválida;
- possui lógica condicional;
- registra resultados para auditoria;
- reduz dependência de notificações externas;
- é mais simples de manter e demonstrar.

Desvantagens:

- não envia e-mail ou Telegram;
- depende da qualidade da resposta do Gemini;
- não substitui avaliação humana final;
- exige configuração correta do Google Sheets.

## Decisão

A solução escolhida foi a Solution C — Fluxo multi-etapas simplificado.

## Justificativa

A Solution C foi escolhida porque atende melhor aos critérios centrais do projeto sem adicionar complexidade desnecessária.

A versão final removeu e-mail, Telegram, Switch complexo e Respond to Webhook para reduzir erros operacionais. A integração externa escolhida foi o Google Sheets, que também cumpre a função de persistência e rastreabilidade.

A IA influencia diretamente o fluxo, pois o campo `precisa_correcao` define se a entrega segue para o caminho de pendência ou para o caminho de validação sem pendências críticas.

## Consequências

A solução final é mais simples, estável e demonstrável.

Como consequência, a notificação externa foi substituída pelo registro estruturado em Google Sheets. Essa decisão reduz complexidade, mas mantém os requisitos principais: automação, IA, decisão condicional, integração e rastreabilidade.

## Critérios de comparação

| Critério | Solution A | Solution B | Solution C |
|---|---|---|---|
| Simplicidade | Alta | Média | Média |
| Robustez | Baixa | Média | Alta |
| Rastreabilidade | Baixa | Média | Alta |
| Tratamento de erro | Baixo | Médio | Alto |
| Aderência ao enunciado | Média | Boa | Alta |
| Manutenção | Alta | Média | Boa |

## Resultado

A Solution C foi adotada como solução final do projeto.