# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** André Emanuel Bispo da Silva
> **Matrícula:** 221007813
> **Data de entrega:** 29/3/2026

---

## 1. Resumo do Projeto

Este projeto é um protótipo de um script que automatiza a separação de um projeto de software
em módulos, automatizando uma das tarefas de organização de código. O escopo do protótipo trata
apenas de arquivos python.

---

## 2. Combinação Atribuída

| Item                      | Valor |
| ------------------------- | ----- |
| **Domínio**               | 10    |
| **Função do agente**      | 1     |
| **Restrição obrigatória** | 2     |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

A estrutura do projeto, junto com o código fonte dos arquivos

### 3.2 Processamento (Pipeline)

```
Usuário -> Comando -> upload do projeto -> Análise do projeto -> Sugestão de estrutura de módulos -> Geração de script
-> Revisão do usuário -> Confirmação do usuário -> Execução do script -> Projeto organizado em módulos
```

### 3.3 Decisão

É utilizado um prompt injetado com a estrutura do projeto em formato json
e o conteúdo de cada arquivo fonte python: "
You are a senior Python software architect.

Given these Python files:

[[ARQUIVOS]]

Split them into multiple modules.

Rules:

- Each module must have a single responsibility
- Keep behavior unchanged
- DO NOT invent new logic
- Only reorganize existing code
- Include necessary imports
- Output COMPLETE, runnable Python files

Return ONLY a bash script (NO markdown, must be directly runnable) that will apply the required modifications
"

### 3.4 Saída (Output)

- Um script que efetua a separação dos módulos, de forma que possa ser revisado antes de executar

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade                         |
| ---------- | ------ | ---------------------------------- |
| Python     | 3.10   | Linguagem de programação           |
| API Gemini | -      | Processamento de linguagem natural |

### 4.2 Estrutura do código

```
.
├── documento-engenharia.md
├── relatorio-entrega.md
└── src
    ├── ai_client.py
    ├── discovery.py
    ├── .gitignore
    ├── main.py
    ├── modules_plan.sh
    ├── requirements.txt
    └── test1
        ├── output
        │   ├── modules_plan.sh
        │   └── test1
        │       ├── __init__.py
        │       ├── main.py
        │       ├── parser.py
        │       ├── tokenizer.py
        │       └── tokens.py
        └── parser.py
```

### 4.3 Como executar

Para executar este projeto basta seguir os seguintes passos:

```bash
# 1. Instalar dependências
pip install -r src/requirements.txt

# 2. Configurar variáveis de ambiente
export GEMINI_API_KEY=...

# 3. Executar
python src/main.py --help
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
| ------- | --------- | ---------------- |
|         |           |                  |
|         |           |                  |

### 5.2 Exemplos de teste

#### Teste 0

- **Entrada:** Este próprio projeto
- **Saída esperada:** Um projeto modularizado sem alterações em comportamento após a execução do script
- **Saída obtida:** Projeto modularizado com mesmo comportamento
- **Resultado:** Sucesso

#### Teste 1

- **Entrada:** Analisador sintático recursivo descendente (de minha autoria) de pré requisitos do sigaa
- **Saída esperada:** Um Analisador sintático dividido em módulos com o mesmo comportamento
- **Saída obtida:** Um analisador sintático em um pacote dividido em vários módulos
- **Resultado:** Sucesso

### 5.3 Análise dos resultados

De acordo com os testes feitos a LLM ainda tem uma tendência de modificar um pouco o código,
e é um pouco inconsistente no jeito de efetuar as alterações pelo script. Mas o script é legível
e permite um preview das mudanças antes da confirmação, e a modularização é aceitável.

---

## 6. Diferenciais implementados

_Marque os diferenciais que foram implementados:_

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [ ] Memória persistente
- [ ] Explicabilidade
- [ ] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

As limitações deste trabalho são principalmente quanto e evitar a LLM de modificar o comportamento do código
E limitações de tamanho do projeto. Como a LLM precisa do código fonte inteiro para poder corretamente colocar
imports e dependências nos scripts separados o script fica muito limitado quando o projeto é de maior escala.
Uma consideração possível seria gerar um grafo de dependências entre os scripts, apenas com os símbolos a fim
de diminuir o tamanho do prompt.

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
