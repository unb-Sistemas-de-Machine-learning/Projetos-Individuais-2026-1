# Documento de Engenharia — Projeto Individual 1

> **Aluno(a):** Ingrid Soares
> **Matrícula:** [Sua matrícula]
> **Domínio:** Open Source / Comunidades
> **Função do agente:** Extração de Dados
> **Restrição obrigatória:** Privacidade (LGPD)

---

## 1. Problema e Contexto

No ecossistema de software de código aberto (Open Source), a escolha da licença é fundamental para definir como o software pode ser utilizado, modificado e distribuído. No entanto, acompanhar as tendências de licenciamento em milhares de novos projetos criados diariamente em plataformas como o GitHub é um desafio. 

Este agente de IA resolve o problema de **extração e análise de metadados de licenciamento** em projetos recém-criados, permitindo identificar padrões de adoção de licenças por linguagem de programação e popularidade, sem comprometer a privacidade dos desenvolvedores, em total conformidade com a LGPD. O público-alvo inclui pesquisadores de ecossistemas de software, mantenedores de comunidades e desenvolvedores interessados em tendências de mercado.

---

## 2. Stakeholders

| Stakeholder | Papel | Interesse no sistema |
|-------------|-------|----------------------|
| Pesquisadores de Software | Usuários | Analisar tendências de licenciamento e adoção de tecnologias. |
| Mantenedores de Comunidades | Interessados | Entender o panorama legal de novos projetos em seus ecossistemas. |
| Órgãos de Fiscalização (LGPD) | Auditores | Garantir que a extração de dados públicos não colete informações pessoais. |

---

## 3. Requisitos Funcionais (RF)

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O sistema deve buscar repositórios recém-criados na API do GitHub. | Alta |
| RF02 | O sistema deve extrair metadados como nome, URL, linguagem, licença, estrelas e forks. | Alta |
| RF03 | O sistema deve validar e limpar os dados para garantir que nenhuma informação pessoal seja extraída. | Alta |
| RF04 | O sistema deve salvar os dados processados em um formato estruturado (JSON). | Alta |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Descrição | Categoria |
|----|-----------|-----------|
| RNF01 | O sistema deve estar em total conformidade com a LGPD, não coletando dados pessoais. | Privacidade / Segurança |
| RNF02 | O sistema deve lidar com os limites de taxa (rate limits) da API do GitHub. | Desempenho / Confiabilidade |
| RNF03 | O sistema deve ser modular e fácil de estender (ex: adicionar novas fontes de dados). | Manutenibilidade |
| RNF04 | Toda a documentação e logs devem estar em Português (Brasil). | Usabilidade / Internacionalização |

---

## 5. Casos de Uso

### Caso de uso 1: Extração de Tendências de Licenciamento

- **Ator:** Analista de Dados / Pesquisador
- **Pré-condição:** Conectividade com a internet e (opcionalmente) um token da API do GitHub configurado.
- **Fluxo principal:**
  1. O usuário configura os parâmetros de busca (ex: data de criação, linguagem).
  2. O agente inicia a busca na API do GitHub.
  3. O agente filtra e extrai apenas os metadados de projeto definidos.
  4. O agente valida a ausência de dados pessoais (limpeza LGPD).
  5. O agente salva os resultados em um arquivo JSON.
- **Pós-condição:** Um arquivo JSON contendo os metadados dos projetos é gerado para análise posterior.

---

## 6. Fluxo do Agente

O agente opera em um pipeline sequencial de processamento de dados:

```
Configuração → Busca (GitHub API) → Dados Brutos → Validação/Limpeza (LGPD) → Processamento → Saída (JSON)
```

1.  **Configuração:** Carrega parâmetros e chaves de ambiente.
2.  **Busca:** Realiza requisições paginadas à API do GitHub.
3.  **Validação/Limpeza:** Filtra campos sensíveis e garante que apenas metadados de projeto não identificáveis sejam mantidos.
4.  **Saída:** Estrutura e salva os dados finais.

---

## 7. Arquitetura do Sistema

- **Tipo de agente:** Pipeline sequencial de extração e processamento de dados (Data Extraction Agent).
- **LLM utilizado:** Para este protótipo inicial, o foco foi na lógica de extração e conformidade LGPD. Uma integração com LLM (como GPT-4) pode ser adicionada no módulo de processamento para análise qualitativa das descrições.
- **Componentes principais:**
  - [x] Módulo de entrada (Configuração)
  - [ ] Processamento / LLM (Módulo de Análise - Opcional)
  - [x] Ferramentas externas (GitHub API)
  - [ ] Memória (Não necessária para este caso de uso)
  - [x] Módulo de saída (Utils / JSON)

---

## 8. Estratégia de Avaliação

- **Métricas definidas:** Precisão da extração de licenças, integridade dos metadados, conformidade LGPD (zero dados pessoais) e desempenho da API.
- **Conjunto de testes:** Execução real com os 100-200 projetos mais populares criados desde 2024.
- **Método de avaliação:** Automático (verificação de campos e tipos) e manual (inspeção visual para detecção de dados pessoais).

---

## 9. Referências

1. Documentação da API do GitHub: https://docs.github.com/en/rest
2. Guia da LGPD para desenvolvedores: https://www.gov.br/governodigital/pt-br/seguranca-e-protecao-de-dados/guias-e-orientacoes/guia-lgpd-para-desenvolvedores
3. Licença MIT: https://opensource.org/licenses/MIT
