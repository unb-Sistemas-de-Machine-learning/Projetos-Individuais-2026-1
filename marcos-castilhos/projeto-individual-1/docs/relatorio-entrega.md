# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Marcos Antonio Teles de Castilhos <br>
> **Matrícula:** 221008300 <br>
> **Data de entrega:** 30/03/2026

### 1. Resumo do Projeto

Este projeto desenvolve um sistema multi-agente de IA para triagem automatizada de demandas de zeladoria urbana. Para cumprir a restrição estrita de "Baixo Custo", a arquitetura terceirizou o processamento para a nuvem via API do Groq (utilizando o modelo leve Llama 3 8B). O sistema recebe relatos ruidosos em linguagem natural, passa por um Agente Auditor focado em riscos à saúde/segurança, e repassa o contexto para um Agente Despachante que devolve um objeto JSON tipado. O pipeline processou 51 casos de teste, demonstrando alta resiliência de parsing e uma acurácia global de 72,55% na classificação estrita.

### 2. Combinação Atribuída

| **Item**	| **Valor** |
| --- | --- |
| Domínio |	Participação cidadã (3)|
| Função do agente	| Classificação (1)
| Restrição obrigatória	| Baixo custo (2) |

### 3. Modelagem do Agente
#### 3.1 Entrada:

String textual contendo relatos desestruturados do cidadão.
#### 3.2 Processamento:

Input String → Agente 1 (Prompt Auditoria) → Output Agente 1 + Input Original → Agente 2 (Prompt Taxonomia + JSON Format) → Output JSON parseado.
#### 3.3 Decisão:

O sistema "pensa" dividindo a carga cognitiva. O Agente 1 foca exclusivamente na identificação de anomalias críticas (risco de morte, doenças ou acidentes). O Agente 2 recebe esse parecer e atua como um roteador rigoroso, aplicando as regras de negócio do município (ex: priorizando o risco sanitário sobre a estética urbana) e enquadrando o problema na taxonomia permitida.

#### 3.4 Saída:

Objeto JSON contendo as chaves mapeadas (categoria, urgencia, resumo_problema, explicacao).

### 4. Implementação
#### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
| --- | --- | --- |
| Python | 3.12+  |	Linguagem principal do projeto. |
| Groq SDK	| 0.x	| Cliente oficial para inferência na API em nuvem (modelo Llama 3 8B). |
| python-dotenv	| 1.x	| Gerenciamento seguro de variáveis de ambiente (API Keys). |
| json (Built-in) |	-	| Parsing nativo e estruturação das saídas do LLM. |
| csv (Built-in) | - | Persistência local de dados para avaliação do Ground Truth. |

#### 4.2 Estrutura do código

#### projeto-individual-1/
    ├── src/ <br>
        └── main_gemini.py             # Implementação do projeto utilizando a API do Google
        └── main_groq.py               # Implementação do projeto utilizando a API do Groq
    ├── docs/
        └── avaliacoes.csv             # Log de execução e base para cálculo de acurácia
        └── avaliacoes_corrigido.xlsx  # Ground truth com avaliação humana e contagem de erros.
    ├── templates/
        ├── documento-engenharia.md # Documentação de requisitos
        └── relatorio-entrega.md    # Relatório final de execução
        ├── .env.example            # Template seguro para as chaves de API
    ├── requirements.txt            # Dependências do projeto
    └── README.md                   # Descrição geral do repositório
### 5. Avaliação e Testes

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
| **Acurácia Global** | Taxa de acerto conjunto (Categoria correta + Urgência correta) em relação ao Ground Truth humano. | **72,55%** (37 acertos em 51 testes). |
| **Taxa de Sucesso (Parsing)** | Frequência em que o Agente Despachante retornou um JSON válido, sem quebrar o sistema. | **100%** (51/51). O modelo seguiu o schema perfeitamente. |
| **Custo por Inferência** | Custo financeiro para rodar os 51 testes duplos (102 requisições no total). | **R$ 0,00**. Restrição de Baixo Custo (RNF01) atingida via tier gratuito (Groq/Llama3). |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:**
    *'não vi acidente ainda mas alguém vai se machucar naquela curva sem placa'*
- **Saída esperada:** *Risco potencial*; <br>Categoria: Transito;<br>Urgencia: Média;<br>Resumo: Curva sem placa;<br> Explicação: Risco latente, no entanto, não iminente.

- **Saída obtida:** *Sem risco iminente*; 
  <br>"categoria": "Trânsito",<br>
  "urgencia": "Média",<br>
  "resumo_problema": "Curva sem placa",<br>
  "explicacao": "Risco de acidente, mas sem risco iminente, conforme Parecer do Auditor"<br>
- **Resultado:** Sucesso

#### Teste 2

- **Entrada:** *'a água da torneira está saindo com cor estranha hoje'*
- **Saída esperada:** *Sem risco iminente.*
- **Saída obtida:** *Sem risco iminente.*
  <br>"categoria": "Saneamento",
  <br>"urgencia": "Média",
  <br>"resumo_problema": "Água da torneira estranha",
  <br>"explicacao": "A água da torneira está saindo com cor estranha, o que pode indicar problemas de tratamento ou infraestrutura, mas não há risco imediato à saúde pública."

- **Resultado:** Sucesso

#### 5.3 Análise dos resultados (O Ponto Crítico)

O sistema foi submetido a uma bateria de 51 testes empíricos. O pipeline alcançou 100% de sucesso no RNF02 (estabilidade de parsing JSON), provando que a imposição de formato funcionou.

Na acurácia categórica e de urgência, o sistema obteve 37 acertos em 51 casos, resultando em 72,55% de acurácia global. A análise manual do log exportado em CSV revelou que os erros não foram aleatórios. O modelo Llama 3 8B, por ser um LLM menor e mais leve, demonstrou dificuldade semântica em intersecções de domínio (ex: classificar um buraco escondido sob a água como "Saneamento" em vez de "Infraestrutura"). Além disso, o projeto enfrentou instabilidade de infraestrutura de terceiros: inicialmente projetado para a API do Google (Gemini), o pipeline sofreu throttling (Erro 503 UNAVAILABLE) sob a carga de testes sequenciais, forçando uma adaptação arquitetural pragmática para a API do Groq.

### 6. Diferenciais implementados

    [x] Múltiplos agentes (Pipeline com Agente Auditor e Agente Despachante).

    [x] Análise crítica de limitações (Discussão sobre a acurácia de 72,55% e o limite de raciocínio de LLMs menores).

### 7. Limitações e Trabalhos Futuros

A limitação intrínseca deste projeto reside na dependência de infraestruturas de nuvem gratuitas que não possuem SLA de disponibilidade (evidenciado pelo erro 503 enfrentado na etapa de testes). Além disso, a arquitetura atual confia inteiramente no conhecimento paramétrico de um modelo de 8 bilhões de parâmetros para entender regras de posturas municipais. Em iterações futuras, o sistema pode implementar o padrão de Circuit Breaker para tolerância a falhas de API e acoplar um módulo RAG para basear as decisões do Agente 2 no código de leis do município específico, elevando a precisão para além da barreira dos 72%.