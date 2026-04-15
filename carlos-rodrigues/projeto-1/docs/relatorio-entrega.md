# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Carlos Eduardo Rodrigues
> **Matrícula:** 221031265
> **Data de entrega:** 29/03/2026

---

## 1. Resumo do Projeto

Este projeto implementa um agente de IA para detectar possíveis inconsistências em textos de licitações públicas. O problema abordado é a dificuldade de triagem manual de grandes volumes de documentos textuais com qualidade heterogênea.

O agente foi desenvolvido em Python e utiliza a API do Gemini por meio da biblioteca google-genai, com modelo padrão Gemini 2.5 Flash. O pipeline segue a estrutura: entrada JSON -> pré-processamento -> análise por LLM -> regras heurísticas -> saída estruturada.

O principal resultado foi a entrega de um protótipo funcional, modular e reprodutível, capaz de processar registros e gerar saída padronizada para apoio à auditoria humana.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | 4 - Compras públicas |
| **Função do agente** | 9 - Detecção de anomalias |
| **Restrição obrigatória** | 8 - Integração com API externa (Gemini) |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe registros em JSON no formato:

```json
[
	{
		"Texto_encontrado": "...",
		"Data": "YYYY-MM-DD",
		"Municipio": "..."
	}
]
```

Cada registro é analisado individualmente.

Origem dos dados:
- Os dados extraídos utilizados neste projeto foram obtidos do repositório Licitaiba: https://github.com/unb-mds/2023-2-Squad04/
- O projeto "Licitaiba - Extrator de Licitações do Diário Oficial da Paraíba" trata-se de uma iniciativa para automatizar a coleta e o acompanhamento de informações sobre licitações públicas no estado da Paraíba.

### 3.2 Processamento (Pipeline)

Etapas implementadas:

```text
Entrada JSON
	-> preprocess_text(texto)
	-> extract_features(texto, data_referencia)
	-> evaluate_hard_rules(features)
	-> call_llm(texto, features)
	-> apply_rules(texto, resultado_llm, features)
	-> Saída estruturada
```

- preprocess_text: remove espaços extras e normaliza o texto.
- extract_features: identifica modalidade, valor, limite legal, proximidade do limite e sinais de incerteza.
- evaluate_hard_rules: aplica decisão determinística para violações claras (ex.: dispensa acima do limite).
- call_llm: envia prompt com contexto legal e features estruturadas para reduzir alucinações.
- apply_rules: combina risco do LLM com score heurístico.

### 3.3 Decisão

A lógica de decisão combina regras determinísticas + LLM:

1. O agente extrai features e tenta decidir com regras objetivas + LLM.
2. Quando não há decisão forte, o Gemini avalia o texto com base em contexto legal e sinais extraídos.
3. O resultado final combina score, categoria e nível de risco de forma conservadora.

O prompt orienta explicitamente a detecção de:
- inexigibilidade suspeita
- aditivos
- valores altos
- descrições vagas
- e evita inferência de irregularidade quando há dados insuficientes

### 3.4 Saída (Output)

Formato da saída por registro:

```json
{
	"tem_anomalia": true,
	"nivel_risco": "baixo|medio|alto",
	"categoria": "legal|financeiro|documental|descritivo",
	"tipo": "string",
	"justificativa": "string",
	"confianca": 0.0
}
```

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.14.3 | Linguagem principal |
| google-genai | 0.8.0+ | Integração com API Gemini |
| python-dotenv | 1.0.1+ | Carregamento de variáveis de ambiente |

### 4.2 Estrutura do código

```
projeto-1/
├── .env.example
├── .gitignore
├── requirements.txt
├── data/
│   └── data.json
│   ├── data_small.json
├── src/
│   ├── agent.py
│   ├── config.py
│   └── main.py
└── docs/
	├── documento-engenharia.md
	└── relatorio-entrega.md
```

### 4.3 Como executar

_Instruções passo a passo para rodar o projeto:_

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# editar .env e inserir GEMINI_API_KEY

# 3. Executar
python src/main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| Cobertura de schema | % de respostas com 6 campos obrigatórios (tem_anomalia, nivel_risco, categoria, tipo, justificativa, confianca) | 100% |
| Latência média | Tempo médio por licitação processada | 12.893s |

### 5.2 Exemplos de teste

