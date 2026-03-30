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
projeto-1/
├── src/
│   ├── main.py
├── data/
│   ├── ...
├── tests/
│   ├── ...
├── requirements.txt
└── README.md
```

### 4.3 Como executar

Para executar este projeto basta seguir os seguintes passos:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
export GEMINI_API_KEY=...

# 3. Executar
python src/main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
| ------- | --------- | ---------------- |
|         |           |                  |
|         |           |                  |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:**
- **Saída esperada:**
- **Saída obtida:**
- **Resultado:** Sucesso / Falha

#### Teste 2

- **Entrada:**
- **Saída esperada:**
- **Saída obtida:**
- **Resultado:** Sucesso / Falha

### 5.3 Análise dos resultados

_Discuta os resultados obtidos. O agente atingiu os objetivos? Quais foram os pontos fortes e fracos?_

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

_Descreva as limitações encontradas e o que poderia ser melhorado em iterações futuras._

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
