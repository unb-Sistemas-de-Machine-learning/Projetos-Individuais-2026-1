# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Carlos Henrique Souza Bispo
> **Matrícula:** 211061529
> **Data de entrega:** 25/03/2026

---

## 1. Resumo do Projeto

Este projeto implementa um agente de IA para classificação de risco de evasão estudantil no domínio de Educação. O sistema recebe dados acadêmicos e um relato textual do estudante, calcula um score de risco e retorna uma classe (baixo, moderado ou alto) com explicação obrigatória. A explicabilidade é garantida em todas as respostas por meio de fatores que impactaram a decisão e recomendações práticas para intervenção da coordenação. A arquitetura foi construída como pipeline sequencial com validação de entrada, extração de features, motor de decisão e módulo de explicação. O agente suporta integração opcional com LLM (OpenAI) para enriquecer justificativas e possui fallback local determinístico para manter operação mesmo sem API key. O resultado principal foi a construção de um protótipo funcional, com testes automatizados e casos de avaliação que demonstram consistência entre entradas de maior vulnerabilidade e classificações de risco mais elevadas.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Educação |
| **Função do agente** | Classificação |
| **Restrição obrigatória** | Explicabilidade obrigatória |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe um objeto JSON com os campos:

- `frequencia` (0-100)
- `nota_media` (0-10)
- `acessos_plataforma_semana` (inteiro)
- `pendencia_financeira` (booleano)
- `relato_estudante` (texto curto)

### 3.2 Processamento (Pipeline)

Pipeline implementado:

```
Entrada JSON
→ validação de domínio dos campos
→ extração de sinais de risco (numéricos + texto)
→ cálculo do score de risco
→ classificação por thresholds
→ geração de explicação + recomendações
→ saída estruturada em JSON
```

### 3.3 Decisão

Lógica de decisão:

1. Cada variável recebe peso conforme impacto esperado no risco de evasão.
2. O relato textual é analisado por palavras-chave de vulnerabilidade e engajamento.
3. O score final (0-100) é mapeado para classes:
	- `0-39`: baixo
	- `40-69`: moderado
	- `70-100`: alto
4. A explicação é gerada por dois modos:
	- Modo LLM: prompt estruturado para justificar a decisão com linguagem clara.
	- Modo fallback local: template determinístico com fatores e ações sugeridas.

### 3.4 Saída (Output)

Saída em JSON com:

- `nivel_risco`
- `score_risco`
- `fatores_risco`
- `fatores_protecao`
- `explicacao`
- `acoes_recomendadas`

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.10+ | Linguagem principal |
| OpenAI SDK | 1.0+ | Geração opcional de explicações com LLM |
| unittest | stdlib | Testes automatizados |

### 4.2 Estrutura do código

```
Projeto-01/
├── src/
│   ├── agent.py
│   └── main.py
├── data/
│   └── test_cases.json
├── tests/
│   └── test_agent.py
├── requirements.txt
└── README.md
```

### 4.3 Como executar

```bash
# 1. Entrar na pasta do projeto
cd Projeto-01

# 2. (Opcional) criar ambiente virtual
python -m venv .venv
# Windows
.venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. (Opcional) habilitar LLM
set OPENAI_API_KEY=sua_chave

# 5. Rodar exemplo principal
python src/main.py

# 6. Rodar testes
python -m unittest discover -s tests -v
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Acurácia de classificação (amostra sintética) | Percentual de acerto da classe em 5 casos | 100% (5/5) |
| Cobertura de explicação | Saídas com justificativa textual | 100% |
| Estabilidade sem API key | Execuções concluídas no fallback local | 100% |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:** frequência 45, nota 4.2, 1 acesso/semana, pendência financeira true, relato de desmotivação
- **Saída esperada:** risco alto
- **Saída obtida:** risco alto
- **Resultado:** Sucesso

#### Teste 2

- **Entrada:** frequência 88, nota 8.1, 7 acessos/semana, sem pendência, relato positivo
- **Saída esperada:** risco baixo
- **Saída obtida:** risco baixo
- **Resultado:** Sucesso

### 5.3 Análise dos resultados

O agente atingiu o objetivo principal de classificar risco e justificar decisões de forma transparente. O ponto forte é a explicabilidade obrigatória, entregue mesmo sem dependência de API externa. Outro ponto positivo é a estrutura modular, que facilita evolução do motor de decisão. A calibração de regras nesta versão elevou a acurácia no conjunto sintético para 5/5. Como limitação, o conjunto de validação ainda é pequeno e sintético; para uso real, é necessário calibrar pesos e thresholds com dados históricos da instituição.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [x] Uso de ferramentas (tools)
- [ ] Memória persistente
- [x] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

Limitações atuais:

- Regras e pesos definidos heurísticamente, sem ajuste estatístico com base real.
- Avaliação com base sintética reduzida.
- Módulo LLM depende de conectividade e custo por token.

Trabalhos futuros:

- Treinar/calibrar modelo de risco com histórico real anonimizado.
- Adicionar dashboard para priorização de atendimentos.
- Incluir trilha temporal para comparar evolução do aluno semana a semana.

---

## 8. Referências

1. OpenAI API Reference. https://platform.openai.com/docs
2. OECD (2023). Student retention and early warning systems in education.
3. Python Software Foundation. unittest documentation.

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto
