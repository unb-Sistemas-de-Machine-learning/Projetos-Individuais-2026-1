# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Ingrid Soares
> **Matrícula:** [Sua matrícula]
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

Este projeto desenvolveu um agente de IA para extração e análise de metadados de licenciamento em projetos de software open source. O problema abordado é a dificuldade em monitorar tendências de conformidade legal em larga escala no GitHub. O agente construído utiliza a API do GitHub para coletar dados de projetos recém-criados, aplicando um pipeline rigoroso de validação e limpeza para garantir que nenhuma informação pessoal seja processada, em total conformidade com a LGPD. Como principal resultado, o agente extraiu e validou dados de 200 repositórios de alta popularidade, gerando um dataset estruturado em JSON pronto para análise estatística e qualitativa.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Open Source / Comunidades |
| **Função do agente** | Extração de Dados |
| **Restrição obrigatória** | Privacidade (LGPD) |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe como entrada parâmetros de configuração definidos em `src/config.py`, incluindo critérios de busca do GitHub (ex: data de criação >= 2024-01-01, ordenação por estrelas) e metadados de projeto desejados.

### 3.2 Processamento (Pipeline)

O pipeline do agente é sequencial e robusto:

```
Configuração → Chamadas à API (GitHub REST API) → Extração de Campos → Validação LGPD (Filtro de Dados Pessoais) → Formatação JSON → Salvamento em Arquivo
```

### 3.3 Decisão

A lógica de decisão do agente é baseada em regras programáticas e validação de esquemas:
1.  **Filtragem de Busca:** O agente decide quais repositórios extrair com base nos parâmetros da API de busca do GitHub.
2.  **Validação de Privacidade:** O agente "decide" manter um campo apenas se ele pertencer à lista de metadados de projeto públicos predefinidos. Se qualquer campo suspeito de conter dados pessoais for encontrado, ele é descartado no módulo `data_processor.py`.

### 3.4 Saída (Output)

A saída é um arquivo JSON estruturado contendo uma lista de objetos, onde cada objeto representa um repositório com os campos: `nome_repositorio`, `url_repositorio`, `data_criacao`, `linguagem_principal`, `licenca` (SPDX ID), `descricao_curta`, `estrelas` e `forks`.

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.9+ | Linguagem principal do agente |
| requests | 2.31.0 | Interação com a API REST do GitHub |
| python-dotenv | 1.0.1 | Gerenciamento de variáveis de ambiente e chaves de API |
| JSON | - | Formato de armazenamento e saída de dados |

### 4.2 Estrutura do código

```
ingrid-soares/projeto-1/
├── src/
│   ├── agent.py          # Orquestrador do agente
│   ├── config.py         # Configurações e parâmetros
│   ├── github_api.py     # Cliente da API do GitHub
│   ├── data_processor.py # Lógica de processamento e LGPD
│   └── utils.py          # Funções utilitárias (I/O)
├── requirements.txt      # Dependências
├── README.md             # Documentação de execução
├── documento-engenharia.md # Especificações técnicas
├── relatorio-entrega.md  # Este relatório
└── dados_projetos_open_source.json # Resultado da extração (dataset)
```

### 4.3 Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente (Opcional, para evitar rate limits)
# Edite o arquivo .env e adicione seu GITHUB_TOKEN

# 3. Executar o agente como um módulo
python -m src.agent
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Precisão da Licença | Percentual de licenças extraídas corretamente. | 100% (validação visual manual) |
| Integridade de Dados | Presença de todos os campos esperados no JSON. | 100% |
| Conformidade LGPD | Zero dados pessoais identificáveis na saída. | Sucesso (0 dados pessoais detectados) |
| Desempenho | Tempo de extração para 200 registros. | ~5 segundos |

### 5.2 Exemplos de teste

#### Teste 1: Extração Bem-Sucedida

- **Entrada:** Projetos criados desde 2024-01-01, ordenados por popularidade.
- **Saída esperada:** Lista de projetos com metadados completos e IDs de licença válidos.
- **Saída obtida:** Dataset com 200 repositórios (ex: `coze-dev/coze-studio`, `stitionai/devika`).
- **Resultado:** Sucesso

#### Teste 2: Validação de Privacidade (LGPD)

- **Entrada:** Repositórios retornados pela API (que incluem dados de proprietário/owner).
- **Saída esperada:** Saída final deve conter apenas metadados de projeto, excluindo dados de usuários (emails, etc.).
- **Saída obtida:** JSON contendo apenas informações de nível de repositório; dados pessoais de 'owners' filtrados com sucesso.
- **Resultado:** Sucesso

### 5.3 Análise dos resultados

O agente atingiu plenamente os objetivos estabelecidos. A extração de dados foi precisa e rápida, e a restrição de privacidade (LGPD) foi respeitada através de um design que prioriza a minimização de dados desde a coleta. Os pontos fortes incluem a modularidade do código e a facilidade de configuração. Um ponto de atenção é o limite secundário de taxa do GitHub, que foi contornado automaticamente pela lógica de tratamento de erros da API.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [x] Uso de ferramentas (tools) - API do GitHub
- [ ] Memória persistente
- [ ] Explicabilidade
- [x] Conformidade nativa com a LGPD (Privacy by Design)

---

## 7. Limitações e Trabalhos Futuros

As principais limitações estão ligadas aos limites de taxa da API gratuita do GitHub. Para iterações futuras, planeja-se:
1. Integrar um LLM para resumir as descrições dos projetos de forma mais rica.
2. Adicionar suporte para múltiplas fontes de dados (GitLab, Bitbucket).
3. Implementar um dashboard visual para exibir as tendências de licenças em tempo real.

---

## 8. Referências

1. GitHub API Documentation: https://docs.github.com/en/rest
2. SPDX License List: https://spdx.org/licenses/
3. Python Requests Library: https://requests.readthedocs.io/

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
