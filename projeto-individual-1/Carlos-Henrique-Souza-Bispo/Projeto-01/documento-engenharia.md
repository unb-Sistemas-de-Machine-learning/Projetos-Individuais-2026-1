# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Carlos Henrique Souza Bispo
> **Matrícula:** 211061529
> **Domínio:** Educação
> **Função do agente:** Classificação
> **Restrição obrigatória:** Explicabilidade obrigatória

---

## 1. Problema e Contexto

Instituições de ensino enfrentam dificuldade para identificar, com antecedência, estudantes com risco de evasão. Em muitos casos, o problema só é percebido quando a situação já está crítica (faltas acumuladas, baixo desempenho e desengajamento). Isso reduz a efetividade de intervenções pedagógicas e de apoio.

O projeto propõe um agente de IA para classificar o nível de risco de evasão de cada estudante (baixo, moderado ou alto) com base em dados acadêmicos e um texto curto de relato do aluno. O diferencial obrigatório do projeto é a explicabilidade: toda decisão do agente deve apresentar justificativas claras, evidências usadas e recomendações práticas para ação da coordenação.

Público-alvo principal:

- Coordenação pedagógica
- Professores e tutores
- Equipe de permanência estudantil

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Coordenação pedagógica | Prioriza casos e define plano de intervenção | Reduzir evasão com decisões rápidas e justificadas |
| Professores/tutores | Acompanham alunos em risco | Entender motivos do risco para orientar ações em sala e mentorias |
| Estudantes | Fornecem dados e recebem suporte | Ter atendimento mais cedo e personalizado |
| Gestão da instituição | Define metas de retenção | Melhorar indicadores de permanência e desempenho |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | Receber dados do estudante (frequência, nota média, acessos semanais, pendência financeira e relato textual). | Alta |
| RF02 | Classificar o risco de evasão em três classes: baixo, moderado e alto. | Alta |
| RF03 | Gerar explicação textual obrigatória para a classificação, com fatores que impactaram a decisão. | Alta |
| RF04 | Exibir score numérico de risco (0 a 100) para facilitar priorização de casos. | Média |
| RF05 | Sugerir ações recomendadas por nível de risco para orientar intervenção. | Média |
| RF06 | Permitir execução em lote por arquivo JSON para avaliação de múltiplos casos. | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O agente deve responder cada análise individual em até 2 segundos no modo local (sem chamada remota). | Desempenho |
| RNF02 | Toda saída deve conter seção de explicabilidade (fatores positivos, negativos e recomendações). | Explicabilidade |
| RNF03 | O sistema deve continuar funcional sem chave de API, usando fallback local determinístico. | Confiabilidade |
| RNF04 | Estrutura de código modular, com separação entre entrada, decisão e geração de explicação. | Manutenibilidade |
| RNF05 | Não armazenar dados pessoais sensíveis no código-fonte ou logs de demonstração. | Segurança/Privacidade |

---

## 5. Casos de Uso

### Caso de uso 1: Classificar risco individual

- **Ator:** Coordenador pedagógico
- **Pré-condição:** Dados básicos do estudante disponíveis
- **Fluxo principal:**
  1. Coordenador informa os dados acadêmicos e o relato do estudante.
  2. O agente calcula score de risco usando regras e análise textual.
  3. O agente retorna classe de risco + explicação + recomendações.
- **Pós-condição:** Caso fica pronto para decisão de intervenção.

### Caso de uso 2: Avaliar lista de estudantes

- **Ator:** Equipe de permanência
- **Pré-condição:** Arquivo JSON de casos de teste estruturado
- **Fluxo principal:**
  1. Equipe executa o script de avaliação em lote.
  2. O agente processa cada entrada do arquivo.
  3. O sistema retorna resultados para comparação com rótulos esperados.
- **Pós-condição:** Métricas de qualidade e relatório de desempenho disponíveis.

---

## 6. Fluxo do Agente

Fluxo textual do pipeline:

```
Entrada estruturada + relato textual
→ validação de dados
→ extração de features (acadêmicas e textuais)
→ cálculo de score de risco
→ classificação (baixo/moderado/alto)
→ geração de explicação (LLM opcional + fallback local)
→ recomendações de intervenção
→ saída JSON
```

---

## 7. Arquitetura do Sistema

- **Tipo de agente:** Pipeline sequencial tool-using com módulo de decisão explicável
- **LLM utilizado:** OpenAI (gpt-4o-mini) opcional via variável `OPENAI_API_KEY`; fallback local sem LLM
- **Componentes principais:**
  - [x] Módulo de entrada
  - [x] Processamento / LLM
  - [x] Ferramentas externas (tools)
  - [ ] Memória
  - [x] Módulo de saída

Diagrama simplificado:

```
CLI/API Input
    ↓
Validation Layer
    ↓
Risk Scoring Engine (regras)
    ↓
Classifier (thresholds)
    ↓
Explanation Builder
  ├─ LLM Adapter (OpenAI, opcional)
  └─ Local Template Fallback
    ↓
JSON Output + Recommended Actions
```

---

## 8. Estratégia de Avaliação

- **Métricas definidas:**
  - Acurácia da classe de risco (comparação com rótulo esperado)
  - Cobertura de explicação (100% das saídas com justificativa)
  - Latência média por caso
  - Taxa de falha em execução sem API key
- **Conjunto de testes:**
  - 5 casos sintéticos representando cenários de baixo, moderado e alto risco
  - Dados baseados em padrões típicos de frequência, nota, engajamento e relato
- **Método de avaliação:**
  - Automático (testes unitários para regras e classificação)
  - Manual (inspeção da qualidade das explicações geradas)

---

## 9. Referências

1. OpenAI API Reference. https://platform.openai.com/docs/api-reference
2. OECD (2023). Student retention and early warning systems in education.
3. Sculley et al. (2015). Hidden Technical Debt in Machine Learning Systems.
