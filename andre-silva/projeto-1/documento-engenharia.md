# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** André Emanuel Bispo da Silva
> **Matrícula:** 221007813
> **Domínio:** Open source / comunidades
> **Função do agente:** Classificação
> **Restrição obrigatória:** Baixo custo

---

## 1. Problema e Contexto

Em desenvolvimento de software as vezes projetos crescem o suficiente para necessitar
da separação em módulos, este agente automatiza a separação de arquivos python em módulos.

---

## 2. Stakeholders

| Stakeholder   | Papel   | Interesse no sistema                                                  |
| ------------- | ------- | --------------------------------------------------------------------- |
| Desenvolvedor | Usuário | Organizar projetos que cresceram rapidamente em módulos com agilidade |
|               |         |                                                                       |

---

## 3. Requisitos Funcionais (RF)

| ID   | Descrição                                                                          | Prioridade |
| ---- | ---------------------------------------------------------------------------------- | ---------- |
| RF01 | Separar arquivos python em módulos diferentes, mantendo o comportamento do sistema | Alta       |
| RF02 | Ter interface CLI                                                                  | Alta       |
| RF03 | Mostrar preview das mudanças a serem feitas                                        | Alta       |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID    | Descrição                                                                    | Categoria      |
| ----- | ---------------------------------------------------------------------------- | -------------- |
| RNF02 | O sistema deve ter o mesmo funcionamento externo antes e depois das mudanças | Confiabilidade |
| RNF02 | O script só pode efetuar as alterações após confirmação do usuário           | Confiabilidade |

---

## 5. Casos de Uso

### Caso de uso 1:

- **Ator:** Desenvolvedor
- **Pré-condição:** Arquivo python disponível
- **Fluxo principal:**
  1. O desenvolvedor executa o comando para separar o arquivo em módulos.
  2. O agente analisa o arquivo e sugere uma estrutura de módulos.
  3. O agente gera um script com as mudanças a serem feitas.
  4. Após a revisão das mudanças a serem feitas (através da leitura do script), o desenvolvedor executa as mudanças
- **Pós-condição:** O projeto está organizado em módulos, mantendo o mesmo comportamento externo.

---

## 6. Fluxo do Agente

_Descreva ou desenhe o fluxo de funcionamento do agente. Pode ser um diagrama (imagem ou mermaid) ou uma descrição textual passo a passo._

```
Usuário -> Comando -> upload do projeto -> Análise do projeto -> Sugestão de estrutura de módulos -> Geração de script
-> Revisão do usuário -> Confirmação do usuário -> Execução do script -> Projeto organizado em módulos
```

---

## 7. Arquitetura do Sistema

_Descreva a arquitetura escolhida para o agente. Responda:_

- **Tipo de agente:** pipeline sequencial
- **LLM utilizado:** Gemini
- **Componentes principais:**
  - [x] Módulo de entrada
    - Interface CLI
    - Leitura da estrutura do projeto
  - [x] Processamento / LLM
    - Análise do código (estrutura do projeto e conteúdo)
    - Sugestão de estrutura de módulos
    - Geração de script
  - [ ] Ferramentas externas (tools)
  - [ ] Memória
  - [x] Módulo de saída
    - Geração de script para execução

- **Diagrama de arquitetura:** _(opcional, mas recomendado)_

---

## 8. Estratégia de Avaliação

_Descreva como você pretende avaliar o agente:_

- **Métricas definidas:** (Código compila/executa corretamente, satisfaz testes, mesmo comportamento)
- **Conjunto de testes:** (Este próprio projeto, e projetos de exemplo)
- **Método de avaliação:** (manual)

---
