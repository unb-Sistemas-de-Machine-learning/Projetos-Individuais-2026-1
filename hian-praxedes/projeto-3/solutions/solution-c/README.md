# Solution C — Validação Multi-etapas com Fallback

## Abordagem

A Solution C é a solução final escolhida para o projeto.

Ela combina validação inicial, agente de IA, normalização da saída, verificação de confiança, persistência e roteamento automático no n8n.

Diferente das soluções anteriores, esta abordagem não depende apenas de uma chamada simples de IA. Ela trata falhas, entradas inválidas e baixa confiança antes de executar ações automáticas.

## Problema tratado

O problema tratado é a validação automatizada de entregas acadêmicas.

O usuário informa o que já foi feito em uma entrega, e o agente identifica se ela está completa, incompleta, crítica ou inválida. Depois disso, o n8n decide a rota adequada com base no resultado da IA.

## Fluxo proposto

Webhook

Validação de entrada

Agente de IA

Normalização da saída da IA

Verificação de confiança

Google Sheets

Switch por rota

Notificação externa

Respond to Webhook

## Desenho lógico do fluxo

1. O usuário envia uma descrição da entrega via Webhook.
2. Um nó de validação verifica se a entrada possui conteúdo mínimo.
3. A descrição é enviada ao agente de IA.
4. A IA retorna um JSON estruturado.
5. Um nó de código normaliza e valida a saída da IA.
6. O fluxo calcula a rota executada.
7. O resultado é registrado no Google Sheets.
8. Um Switch decide o caminho a seguir.
9. O fluxo envia notificação quando necessário.
10. O Webhook retorna uma resposta final ao usuário.

## Entrada esperada

Exemplo de entrada:

{
  "aluno": "Hian Praxedes",
  "projeto": "Projeto Individual 3",
  "descricao_entrega": "Fiz o README e o workflow no n8n, mas ainda não exportei o JSON nem tirei prints.",
  "link_repositorio": "https://github.com/seu-usuario/seu-repo"
}

## Saída esperada da IA

{
  "status": "incompleta",
  "percentual_prontidao": 60,
  "itens_identificados": [
    "README",
    "workflow n8n"
  ],
  "pendencias": [
    "Exportar workflow do n8n em JSON",
    "Adicionar prints de funcionamento",
    "Finalizar relatório técnico"
  ],
  "riscos": [
    "Ausência de evidências obrigatórias",
    "Impossibilidade de comprovar funcionamento da automação"
  ],
  "acao_recomendada": "solicitar_correcoes",
  "confianca": 0.91,
  "justificativa": "A entrega possui parte da documentação e menciona o workflow, mas ainda faltam exportação do fluxo, evidências e relatório técnico."
}

## Decisões do fluxo

| Condição | Rota executada |
|---|---|
| Entrada vazia ou insuficiente | revisao_humana |
| Confiança menor que 0.70 | revisao_humana |
| Status completa | registrar |
| Status incompleta | solicitar_correcoes |
| Status crítica | notificar_responsavel |
| Status inválida | revisao_humana |
| Erro ao interpretar JSON | revisao_humana |

## Ações por rota

### registrar

A entrega é registrada como pronta ou sem ação urgente.

Ação:

- salvar auditoria no Google Sheets;
- retornar diagnóstico ao usuário.

### solicitar_correcoes

A entrega possui pendências, mas não está em estado crítico.

Ação:

- salvar auditoria no Google Sheets;
- enviar e-mail ou Telegram com pendências;
- retornar lista de correções ao usuário.

### notificar_responsavel

A entrega está em risco crítico.

Ação:

- salvar auditoria no Google Sheets;
- enviar alerta para responsável;
- retornar diagnóstico com riscos.

### revisao_humana

A entrada é inválida, ambígua, tem baixa confiança ou a IA falhou.

Ação:

- salvar tentativa no Google Sheets;
- enviar alerta de revisão humana;
- retornar mensagem pedindo análise manual.

## Nós principais do n8n

A solução final usa os seguintes nós:

- Webhook;
- Code para validação de entrada;
- IF para verificar entrada válida;
- OpenAI ou AI Agent;
- Code para normalizar saída da IA;
- Google Sheets para registrar auditoria;
- Switch para decidir a rota;
- Gmail, Email ou Telegram para notificação;
- Respond to Webhook.

## Critérios usados pelo agente

O agente considera como itens importantes:

- README;
- agent.md;
- mission-brief.md;
- mentorship-pack.md;
- workflow-runbook.md;
- três soluções documentadas;
- workflow n8n exportado em JSON;
- evidências ou prints de funcionamento;
- Google Sheets ou outra persistência;
- tratamento de erro;
- ADR;
- merge-readiness-pack;
- relatório técnico;
- commits organizados;
- Pull Request.

## Tratamento de erros

A Solution C trata os seguintes erros:

- entrada vazia;
- descrição curta ou insuficiente;
- resposta da IA fora do formato JSON;
- confiança menor que 0.70;
- status inválido;
- necessidade de revisão humana.

## Persistência e rastreabilidade

Todas as execuções devem ser registradas no Google Sheets com:

- data e hora;
- aluno;
- projeto;
- descrição da entrega;
- status;
- percentual de prontidão;
- itens identificados;
- pendências;
- riscos;
- ação recomendada;
- confiança;
- justificativa;
- rota executada.

## Pontos positivos

- É a solução mais robusta.
- Possui fallback.
- Possui validação de entrada.
- Possui verificação de confiança.
- Permite auditoria.
- Demonstra IA influenciando o fluxo.
- Usa n8n como orquestrador.
- Possui integração externa real.
- Atende melhor aos critérios do projeto.

## Limitações

- É mais trabalhosa de configurar.
- Depende de credenciais externas.
- Depende de serviço de IA.
- Exige testes com diferentes cenários.
- Ainda não substitui avaliação humana final.

## Riscos

- A IA pode classificar incorretamente uma entrega ambígua.
- A integração com Google Sheets pode falhar.
- A notificação externa pode não ser enviada.
- O JSON da IA pode vir malformado.
- O usuário pode omitir informações importantes.

## Comparação com as soluções anteriores

A Solution A é simples e rápida, mas depende apenas de prompt.

A Solution B melhora a análise ao adicionar uma base de checklist.

A Solution C combina a clareza da Solution B com uma arquitetura mais segura, usando validação, fallback, persistência e roteamento automatizado.

## Justificativa da escolha

A Solution C foi escolhida como solução final porque é a que melhor atende aos requisitos do Projeto Individual 3.

Ela demonstra:

- fluxo claro no n8n;
- IA sendo usada para decidir, não apenas responder;
- lógica condicional;
- integração externa;
- persistência;
- tratamento de erros;
- rastreabilidade;
- evidências demonstráveis.

## Demonstração esperada

A demonstração deve incluir:

- entrada enviada ao Webhook;
- resposta estruturada da IA;
- registro no Google Sheets;
- rota escolhida no Switch;
- notificação externa;
- resposta final do Webhook;
- caso de erro ou entrada inválida.