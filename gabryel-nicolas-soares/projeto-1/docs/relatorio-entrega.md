# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Gabryel Nicolas Soares de Sousa
> **Matrícula:** 221022570
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

O Brasil possui milhões de famílias elegíveis a benefícios sociais que deixam de recebê-los por falta de informação ou dificuldade de acesso. Este projeto propõe um agente conversacional de IA voltado à assistência social, capaz de orientar cidadãos em situação de vulnerabilidade sobre seus direitos a programas como Bolsa Família, BPC (Benefício de Prestação Continuada), Auxílio Gás, Tarifa Social de Energia e ID Jovem.

O agente coleta dados do usuário via diálogo, aplica regras legais para determinar elegibilidade e usa um modelo de linguagem local (Llama 3 via Ollama) para formatar respostas explicativas em linguagem acessível. Um módulo RAG permite responder perguntas específicas com base em documentos indexados sobre os programas sociais.

O principal resultado é um protótipo funcional que separa a lógica de decisão (regras baseadas em lei) da geração de linguagem (LLM), garantindo explicabilidade total e conformidade com a LGPD — sem armazenamento de dados entre sessões e sem uso de APIs externas pagas.

---

## 2. Combinação Atribuída

| Item | Valor |
|---|---|
| **Domínio** | Assistência Social |
| **Função do agente** | Mediação/Conversação |
| **Restrição obrigatória** | Explicabilidade Obrigatória |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe dois tipos de entrada:

- **Texto livre** digitado pelo usuário no terminal (ex: "quero verificar meus benefícios", "quais documentos preciso para o BPC?")
- **Dados estruturados** coletados interativamente durante a triagem: renda familiar mensal (float), número de pessoas na família (int), idade (int) e presença de membro com deficiência (booleano)

### 3.2 Processamento (Pipeline)

```
Usuário
   │
   ▼
Classificador de Intenção
(palavras-chave → triagem / pergunta / encerramento)
   │
   ├─── [triagem] ──► Coleta de Dados (validada)
   │                        │
   │                        ▼
   │                  Motor de Elegibilidade
   │                  (regras legais — sem LLM)
   │                        │
   │                        ▼
   │                  LLM formata resposta explicativa
   │
   ├─── [pergunta] ──► Busca RAG (base de conhecimento)
   │                        │
   │                        ▼
   │                  LLM gera resposta com contexto RAG
   │
   └─── [encerramento] ──► Descarta sessão e encerra
                                 │
                                 ▼
                          Memória de Sessão
                          (armazena contexto entre turnos)
                                 │
                                 ▼
                           Saída ao Usuário
```

### 3.3 Decisão

O agente opera em duas camadas de raciocínio:

**Camada de regras (determinística):** A elegibilidade é decidida por regras codificadas com base na legislação vigente. O LLM **não decide** quem tem direito — apenas formata a explicação.

| Benefício | Critério | Base Legal |
|---|---|---|
| Bolsa Família | Renda per capita ≤ R$ 218,00 | Lei nº 14.284/2021 |
| BPC (Idoso) | Idade ≥ 65 anos e renda per capita ≤ 1/4 salário mínimo | LOAS, Art. 20 |
| BPC (Deficiência) | Deficiência de longo prazo e renda per capita ≤ 1/4 salário mínimo | LOAS, Art. 20 §2º |
| Auxílio Gás | Renda per capita ≤ 1/2 salário mínimo | Lei nº 14.237/2021 |
| Tarifa Social de Energia | Renda per capita ≤ 1/2 salário mínimo | Lei nº 12.212/2010 |
| ID Jovem | Idade 15–29 anos e renda per capita ≤ 2 salários mínimos | Decreto nº 8.537/2015 |

**Camada de linguagem (LLM):** O Llama 3 recebe um prompt estruturado com o resultado da triagem, os motivos legais e restrições explícitas ("não invente benefícios", "cite a fonte", "use linguagem simples"). Para perguntas livres, o prompt inclui os documentos recuperados pelo RAG.

### 3.4 Saída (Output)

- **Triagem:** lista de benefícios aprovados ou negados, motivo legal para cada um, documentos necessários e orientação de onde se cadastrar
- **Pergunta:** resposta em linguagem natural com citação da fonte legal consultada
- **Erro:** mensagem de orientação ao usuário sem exposição de detalhes técnicos

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|---|---|---|
| Python | 3.11+ | Linguagem principal |
| Ollama | latest | Servidor local para o LLM |
| Llama 3 | 8B | Modelo de linguagem para geração de respostas |
| requests | 2.31+ | Chamadas HTTP à API do Ollama |
| RAG manual | — | Busca por sobreposição de termos (sem dependências externas) |

### 4.2 Estrutura do código

```
projeto-1/
├── src/
│   ├── main.py            # Loop principal, classificador e coleta de dados
│   ├── rag.py             # Base de conhecimento e busca RAG
│   └── elegibilidade.py   # Regras legais, motor de elegibilidade e LLM
├── docs/
│   ├── documento-engenharia
│   ├── relatorio-entrega
└── requirements.txt
```

### 4.3 Como executar

**Passo 1 — Instalar dependências Python**
```bash
pip install -r requirements.txt
```

**Passo 2 — Instalar o Ollama**

