# Projeto Individual 3 — Agente de Validação de Entrega Acadêmica

## Identificação

- **Aluno:** Hian Praxedes de Souza Oliveira - 200019520
- **Projeto:** Projeto Individual 3 — Automação Inteligente de Processos com n8n e Agentes de IA
- **Tema:** Agente de Validação de Entrega Acadêmica

## Descrição

Este projeto implementa uma automação no n8n com uso de IA para validar entregas acadêmicas.

O fluxo recebe uma descrição da entrega, utiliza Gemini para classificar o status da entrega, identifica pendências, avalia riscos e registra o resultado em Google Sheets.

## Problema abordado

Entregas acadêmicas costumam exigir diversos artefatos obrigatórios, como documentação, workflow exportado, prints, testes, evidências e relatório técnico.

O problema é que o aluno pode submeter uma entrega incompleta sem perceber. O agente reduz esse risco ao realizar uma validação inicial automatizada antes da submissão.

## Objetivo

Criar um fluxo automatizado que:

- receba uma descrição de entrega acadêmica;
- valide se a entrada possui conteúdo suficiente;
- use IA para classificar a entrega;
- identifique pendências e riscos;
- tome uma decisão condicional no n8n;
- registre o resultado em Google Sheets para auditoria.

## Solução final

A solução final escolhida foi a **Solution C — Fluxo multi-etapas simplificado**.

O fluxo final é:

    Webhook
    ↓
    Validar entrada
    ↓
    Entrada válida?
    ├── false → Montar resultado inválido → Google Sheets
    └── true → IA - Validar entrega
              ↓
              Normalizar IA
              ↓
              Precisa de correção?
              ├── true → Montar resultado pendente → Google Sheets
              └── false → Montar resultado ok → Google Sheets

## Tecnologias utilizadas

- n8n
- Gemini
- Google Sheets
- Webhook
- Markdown
- Git
- GitHub

## Integrações

A integração externa utilizada foi o **Google Sheets**.

A planilha é usada como camada de persistência e rastreabilidade, registrando cada execução do fluxo.

A planilha registra:

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

## Estrutura do projeto

    projeto-4/
    ├── agent.md
    ├── README.md
    ├── relatorio-entrega.md
    ├── data/
    │   └── base-checklist-entrega.csv
    ├── docs/
    │   ├── mission-brief.md
    │   ├── mentorship-pack.md
    │   ├── workflow-runbook.md
    │   ├── merge-readiness-pack.md
    │   ├── adr/
    │   │   └── 001-escolha-da-solucao.md
    │   └── evidence/
    ├── solutions/
    │   ├── solution-a/
    │   │   └── README.md
    │   ├── solution-b/
    │   │   └── README.md
    │   └── solution-c/
    │       └── README.md
    ├── src/
    │   ├── prompt-agent.md
    │   ├── schema-saida.json
    │   └── exemplos-entrada.json
    ├── tests/
    │   └── casos-de-teste.md
    └── workflows/
        ├── README.md
        └── agente-validacao-entrega-academica.json

## Soluções avaliadas

### Solution A — Prompt simples

A primeira alternativa usa apenas uma chamada de IA com prompt simples para validar a entrega.

Essa solução é fácil de implementar, mas possui menor robustez e menor rastreabilidade.

### Solution B — Base de conhecimento

A segunda alternativa adiciona uma base de checklist com itens obrigatórios da entrega.

Essa solução melhora a consistência da validação, mas ainda depende de uma única etapa principal de IA.

### Solution C — Fluxo multi-etapas simplificado

A terceira alternativa combina validação de entrada, IA, normalização da resposta, decisão condicional e persistência em Google Sheets.

Essa foi a solução escolhida por equilibrar simplicidade, rastreabilidade, tratamento de erro e aderência aos requisitos do projeto.

## Como testar o workflow no n8n

Para testar o projeto, é necessário importar o workflow exportado e configurar as credenciais externas usadas pelo fluxo.

### 1. Importar o workflow

1. Abrir o n8n.
2. Clicar em `Import workflow`.
3. Selecionar o arquivo `workflows/agente-validacao-entrega-academica.json`.
4. Salvar o workflow importado.

### 2. Configurar credencial do Gemini

O workflow usa Gemini para classificar a entrega acadêmica.

Para configurar:

1. Acessar o Google AI Studio.
2. Criar uma API Key.
3. No n8n, abrir o nó `IA - Validar entrega`.
4. Criar uma credencial do tipo Google Gemini/Gemini API.
5. Colar a API Key.
6. Salvar a credencial.

Observação: a API Key não é versionada no repositório por segurança.

### 3. Criar a planilha de auditoria

Criar uma planilha no Google Sheets chamada:

    Auditoria - Validador de Entregas Acadêmicas

Criar uma aba chamada:

    Auditoria

A primeira linha da aba deve conter exatamente as seguintes colunas:

    data_hora
    aluno
    projeto
    descricao_entrega
    status
    percentual_prontidao
    itens_identificados
    pendencias
    riscos
    acao_recomendada
    confianca
    justificativa
    rota_executada

### 4. Configurar o nó Google Sheets

No n8n:

1. Abrir o nó `Append row in sheet`.
2. Configurar a credencial Google.
3. Selecionar a planilha `Auditoria - Validador de Entregas Acadêmicas`.
4. Selecionar a aba `Auditoria`.
5. Conferir o mapeamento das colunas.

### 5. Executar o workflow

Abrir o nó `Webhook` e clicar em `Listen for test event`.

Depois, enviar uma requisição POST para a URL de teste do Webhook.

Exemplo de teste com PowerShell:

    $body = @{
      aluno = "Hian Praxedes"
      projeto = "Projeto Individual 3"
      descricao_entrega = "Fiz o README e o workflow no n8n, mas ainda não exportei o JSON nem tirei prints."
      link_repositorio = "https://github.com/seu-usuario/seu-repo"
    } | ConvertTo-Json -Depth 10

    Invoke-WebRequest `
      -Uri "URL_DO_WEBHOOK_DE_TESTE_AQUI" `
      -Method Post `
      -Body $body `
      -ContentType "application/json" `
      -UseBasicParsing

### 6. Resultado esperado

Após executar o teste, o Google Sheets deve receber uma nova linha com a análise da entrega.

Para o exemplo acima, espera-se algo semelhante a:

    status: incompleta
    acao_recomendada: solicitar_correcoes
    rota_executada: Entrega precisa de correções ou revisão humana.

## Casos de teste

Os casos de teste estão documentados em:

    tests/casos-de-teste.md

Eles incluem:

- entrega incompleta;
- entrada inválida;
- entrega completa.

## Evidências

As evidências de funcionamento estão disponíveis em:

    docs/evidence/

Essa pasta contém prints do workflow, execução da IA, decisões condicionais e registros no Google Sheets.

## Decisão arquitetural

A decisão pela Solution C está registrada em:

    docs/adr/001-escolha-da-solucao.md

## Limitações

- O sistema depende da descrição enviada pelo usuário.
- A IA pode errar classificações em textos ambíguos.
- O fluxo depende das credenciais do Gemini e do Google Sheets.
- A automação não substitui a avaliação humana final.
- A solução não envia notificações por e-mail ou Telegram.

## Resultado

O projeto demonstra uma automação com IA capaz de classificar entregas acadêmicas, tomar decisões condicionais no n8n e registrar os resultados para auditoria em Google Sheets.
