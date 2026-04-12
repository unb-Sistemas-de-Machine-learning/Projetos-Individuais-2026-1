# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Maciel Ferreira Custodio Júnior
> **Matrícula:** 190100087
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

Desenvolvedores que desejam contribuir com projetos open source frequentemente enfrentam dificuldade em encontrar issues adequadas ao seu nível e às suas habilidades. Este projeto implementa um agente de recomendação que recebe o username do GitHub de um desenvolvedor, coleta seus dados públicos via API, analisa o perfil com um LLM e busca issues abertas em repositórios open source compatíveis com o nível e linguagens utilizadas pelo desenvolvedor. As issues são ranqueadas por um score que combina popularidade do repositório (estrelas, forks, commits recentes, número de contribuidores) e relevância da label para o nível do desenvolvedor. O resultado é exibido em linha de comando com paginação. O principal resultado obtido é uma lista personalizada e ranqueada de oportunidades de contribuição, tornando o processo de entrada em projetos open source mais fácil.

---

## 2. Combinação Atribuída

| Item                      | Valor                      |
| ------------------------- | -------------------------- |
| **Domínio**               | Open source / comunidades  |
| **Função do agente**      | Recomendação               |
| **Restrição obrigatória** | Integração com API externa |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe como entrada o username de um perfil público do GitHub, informado pelo usuário via linha de comando.

### 3.2 Processamento (Pipeline)

![Fluxo do Agente](../assets/diagrama.png)

*Figura 1 — Fluxo de funcionamento do agente*

```
Username → [Coleta GitHub API] → [Análise LLM] → [Busca GitHub Search API] → [Enriquecimento + Score] → Ranqueamento → Issues recomendadas
```
O github_client.py coleta nome, bio, data de criação, repositórios públicos, seguidores, linguagens predominantes e pull requests do usuário. O analyzer.py envia esses dados ao Llama 3.3 via Groq e recebe nível, tipo, linguagens relevantes, resumo e keywords de contexto. O issue_finder.py usa linguagens e keywords para construir queries na GitHub Search API, enriquece cada resultado com dados do repositório, calcula um score normalizado e retorna a lista ranqueada.

### 3.3 Decisão

O agente usa o LLM em dois momentos do pipeline. Primeiro para classificar o perfil do desenvolvedor e determinar nível e tipo de atuação, e segundo para gerar keywords técnicas em inglês que descrevem a área de atuação, as quais são injetadas diretamente na query da GitHub Search API. O ranqueamento final é determinístico, calculado localmente pela normalização min-max de cinco dimensões: estrelas, forks, commits recentes, contribuidores e prioridade de label por nível.

### 3.4 Saída (Output)

Uma lista paginada de issues abertas em repositórios open source, exibida em CLI com título, repositório, labels, número de estrelas, score de relevância e link direto para a issue no GitHub.

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia              | Versão | Finalidade                              |
| ----------------------- | ------ | --------------------------------------- |
| Python                  | 3.9+   | Linguagem principal                     |
| Groq SDK                | latest | Acesso ao LLM via API                   |
| Llama 3.3 70B Versatile | -      | Análise de perfil e geração de keywords |

### 4.2 Estrutura do código

```
projeto-1/
├── assets/
│   ├── diagrama.png
├── docs/
│   ├── documento-engenharia.md
│   └── relatorio-entrega.md
├── src/
│   ├── main.py
│   ├── github_client.py
│   ├── analyzer.py
│   └── issue_finder.py
├── .gitignore
├── requirements.txt
└── README.md
```

### 4.3 Como executar

_Instruções passo a passo para rodar o projeto:_

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
# Crie um arquivo .env na raiz do projeto com:
GITHUB_TOKEN=seu_token_github
GROQ_API_KEY=sua_chave_groq

# 4. Executar
python main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica                   | Descrição                                                            | Resultado obtido                                                   |
| ------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Cobertura de resultados   | Número de issues encontradas por execução                            | 47–54 issues para perfis intermediários                            |
| Relevância das linguagens | Issues retornadas condizem com as linguagens do perfil               | Satisfatório (linguagens dominantes presentes nos repos sugeridos) |
| Classificação de nível    | LLM classifica corretamente o nível do desenvolvedor                 | Satisfatório nos testes realizados                                 |
| Ranqueamento              | Repositórios mais populares e com labels relevantes aparecem no topo | Satisfatório após correção da lógica de score                      |


### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:** macieljuniormax
- **Saída esperada:** Issues em JavaScript, Ruby ou TypeScript de repositórios ativos, preferencialmente com labels `bug` ou `enhancement`
- **Saída obtida:** 51 issues, topo com `anomalyco/opencode` (132k estrelas, bug) e `microsoft/vscode` (183k estrelas, feature-request)
- **Resultado:** Sucesso

#### Teste 2

- **Entrada:** torvalds
- **Saída esperada:** Issues em C de repositórios relevantes para sistemas, kernel ou embedded
- **Saída obtida:** 36 issues, predominância de repositórios C com contexto técnico adequado
- **Resultado:** Sucesso
### 5.3 Análise dos resultados

O agente atingiu o objetivo principal de recomendar issues personalizadas com base no perfil do desenvolvedor. O ponto mais forte é a combinação entre análise via LLM e ranqueamento por popularidade, que faz com que repositórios reconhecidos apareçam no topo para perfis compatíveis. O ponto mais fraco é a dependência da qualidade dos keywords gerados pelo LLM, que pode variar entre execuções e impactar a quantidade de resultados retornados. Repositórios com zero estrelas ainda aparecem ocasionalmente, indicando que um filtro mínimo de popularidade seria benéfico. O tempo de resposta do sistema está um pouco elevado, dado que para cada issue encontrada são feitas múltiplas chamadas à API do GitHub para enriquecer os dados do repositório.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [x] Uso de ferramentas (tools)
- [ ] Memória persistente
- [ ] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

A principal limitação atual é a variabilidade dos keywords gerados pelo LLM, que em algumas execuções retorna termos muito genéricos ou muito restritivos, impactando diretamente a quantidade e qualidade das issues encontradas. Além disso, o tempo de execução é significativo devido ao volume de chamadas sequenciais à API do GitHub para enriquecer cada repositório candidato, o que pode ser melhorado em versões futuras.

Para iterações futuras, os principais pontos de melhoria são: implementar filtro de estrelas mínimas por nível de desenvolvedor, adicionar interface web para facilitar o uso, implementar memória persistente para guardar o histórico de issues já visualizadas pelo usuário, e explorar o uso de múltiplos agentes onde um agente especializado avalie a qualidade de cada issue individualmente antes de incluí-la nos resultados.

---

## 8. Referências

1. GitHub REST API Documentation — https://docs.github.com/en/rest
2. Groq API Documentation — https://console.groq.com/docs
3. Meta Llama 3.3 — https://ai.meta.com/blog/meta-llama-3

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
