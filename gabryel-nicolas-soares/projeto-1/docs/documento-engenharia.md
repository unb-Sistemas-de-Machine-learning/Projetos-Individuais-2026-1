# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Gabryel Nicolas Soares de Sousa
> **Matrícula:** 221022570
> **Domínio:** Assistência Social
> **Função do agente:** Mediação/Conversação
> **Restrição obrigatória:** Explicabilidade Obrigatória

---

## 1. Problema e Contexto

O Brasil possui um sistema de assistência social estruturado em políticas públicas como Bolsa Família, Benefício de Prestação Continuada (BPC), Cadastro Único (CadÚnico), CRAS e CREAS. No entanto, grande parte da população elegível desconhece seus direitos ou enfrenta dificuldades para acessar esses serviços.

Milhões de famílias em situação de vulnerabilidade deixam de receber benefícios por falta de informação, dificuldade de acesso ou ausência de orientação adequada. Esse problema é ainda mais crítico em regiões com baixa cobertura de atendimento presencial.

O projeto propõe um agente de IA conversacional que atua como mediador entre o cidadão e o sistema de assistência social, guiando o usuário por meio de diálogo natural para identificar sua situação e indicar benefícios disponíveis, **sempre explicando o raciocínio com base na legislação vigente**.

**Público-alvo:**
- Cidadãos em situação de vulnerabilidade
- Trabalhadores de CRAS e CREAS
- Gestores municipais de assistência social

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|---|---|---|
| Cidadão em vulnerabilidade | Usuário final | Descobrir benefícios e como acessá-los |
| Trabalhador social (CRAS/CREAS) | Usuário operacional | Agilizar atendimento e triagem |
| Gestor municipal | Administrador | Melhorar eficiência e reduzir filas |
| Ministério do Desenvolvimento Social | Regulador | Garantir conformidade legal e atualização das regras |
| Equipe de desenvolvimento | Desenvolvedor | Manter, evoluir e auditar o sistema |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|---|---|---|
| RF01 | Conduzir conversa guiada para coletar dados do usuário | Alta |
| RF02 | Identificar benefícios elegíveis com base no perfil | Alta |
| RF03 | Explicar o raciocínio com base em critérios legais | Alta |
| RF04 | Manter contexto da conversa dentro da sessão | Alta |
| RF05 | Orientar próximos passos (documentos, locais, etc.) | Alta |
| RF06 | Responder dúvidas via RAG sobre benefícios | Média |
| RF07 | Indicar atendimento presencial quando necessário | Média |
| RF08 | Usar linguagem simples e acessível | Alta |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|---|---|---|
| RNF01 | Toda decisão de elegibilidade cita a base legal correspondente | Explicabilidade |
| RNF02 | Responder em até 5 segundos (excluindo tempo do LLM local) | Desempenho |
| RNF03 | Dados do usuário existem apenas durante a sessão ativa, não são persistidos em disco ou transmitidos a serviços externos | Privacidade (LGPD) |
| RNF04 | Interface CLI funcional em terminais padrão | Usabilidade |
| RNF05 | Usar modelo local (Ollama/Llama 3) para eliminar custo de API | Custo |
| RNF06 | Código modular com funções documentadas e tipagem explícita | Manutenibilidade |

---

## 5. Casos de Uso

### Caso de uso 1: Triagem de elegibilidade a benefícios

- **Ator:** Cidadão em situação de vulnerabilidade
- **Pré-condição:** Sessão iniciada; usuário menciona interesse em benefícios
- **Fluxo principal:**
  1. Usuário informa interesse em verificar benefícios
  2. Agente classifica intenção como "triagem"
  3. Agente coleta dados: renda, número de pessoas, idade e deficiência
  4. Motor de elegibilidade aplica regras legais e gera resultado estruturado
  5. LLM formata resposta explicativa com citação legal
  6. Agente apresenta benefícios aprovados, motivos e próximos passos
- **Fluxo alternativo:** Se nenhum benefício for aprovado, o agente explica os motivos e orienta o usuário a buscar o CRAS
- **Pós-condição:** Lista de benefícios com explicação legal + instruções de cadastro

---

### Caso de uso 2: Pergunta direta sobre um benefício

- **Ator:** Cidadão ou trabalhador social
- **Pré-condição:** Sessão iniciada
- **Fluxo principal:**
  1. Usuário faz pergunta específica (ex: "Quais documentos preciso para o BPC?")
  2. Agente classifica intenção como "pergunta"
  3. RAG recupera documentos relevantes da base de conhecimento
  4. LLM gera resposta baseada nos documentos e no contexto da sessão
  5. Resposta é exibida com citação da fonte legal
- **Pós-condição:** Resposta contextualizada com fonte citada

---

### Caso de uso 3: Suporte ao trabalhador do CRAS

- **Ator:** Trabalhador social do CRAS/CREAS
- **Pré-condição:** Atendimento a um cidadão em andamento
- **Fluxo principal:**
  1. Trabalhador informa os dados do cidadão atendido
  2. Agente realiza triagem e retorna resultado com fundamentação legal
  3. Trabalhador usa o resultado como apoio à decisão no atendimento presencial
- **Pós-condição:** Triagem documentada com base legal para registro do atendimento

---

## 6. Fluxo do Agente

```
┌─────────────────────────────────────────────────────────────┐
│                      ENTRADA DO USUÁRIO                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              CLASSIFICADOR DE INTENÇÃO                       │
│   (palavras-chave + fallback semântico)                      │
└──────┬──────────────┬──────────────────────┬────────────────┘
       │              │                      │
   TRIAGEM        PERGUNTA            ENCERRAMENTO
       │              │                      │
       ▼              ▼                      ▼
┌──────────┐   ┌─────────────┐      ┌───────────────┐
│ COLETA   │   │   BUSCA     │      │  Descarta     │
│ DE DADOS │   │   RAG       │      │  sessão e     │
│(validada)│   │(base local) │      │  encerra      │
└────┬─────┘   └──────┬──────┘      └───────────────┘
     │                │
     ▼                ▼
┌──────────────┐  ┌──────────────────────────────────┐
│    MOTOR     │  │   LLM (Llama 3 via Ollama)        │
│ ELEGIBILIDADE│  │   Gera resposta com contexto RAG  │
│ (regras lei) │  │   + dados da sessão               │
└────┬─────────┘  └──────────────┬───────────────────┘
     │                           │
     ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│        LLM formata resposta com explicação legal             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│   MEMÓRIA DE SESSÃO  ←── Armazena contexto para turnos      │
│   (dict em memória, descartado ao encerrar)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     SAÍDA AO USUÁRIO                         │
│   (resposta + citação legal + próximos passos)               │
└─────────────────────────────────────────────────────────────┘
```

O agente opera em duas camadas de raciocínio:

1. **Camada de regras (determinística):** A elegibilidade é decidida exclusivamente por regras codificadas com base na legislação (LOAS, Lei 14.284/2021). O LLM **não decide** quem tem direito — apenas formata a explicação. Isso garante explicabilidade total e evita alucinações na etapa crítica.

2. **Camada de linguagem (LLM):** O modelo de linguagem é usado para formatar respostas em linguagem natural acessível, responder perguntas via RAG e gerar orientações sobre próximos passos. O prompt inclui restrições explícitas contra invenção de informações.

---

## 7. Arquitetura do Sistema

- **Tipo de agente:** Pipeline sequencial com RAG e memória de sessão
- **LLM utilizado:** Llama 3 via Ollama (local)

**Justificativa da escolha do LLM:** O Llama 3 via Ollama foi escolhido por três razões: (1) execução 100% local, sem transmissão de dados do usuário a servidores externos — essencial para a conformidade com a LGPD; (2) custo zero de operação, viabilizando uso por municípios com orçamento restrito; (3) qualidade de geração em português suficiente para o domínio de assistência social. A alternativa GPT-4o-mini oferece melhor qualidade, mas exige API paga e transmissão de dados — incompatível com a restrição de privacidade deste projeto.

- **Componentes principais:**
  - [x] Módulo de entrada
  - [x] Processamento / LLM (Llama 3 via Ollama)
  - [ ] Ferramentas externas (tools)
  - [x] Memória de sessão
  - [x] Módulo de saída

| Componente | Responsabilidade |
|---|---|
| Módulo de entrada | Leitura e validação da mensagem do usuário |
| Classificador de intenção | Categoriza em: triagem, pergunta, encerramento |
| Módulo de coleta de dados | Coleta interativa com validação de tipo e range |
| Motor de elegibilidade | Aplica regras legais, retorna resultado estruturado |
| Módulo RAG | Busca documentos relevantes por similaridade de termos |
| LLM (Llama 3 / Ollama) | Formata respostas e responde perguntas com contexto |
| Memória de sessão | Mantém dados do usuário e histórico durante a conversa |
| Módulo de saída | Formata e exibe resposta ao usuário |

**Decisão arquitetural:** A separação entre o motor de elegibilidade (regras) e o LLM (linguagem) é a principal decisão do projeto. Garante explicabilidade total, ausência de alucinações na etapa crítica e auditabilidade completa dos resultados.

---

## 8. Estratégia de Avaliação

- **Métricas definidas:**

| Métrica | Meta | Método de medição |
|---|---|---|
| Precisão de elegibilidade | ≥ 85% | Comparação com gabarito legal para 5 perfis sintéticos |
| Qualidade da explicação | ≥ 4/5 | Avaliação manual |
| Latência do pipeline (excl. LLM) | ≤ 5s | Medição com time.time() antes e após a chamada ao Ollama |
| Cobertura do RAG | ≥ 80% | Percentual de perguntas com ao menos 1 doc relevante recuperado |

- **Conjunto de testes:**
  - 5 perfis sintéticos cobrindo os principais casos de elegibilidade
  - 1 pergunta direta sobre benefícios para testar o RAG
  - Testes de robustez: entrada inválida, cancelamento e perguntas fora do domínio

- **Método de avaliação:** avaliação automática por comparação com gabarito legal, avaliação manual e medição de latência.

---

## 9. Referências

1. Lei Orgânica da Assistência Social (LOAS) — Lei nº 8.742/1993
2. Lei nº 14.284/2021 — Programa Auxílio Brasil (base do Bolsa Família atual)
3. Decreto nº 11.150/2022 — Regulamentação do Bolsa Família
4. Decreto nº 6.135/2007 — Cadastro Único para Programas Sociais
5. Lei nº 14.237/2021 — Auxílio Gás
6. Lei nº 12.212/2010 — Tarifa Social de Energia Elétrica
7. Decreto nº 8.537/2015 — ID Jovem
8. Política Nacional de Assistência Social (PNAS/2004) — MDS
9. Lewis et al. — Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020)
10. Ollama — Documentação oficial — https://ollama.com