#### Teste com 3 registros

- **Entrada:** `data/data_small.json` com 3 registros de 2026
- **Saída esperada:** classificação conservadora, sem acusação automática de irregularidade por proximidade de limite ou falta de dados
- **Saída obtida:**

```json
=== Registro 1 ===
Municipio: Água Branca
Data: 2026-03-26
Saida estruturada:
{
	"tem_anomalia": false,
	"nivel_risco": "baixo",
	"categoria": "legal",
	"tipo": "Conformidade com limites legais",
	"justificativa": "O valor da contratação (R$ 19.200,00) está significativamente abaixo do limite legal para dispensa por valor (R$ 65.492,11, conforme Art. 75, II da Lei nº 14.133/2021 para 2026). O objeto é específico e não foram identificados sinais de fracionamento ou proximidade com o limite legal. A ausência de justificativa detalhada no extrato, por si só, não configura anomalia conforme as regras estabelecidas.",
	"confianca": 1.0
}

=== Registro 2 ===
Municipio: Areia de Baraúnas
Data: 2026-03-25
Saida estruturada:
{
	"tem_anomalia": false,
	"nivel_risco": "baixo",
	"categoria": "legal",
	"tipo": "Proximidade ao limite legal e agrupamento de itens diversos",
	"justificativa": "O valor da contratação (R$ 60.000,00) por dispensa de licitação, com base no Art. 75, inciso II, da Lei 14.133/21, encontra-se próximo ao limite legal atualizado de R$ 65.492,11 para o ano de 2026. Embora a proximidade ao limite não seja, por si só, uma anomalia, a natureza do objeto, que inclui o fornecimento de diversos materiais permanentes distintos (televisão, impressora, notebook, cadeira de escritório, armário e mesa) em uma única contratação, pode indicar a necessidade de verificação. Recomenda-se analisar a justificativa para o agrupamento desses itens sob uma única dispensa, a fim de assegurar a busca pela proposta mais vantajosa e a adequação da modalidade de contratação, sem que isso configure, necessariamente, um fracionamento. Proximidade com limite legal, isoladamente, nao configura anomalia.",
	"confianca": 0.85
}

=== Registro 3 ===
Municipio: Água Branca
Data: 2026-03-24
Saida estruturada:
{
	"tem_anomalia": false,
	"nivel_risco": "medio",
	"categoria": "financeiro",
	"tipo": "Verificação de limites de adesão à Ata de Registro de Preços (ARP)",
	"justificativa": "O extrato do contrato indica adesão à Ata de Registro de Preços (ARP) com fundamento no Art. 86, §§ 2º e 3º da Lei nº 14.133/2021. O § 3º do referido artigo estabelece que as aquisições ou contratações adicionais por adesão não poderão exceder, por órgão ou entidade, a 50% dos quantitativos dos itens registrados na ARP. O extrato não fornece informações sobre os quantitativos totais da Ata de Registro de Preços nº 03/2025 ou os quantitativos específicos desta adesão, impossibilitando a verificação da conformidade com o limite legal. Requer-se a análise dos documentos complementares do processo para confirmar o atendimento a este requisito.",
	"confianca": 0.8
}
```

- **Resultado:** Sucesso

### 5.3 Análise dos resultados

O agente atingiu o objetivo de estruturar uma triagem inicial de risco para documentos de licitação em português. Como pontos fortes, destacam-se a modularidade do código, uso de API real do Gemini, padronização da saída e combinação de IA com regras explícitas.

Como limitações, a qualidade da resposta depende da redação do documento original e da variabilidade do modelo.

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

Limitações:
- Dependência da disponibilidade e latência da API externa.
- Sensibilidade a textos muito curtos, ruidosos ou incompletos.
- Heurísticas simples.

Trabalhos futuros:
- Incluir regras adicionais (fracionamento, repetição de fornecedores, datas incoerentes).
- Adicionar armazenamento dos resultados em arquivo para auditoria.
- Otimizar latência das chamadas ao LLM (redução de prompt).

---

## 8. Referências

1. Google AI for Developers. Gemini API Documentation.
2. Repositório de extração dos dados: https://github.com/unb-mds/2023-2-Squad04/ (Licitaiba - Extrator de Licitações do Diário Oficial da Paraíba).

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
