# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Breno Queiroz Lima
> **Matrícula:** 211063069
> **Domínio:** Open source / Comunidades
> **Função do agente:** Resumo
> **Restrição obrigatória:** [Restrição sorteada/escolhida]

---

## 1. Problema e Contexto

As vezes não é simples escrever uma boa mensagem de _commit_.
Ferramenta CLI para sugestão de mensagens de _commits_.

---

## 2. Stakeholders

| Stakeholder   | Papel          | Interesse no sistema                                                         |
| ------------- | -------------- | ---------------------------------------------------------------------------- |
| Desenvolvedor | Usuário direto | Gerar mensagens de commits claras, rápidas e padronizadas sem esforço manual |

---

## 3. Requisitos Funcionais (RF)

| ID         | Descrição                                                     | Prioridade |
| ---------- | ------------------------------------------------------------- | ---------- |
| ---------- |
| RF01       | Gerar mensagens consistentes e padronizadas a partir de diffs | Alta       |
| RF02       | Disponibilizar interface via linha de comando (CLI)           | Alta       |
| RF03       | Permitir ao usuário editar a mensagem gerada antes do commit  | Alta       |
| RF04       | Suportar diferentes padrões de commit                         | Média      |
| RF05       | Permitir configuração de idioma das mensagens                 | Média      |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID    | Descrição                                                               | Categoria   |
| ----- | ----------------------------------------------------------------------- | ----------- |
| RNF01 | O sistema deve gerar a mensagem em até 3 segundos para diffs pequenos   | Desempenho  |
| RNF02 | O sistema deve garantir segurança dos dados (não vazar código sensível) | Segurança   |
| RNF03 | O sistema deve permitir configuração simples e intuitiva                | Usabilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Gerar mensagem de commit automaticamente

- **Ator:** Desenvolvedor
- **Pré-condição:**
  - O repositório Git deve estar inicializado
  - Deve haver alterações (diff) prontas para commit
  - A ferramenta CLI deve estar instalada e configurada
- **Fluxo principal:**
  1. O desenvolvedor executa o comando da ferramenta via CLI
  2. O sistema coleta o diff das alterações no repositório
  3. O sistema envia o diff para o modelo LLM
  4. O sistema gera uma mensagem de commit baseada no diff
  5. O sistema exibe a mensagem gerada ao usuário
  6. O usuário pode editar a mensagem (opcional)
  7. O usuário confirma a mensagem  
     8 . O sistema executa o commit com a mensagem final - **Pós-condição:**

---

## 6. Fluxo do Agente

_Descreva ou desenhe o fluxo de funcionamento do agente. Pode ser um diagrama (imagem ou mermaid) ou uma descrição textual passo a passo._

```
Entrada → [etapa 1] → [etapa 2] → ... → Saída
```

---

## 7. Arquitetura do Sistema

- **Tipo de agente:** (Pipeline sequencial com uso de ferramentas)
- **LLM utilizado:** (Gemini)
- **Componentes principais:**
  - [x] Módulo de entrada
    - Interface CLI
    - Coleta do diff via comando Git `git diff --staged`
  - [x] Processamento / LLM
    - Pré-processamento do diff (remoção de ruído, limitação de tamanho)
    - Construção do prompt
    - Chamada ao modelo LLM
  - [x] **Ferramentas externas (tools)**
    - Git (leitura de diff e execução de commit)
    - API de LLM ou modelo local
  - [ ] Memória
  - [ ] Módulo de saída
    - Exibição da mensagem gerada no terminal
    - Integração com editor do Git para edição
    - Execução do commit final

---

## 8. Estratégia de Avaliação

- **Métricas definidas:** (coerência com o diff informado)
- **Conjunto de testes:** (mensagens de commits do repositório)
- **Método de avaliação:** (manual)

---

## 9. Referências

_Liste artigos, documentações, repositórios ou materiais consultados._

1.
2.
3.