Acesse https://ollama.com, baixe e instale o Ollama para o seu sistema operacional. Após a instalação, o Ollama inicia automaticamente em segundo plano.

Para verificar se está funcionando:
```bash
ollama list
```

**Passo 3 — Baixar o modelo Llama 3 (apenas na primeira vez)**
```bash
ollama pull llama3
```
> ⚠️ O download é de aproximadamente 4GB. Aguarde até concluir.

**Passo 4 — Executar o agente**
```bash
python src/main.py 
```

> **Nota:** O projeto não requer chave de API nem conexão com serviços externos. Tudo roda localmente.

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Meta | Resultado obtido |
|---|---|---|---|
| Precisão de elegibilidade | % de perfis com resultado correto vs. gabarito legal | ≥ 85% | 100% (5/5 testes corretos) |
| Qualidade da explicação | Nota de 1 a 5 por avaliador | ≥ 4/5 | 4/5 |
| Latência do pipeline | Tempo do agente excluindo geração do LLM | ≤ 5s | ✅ atingida (0,00s). Tempo total com LLM: 17–47s — restrição de infraestrutura do Ollama local, fora do escopo do RNF. |
| Cobertura RAG | % de perguntas com ao menos 1 doc relevante recuperado | ≥ 80% | 100% (1/1 pergunta com doc relevante) |

### 5.2 Análise dos resultados

#### Teste 1 — Bolsa Família (aprovado)
- **Entrada:** renda R$ 800,00 / 5 pessoas / 35 anos / sem deficiência
- **Saída esperada:** Aprovado para Bolsa Família (renda per capita R$ 160,00 ≤ R$ 218,00)
- **Saída obtida:** Aprovado para Bolsa Família, Auxílio Gás e Tarifa Social de Energia com explicação dos motivos e documentos necessários. Tempo: 32,56s
- **Resultado:** Sucesso
 
#### Teste 2 — BPC Idoso (aprovado)
- **Entrada:** renda R$ 650,00 / 2 pessoas / 68 anos / sem deficiência
- **Saída esperada:** Aprovado para BPC Idoso (renda per capita R$ 325,00 ≤ R$ 353,00 e idade ≥ 65)
- **Saída obtida:** Aprovado para BPC (Idoso), Auxílio Gás e Tarifa Social de Energia com orientação de documentos e onde requerê-los. Tempo: 47,30s
- **Resultado:** Sucesso
 
#### Teste 3 — Nenhum benefício (negado)
- **Entrada:** renda R$ 4.000,00 / 2 pessoas / 40 anos / sem deficiência
- **Saída esperada:** Negado para todos os benefícios com explicação dos motivos e orientação para o CRAS
- **Saída obtida:** Negado para todos os benefícios com motivos detalhados (renda per capita R$ 2.000,00 acima dos limites) e orientação para o CRAS. Tempo: 0,00s
- **Resultado:** Sucesso
 
#### Teste 4 — BPC Deficiência (aprovado)
- **Entrada:** renda R$ 500,00 / 2 pessoas / 30 anos / com deficiência
- **Saída esperada:** Aprovado para BPC Deficiência (renda per capita R$ 250,00 ≤ R$ 353,00)
- **Saída obtida:** Aprovado para BPC (Deficiência), Auxílio Gás e Tarifa Social de Energia com documentos e locais de requerimento. Tempo: 44,71s
- **Resultado:** Sucesso
 
#### Teste 5 — Pergunta RAG
- **Entrada:** "Quais documentos preciso para o BPC?"
- **Saída esperada:** Lista de documentos com fonte citada (LOAS Art. 20)
- **Saída obtida:** Resposta com orientação sobre documentos e elegibilidade citando fontes (LOAS Lei nº 8.742/1993, Art. 20). Agente classificou corretamente como pergunta sem solicitar dados. Tempo: 17,43s
- **Resultado:** Sucesso
 
### 5.3 Análise dos resultados
 
Os 5 testes executados obtiveram resultado de sucesso, demonstrando que o motor de elegibilidade funciona corretamente. O agente identificou com precisão os benefícios aprovados e negados com base nas regras legais, sempre apresentando os motivos correspondentes.
 
O tempo de resposta variou entre 0,00s (casos negados, sem chamada ao LLM) e 47,30s (casos aprovados com geração de texto pelo Llama 3). A latência elevada nos casos aprovados é decorrente do modelo rodando localmente. A métrica de ≤ 5s foi atingida apenas nos casos negados, onde o LLM não é acionado.
 
O módulo RAG funcionou corretamente no Teste 5, classificando a pergunta como "pergunta" e recuperando documentos relevantes da base de conhecimento com citação das fontes legais.

## 6. Diferenciais implementados

- [x] RAG com base local
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [ ] Memória persistente
- [x] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

**Limitações atuais:**
- RAG por palavras-chave sem embeddings semânticos — perguntas com vocabulário diferente do índice podem não recuperar documentos relevantes
- Classificador de intenção baseado em lista de palavras-chave — sentenças ambíguas podem ser classificadas incorretamente
- Critério de deficiência por autodeclaração — a avaliação real exige laudo médico e perícia do INSS

**Trabalhos futuros:**
- Ampliar base de conhecimento com mais programas sociais municipais e estaduais
- Implementar interface web acessível
- Integrar com a API do CadÚnico para verificação automática de cadastro

---

## 8. Referências

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

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto