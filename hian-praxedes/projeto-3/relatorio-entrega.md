# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Hian Praxedes de Souza Oliveira  
> **Matrícula:** [200019520]  
> **Data de entrega:** 05/05/2026  

---

## 1. Resumo do Projeto

Este projeto implementa um agente de validação de entregas acadêmicas utilizando n8n, Gemini e Google Sheets. O problema automatizado é a conferência inicial de uma entrega acadêmica antes da submissão, verificando se itens importantes foram informados, como README, documentação, workflow exportado, evidências, testes, ADR e relatório técnico.

A IA atua como componente de decisão dentro do fluxo. Ela analisa a descrição enviada pelo usuário, classifica a entrega como completa, incompleta, crítica ou inválida, identifica pendências, estima um percentual de prontidão, avalia riscos e recomenda uma ação.

O principal resultado obtido foi um workflow funcional no n8n que recebe uma entrada via Webhook, valida a entrada, utiliza IA para classificar a entrega, executa decisões condicionais e registra o resultado em uma planilha Google Sheets para rastreabilidade e auditoria.

---

## 2. Problema Escolhido

O problema escolhido foi a validação automatizada de entregas acadêmicas.

Em projetos acadêmicos com muitos artefatos obrigatórios, é comum que estudantes esqueçam arquivos, evidências, prints, testes, documentação ou instruções de execução. Isso pode gerar entregas incompletas, perda de rastreabilidade e dificuldade para revisar o que foi efetivamente produzido.

A automação é relevante porque funciona como uma triagem inicial antes da submissão. O usuário informa o estado da entrega, e o agente identifica pendências e riscos de forma estruturada. Assim, o fluxo ajuda a reduzir falhas simples de submissão e gera um histórico auditável das validações realizadas.

---

## 3. Desenho do Fluxo

O fluxo implementado no n8n segue uma estrutura simplificada e auditável.

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

O workflow recebe uma entrada via Webhook, valida se a descrição possui conteúdo suficiente e, quando válida, envia os dados para o agente de IA. A resposta da IA é normalizada, avaliada em uma condição e registrada no Google Sheets.

### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Webhook | Trigger | Recebe a entrada com aluno, projeto, descrição da entrega e link do repositório. |
| Validar entrada | Code | Verifica se a descrição da entrega possui conteúdo mínimo para análise. |
| Entrada válida? | IF | Decide se o fluxo deve seguir para a IA ou registrar uma entrada inválida. |
| IA - Validar entrega | Gemini | Analisa a descrição da entrega e retorna classificação, pendências, riscos e ação recomendada. |
| Normalizar IA | Code | Converte a resposta da IA para campos estruturados e calcula se precisa de correção. |
| Precisa de correção? | IF | Decide se a entrega possui pendências ou pode ser considerada sem pendências críticas. |
| Montar resultado inválido | Code | Gera um resultado padronizado para entrada inválida. |
| Montar resultado pendente | Code | Gera um resultado para entregas incompletas, críticas ou com baixa confiança. |
| Montar resultado ok | Code | Gera um resultado para entregas consideradas completas. |
| Append row in sheet | Google Sheets | Registra a execução, decisão e justificativa na planilha de auditoria. |

---

## 4. Papel do Agente de IA

A IA é utilizada como mecanismo de análise e decisão dentro do fluxo. Ela não é usada apenas para gerar texto; sua saída influencia diretamente o caminho executado no n8n.

- **Modelo/serviço utilizado:** Gemini.
- **Tipo de decisão tomada pela IA:** classificação, extração estruturada, avaliação de risco e recomendação de ação.
- **Como a decisão da IA afeta o fluxo:** a IA retorna um JSON com status, percentual de prontidão, pendências, riscos, confiança e ação recomendada. O nó de normalização interpreta essa saída e gera o campo `precisa_correcao`. Esse campo é usado pelo nó IF para decidir se o fluxo seguirá para `Montar resultado pendente` ou `Montar resultado ok`.

Exemplo de saída esperada da IA:

    {
      "status": "incompleta",
      "percentual_prontidao": 60,
      "itens_identificados": ["README", "workflow n8n"],
      "pendencias": ["Exportar workflow do n8n em JSON", "Adicionar prints de funcionamento"],
      "riscos": ["Ausência de evidências obrigatórias"],
      "acao_recomendada": "solicitar_correcoes",
      "confianca": 0.91,
      "justificativa": "A entrega possui parte dos artefatos, mas ainda faltam evidências."
    }

---

## 5. Lógica de Decisão

O fluxo possui dois pontos principais de decisão.

- **Condição 1: Entrada válida?**
  - Caminho A → Se `entrada_valida = true`, o fluxo segue para o agente de IA.
  - Caminho B → Se `entrada_valida = false`, o fluxo monta um resultado inválido e registra no Google Sheets sem chamar a IA.

