# Relatório Técnico — Projeto Individual 3

## Problema escolhido

O problema escolhido foi a validação automatizada de entregas acadêmicas.

Em projetos acadêmicos com muitos artefatos obrigatórios, é comum que estudantes esqueçam itens importantes, como documentação, prints, testes, workflow exportado ou relatório técnico. A proposta deste projeto é criar um agente que faça uma triagem inicial da entrega antes da submissão.

## Desenho do fluxo

O fluxo foi implementado no n8n com a seguinte estrutura:

Webhook

Validar entrada

Entrada válida?

Se a entrada for inválida:
Montar resultado inválido
Registrar auditoria no Google Sheets

Se a entrada for válida:
IA - Validar entrega
Normalizar IA
Precisa de correção?

Se precisar de correção:
Montar resultado pendente
Registrar auditoria no Google Sheets

Se não precisar de correção:
Montar resultado ok
Registrar auditoria no Google Sheets

## Papel do agente de IA

O agente de IA é responsável por analisar a descrição da entrega acadêmica e retornar uma classificação estruturada.

Ele identifica:

- status da entrega;
- percentual de prontidão;
- itens identificados;
- pendências;
- riscos;
- ação recomendada;
- confiança;
- justificativa.

A IA influencia diretamente o fluxo porque o campo gerado na normalização define se a entrega precisa de correção ou se pode ser considerada sem pendências críticas.

## Decisões de arquitetura

A solução final usa:

- n8n como orquestrador;
- Webhook como entrada;
- Gemini como modelo de IA;
- nós Code para validação e normalização;
- IF para lógica condicional;
- Google Sheets como camada de persistência e auditoria.

Durante a construção, foram consideradas três soluções:

- Solution A: prompt simples;
- Solution B: checklist/base de conhecimento;
- Solution C: fluxo multi-etapas simplificado.

A Solution C foi escolhida por equilibrar simplicidade, rastreabilidade e aderência aos requisitos do projeto.

## Limitações do sistema

- O sistema depende da descrição enviada pelo usuário.
- A IA pode errar classificações em textos ambíguos.
- A automação não substitui a avaliação humana final.
- O fluxo depende das credenciais do Gemini e do Google Sheets.
- O sistema não envia notificações externas por e-mail ou Telegram.

## Riscos

- A IA pode retornar JSON inválido.
- O usuário pode omitir informações importantes.
- O Google Sheets pode falhar por erro de credencial.
- A entrega pode ser classificada como completa sem evidência suficiente.
- A planilha pode ficar inconsistente se as colunas forem alteradas.

## Tratamento de erros e limites

O fluxo trata entrada inválida antes de chamar a IA. Se a descrição estiver vazia ou curta demais, o fluxo monta um resultado inválido e registra a tentativa no Google Sheets.

A normalização da saída da IA também possui fallback para casos em que a resposta não esteja em JSON válido.

## Evidências

As evidências de funcionamento foram adicionadas em:

docs/evidence/

Elas incluem prints do workflow, execução dos testes e registros no Google Sheets.

## Conclusão

O projeto implementa uma automação inteligente com n8n e agente de IA, demonstrando orquestração de serviços, decisão automatizada, tratamento de entrada inválida, persistência em Google Sheets e documentação auditável.