- **Condição 2: Precisa de correção?**
  - Caminho A → Se `precisa_correcao = true`, o fluxo monta um resultado pendente e registra a necessidade de correção ou revisão humana.
  - Caminho B → Se `precisa_correcao = false`, o fluxo monta um resultado ok e registra que a entrega foi validada sem pendências críticas.

A decisão `precisa_correcao` é calculada com base no status retornado pela IA, na ação recomendada e na confiança da resposta.

---

## 6. Integrações

| Serviço | Finalidade |
|---------|------------|
| Gemini | Classificar a entrega acadêmica, identificar pendências, avaliar riscos e recomendar ação. |
| Google Sheets | Registrar entradas, decisões, justificativas e resultados para auditoria. |
| Webhook | Receber dados externos para iniciar o workflow. |

---

## 7. Persistência e Rastreabilidade

A persistência foi implementada com Google Sheets. Cada execução do fluxo adiciona uma nova linha na planilha de auditoria.

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

Essa estrutura permite auditar o que foi enviado, qual decisão foi tomada pela IA, qual caminho o fluxo executou e qual foi a justificativa registrada.

---

## 8. Tratamento de Erros e Limites

O fluxo implementa tratamento de erros e limites em três pontos principais.

- **Falhas da IA:** o nó `Normalizar IA` tenta converter a resposta da IA para JSON. Caso a resposta venha fora do formato esperado, o fluxo gera um resultado inválido com ação recomendada `revisao_humana`.

- **Entradas inválidas:** antes de chamar a IA, o nó `Validar entrada` verifica se a descrição possui conteúdo mínimo. Se a descrição estiver vazia ou curta demais, o fluxo não chama a IA e registra a entrada como inválida.

- **Fallback (baixa confiança):** quando a confiança retornada pela IA é menor que o limite definido, o fluxo considera que a entrega precisa de correção ou revisão humana.

Limites conhecidos:

- a classificação depende da qualidade da descrição enviada;
- a IA pode errar em casos ambíguos;
- a automação não substitui a avaliação humana final;
- a execução depende das credenciais do Gemini e do Google Sheets.

---

## 9. Diferenciais implementados

- [ ] Memória de contexto
- [x] Multi-step reasoning
- [x] Integração com base de conhecimento
- [ ] Uso de embeddings / busca semântica

Observação: o projeto utiliza um processo multi-etapas com validação, IA, normalização, decisão condicional e persistência. Também foi criada uma base simples de checklist em `data/base-checklist-entrega.csv`, usada como referência documental do projeto.

---

## 10. Limitações e Riscos

As principais limitações e riscos identificados foram:

- a IA pode classificar incorretamente uma entrega ambígua;
- o usuário pode omitir informações importantes na descrição;
- o resultado depende da qualidade do prompt e da resposta do modelo;
- a resposta da IA pode vir fora do formato JSON esperado;
- a planilha pode falhar se as colunas forem alteradas;
- credenciais externas precisam ser configuradas corretamente no n8n;
- a validação automatizada não substitui a revisão humana final.

A solução reduz esses riscos com validação de entrada, fallback para resposta malformada, registro em Google Sheets e documentação dos testes executados.

---

## 11. Como executar

Instruções para importar e rodar o workflow:

    # 1. Importar o workflow no n8n
    Importar o arquivo workflows/agente-validacao-entrega-academica.json

    # 2. Configurar credenciais necessárias
    Configurar a credencial do Gemini no nó IA - Validar entrega
    Configurar a credencial do Google Sheets no nó Append row in sheet

    # 3. Criar a planilha de auditoria
    Criar uma planilha chamada Auditoria - Validador de Entregas Acadêmicas
    Criar uma aba chamada Auditoria
    Adicionar as colunas documentadas no README.md

    # 4. Executar uma entrada de teste
    Abrir o nó Webhook
    Clicar em Listen for test event
    Enviar uma requisição POST para a URL do Webhook

Exemplo de entrada de teste:

    {
      "aluno": "Hian Praxedes",
      "projeto": "Projeto Individual 3",
      "descricao_entrega": "Fiz o README e o workflow no n8n, mas ainda não exportei o JSON nem tirei prints.",
      "link_repositorio": "https://github.com/seu-usuario/seu-repo"
    }

Resultado esperado no Google Sheets:

    status: incompleta
    acao_recomendada: solicitar_correcoes
    rota_executada: Entrega precisa de correções ou revisão humana.

---

## 12. Referências

1. Documentação oficial do n8n.
2. Documentação oficial do Google Gemini / Google AI Studio.
3. Documentação oficial do Google Sheets.
4. Enunciado do Projeto Individual 3.
5. Artefatos internos do projeto: Mission Brief, Agent.md, Mentorship Pack, Workflow Runbook, ADR e Merge-Readiness Pack.

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (.json)
- [x] Código/scripts auxiliares incluídos
- [x] Demonstração do fluxo (vídeo ou prints)
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
