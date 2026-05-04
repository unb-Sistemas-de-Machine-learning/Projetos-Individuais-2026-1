# Detalhes Técnicos: Engenharia de ML e Arquitetura de Sistemas (Projeto 2)

Este documento consolidado provê uma visão técnica aprofundada sobre a implementação, arquitetura de sistemas e os desafios enfrentados no desenvolvimento do pipeline do Projeto 2, servindo como base de conhecimento para manutenção, auditoria técnica e estudos futuros.

---

## 1. Engenharia de Dados (Pipeline de Ingestão e Pré-processamento)

A etapa de ingestão de dados para o dataset `CICIDS2017` é o pilar fundamental que garante a estabilidade numérica e a capacidade de generalização do sistema de detecção de anomalias.

**Desafios da Carga:**  
O dataset original possui uma estrutura de dados de tráfego de rede capturada em condições reais, o que introduz um nível elevado de ruído estatístico e inconsistências estruturais.

**Padronização de Schema:**  
Observou-se que o dataset original contém nomes de colunas com espaços ocultos ou caracteres não imprimíveis (ex: `" Source Port"`), que impedem a indexação correta pelo `pandas`.  
Implementamos o módulo `clean_column_names` utilizando `str.strip()` para sanear todos os rótulos de colunas, garantindo que o mapeamento de features seja executado sem exceções.

**Sanitização Numérica:**  
Dados de rede frequentemente contêm divisões por zero ou estados de conexão mal terminados, resultando em valores `np.inf`.  
Aplicamos a substituição sistemática desses valores por `np.nan`, seguida de uma limpeza estrutural com `dropna()`. Este procedimento é vital para evitar que o algoritmo `IsolationForest` apresente divergência matemática durante o cálculo do caminho médio de isolamento das árvores de decisão.

**Modularidade e Reprodutibilidade:**  
Todo o fluxo de processamento é encapsulado em `src/ids/data_preprocessing.py`, garantindo que o dataset de treino seja consistente e reprodutível.  
A modularidade permite que cada sub-etapa (limpeza, normalização, particionamento) seja auditada e testada individualmente sem afetar o restante do pipeline.

**Performance e I/O:**  
Embora a implementação atual utilize o formato `csv` para maior compatibilidade de leitura e depuração, o sistema está desenhado para migração futura para `parquet`.  
O `parquet` é uma escolha superior para este volume (milhares de registros), oferecendo compressão columnar e leitura seletiva, reduzindo drasticamente o tempo de I/O em ambientes de alta carga.

**Conceito Chave:**  
O *Data Cleaning* rigoroso em séries temporais de rede não é apenas um requisito funcional, mas uma necessidade de segurança.  
Ruídos não tratados podem ser interpretados pelo modelo como sinais de ataques reais, aumentando a taxa de falsos positivos (FPR) e causando fadiga de alertas na equipe de SOC.

---

## 2. Modelagem de Segurança

A estratégia de modelagem foi dividida em dois eixos complementares: detecção de anomalias estatísticas para tráfego bruto (IDS) e processamento de linguagem natural (NLP) para análise de intenção em URLs maliciosas.

### 2.1 Módulo IDS (Detecção de Anomalias)

**Status:** **Validado e Funcional**  
O pipeline de treinamento está em produção local, integrado com *Logging* automatizado.

**Modelo:** *IsolationForest* (Aprendizado Não Supervisionado)  
A escolha baseia-se na premissa de que anomalias (ataques de varredura ou intrusão) são casos "raros e diferentes" no espaço de features.  
Diferente de algoritmos supervisionados que requerem rótulos exatos (muitas vezes indisponíveis em cenários de ataques zero-day), este modelo isola os registros através de subdivisões randômicas do espaço de atributos.  
Ataques como o *Port Scanning* alteram o comportamento típico de pacotes (frequência e flags de sinalização), permitindo que o modelo os isole rapidamente em níveis profundos das árvores de decisão.

**Configuração e Hiperparâmetros:**  
O parâmetro `contamination=0.01` foi definido após análise empírica do dataset, isolando efetivamente o top 1% do comportamento da rede como potencialmente anômalo.  
A reprodutibilidade do estado estocástico é garantida pela semente `random_state=42`, essencial para experimentos comparáveis no MLflow.

**Instrumentação:**  
Adicionamos um *logger* de métricas customizado (`n_anomalies`, `n_normal`) via `mlflow.log_metric`.  
Esta camada de instrumentação é crucial para observar como variações no parâmetro de contaminação impactam a detecção, permitindo que a equipe de engenharia identifique a zona de operação ótima do IDS.

---

### 2.2 Módulo Phishing (NLP)

**Status:** **Em desenvolvimento** (Pipeline e base de treino validados)

**Abordagem:**  
*Fine-tuning* do modelo `DistilBERT` (Hugging Face) utilizando a `Trainer` API, que abstrai a complexidade do loop de otimização de gradientes.

**Fundamentação:**  
O phishing moderno utiliza técnicas avançadas de ofuscação (URL shorteners, typosquatting) que fogem de filtros baseados em listas negras.  
O uso de Deep Learning é mandatório para detectar padrões semânticos na URL.

**Componentes:**
- `data_preprocessing.py`: Responsável pela limpeza do corpus e tokenização via `DistilBertTokenizer`.
- `model_training.py`: Orquestra o treinamento do modelo `DistilBertForSequenceClassification`, inicializando a cabeça de classificação binária.

**Por que DistilBERT?**  
Escolhido por oferecer um equilíbrio ideal entre performance (baixa latência de inferência) e precisão, sendo ideal para sistemas que exigem resposta em tempo real.

## 3. Arquitetura de ML Systems (MLOps)

O sistema foi estruturado para suportar o ciclo de vida completo (*Model Life Cycle*):

**Rastreabilidade (MLflow Tracking):**  
Funciona como a central de comando. Armazenar modelos (`log_model`) e métricas (`log_metric`) garante que qualquer experimento possa ser auditado meses depois, essencial para conformidade e melhoria contínua.  
Cada execução captura o estado exato dos dados e do código, evitando a perda de conhecimento.

**Reprodutibilidade:**  
O uso de `pyenv` (Python 3.10.12) é vital. Bibliotecas como `transformers` e `torch` dependem de versões específicas de compiladores e bibliotecas C++, que mudam drasticamente entre versões do Python.  
O `requirements.txt` rigoroso garante que o ambiente seja o mesmo em qualquer máquina, eliminando o "Dependency Hell".

**Observabilidade:**  
A `mlflow ui` atua como painel de controle, permitindo que a equipe inspecione artefatos e compare métricas em tempo real, facilitando a decisão de qual modelo está apto para subir para o ambiente de produção.

**Escalabilidade:**  
A separação entre treinamento e inferência permite que o pipeline cresça organicamente.  
A inclusão futura de `parquet` facilitará o processamento de terabytes de logs de rede sem sobrecarregar a memória do servidor de inferência.

**Integração Contínua:**  
Embora simplificado nesta versão, o pipeline é modular o suficiente para ser inserido em esteiras de CI/CD, onde cada novo commit dispara testes de regressão no modelo, garantindo que novas funcionalidades não quebrem o IDS ou o Phishing Detector.

---

## 4. Conceitos Fundamentais

**Data Drift:**  
Fenômeno que ocorre quando as propriedades estatísticas dos dados de entrada mudam ao longo do tempo (ex: novos protocolos de rede, novos padrões de ataque).  
O sistema requer monitoramento contínuo para evitar a obsolescência do modelo.  
O *Data Drift* é um dos principais motivos de falhas silenciosas em sistemas de ML em produção, pois o modelo continua fazendo predições, mas com acurácia degradada.

**Tokenização:**  
Processo técnico de converter texto bruto (URLs ou logs) em IDs numéricos que os modelos *Transformer* conseguem processar como tensores.  
Esta etapa é o alicerce para a extração de características semânticas em modelos de Deep Learning, permitindo que a máquina entenda a relação espacial e hierárquica entre caracteres em uma URL.

**Fine-tuning (Transfer Learning):**  
Técnica de ajustar os pesos internos de um modelo previamente treinado em um dataset genérico para uma tarefa específica de nicho.  
Ao realizar fine-tuning do `DistilBERT` com nossos dados de Phishing, poupamos semanas de treinamento computacional enquanto especializamos o modelo na sintaxe maliciosa.

**Guardrails (Segurança de Entrada):**  
Camadas de proteção lógicas aplicadas *antes* da inferência real.  
Incluem validação de schema (ex: via `pydantic` para garantir que o input seja um IP ou URL válido), o que é vital para evitar *adversarial attacks* que tentam injetar lixo nos modelos.

**Bias vs Variance Trade-off:**  
Equilíbrio central na modelagem.  
No IDS, o ajuste de `contamination` controla o trade-off entre capturar todos os ataques (alta variância/recall) ou manter poucos falsos positivos (alto viés/precisão).

**Offline vs Online Inference:**  
Nossa arquitetura suporta ambos.  
O processamento de logs históricos via CSV/Parquet é offline (Batch), enquanto a inferência via script (`inference.py`) prepara o terreno para um sistema de predição online (streaming).

**Feature Importance:**  
Em modelos de segurança, é essencial saber qual variável (ex: tamanho de payload ou flag TCP) pesou mais na decisão de "anomalia".  
O *Isolation Forest* nos permite inferir, indiretamente, a importância das variáveis analisadas no isolamento dos pontos.

**Batch Normalization (Conceito de Rede Neural):**  
Técnica usada no *DistilBERT* para estabilizar o aprendizado ajustando a média e variância de cada camada, essencial para evitar o *Vanishing Gradient Problem*.

**Overfitting:**  
O pesadelo do MLOps.  
Ocorre quando o modelo memoriza o dataset de treinamento e perde a capacidade de generalização.  
Nosso uso de `random_state=42` e `val_data` (em desenvolvimento) serve justamente para detectar isso.

**Latência de Inferência:**  
O tempo decorrido desde a recepção da URL até o retorno da classificação.  
Em sistemas de rede, cada milissegundo conta, por isso a escolha do `DistilBERT` (modelo menor) em vez de `BERT-Large` (modelo pesado).

---

## 5. Comandos Fundamentais de Operação e Automação

A operação de um pipeline de ML em ambiente de cibersegurança exige comandos que garantam a integridade dos artefatos, a reprodutibilidade dos experimentos e a manutenção do ciclo de vida do modelo.

**`mlflow ui` (Observabilidade em Tempo Real):**  
Inicia o servidor local do MLflow que gerencia o registro de artefatos.  
Este comando não é apenas para visualização; ele expõe a API do MLflow, permitindo que o `model_training.py` registre métricas, parâmetros e o binário do modelo em tempo real.  
Em produção, este componente deve ser escalado como um serviço containerizado (Docker) conectado a um banco de dados persistente.

**`python -m pip install -r requirements.txt` (Governança de Ambiente):**  
Comando crítico para evitar o *Dependency Hell*.  
A instalação das bibliotecas com versões fixadas garante que a mesma versão do `transformers`, `torch` e `mlflow` utilizada no treinamento seja a mesma utilizada na inferência.  
A falta deste rigor é a principal causa de falhas de predição em sistemas de ML distribuídos.

**`git rebase --continue` (Manutenção de Histórico):**  
Essencial em fluxos de desenvolvimento colaborativo.  
Ao realizar o rebase, garantimos que o histórico de commits do pipeline seja linear e não contenha "poluição" de merges automáticos.  
Isso permite que qualquer membro da equipe ou auditor técnico rastreie a evolução do modelo a partir de qualquer commit específico, essencial para conformidade.

**`python src/ids/model_training.py` (Orquestração de Pipeline):**  
Este comando atua como o *entrypoint* do pipeline de IDS.  
Ele encapsula a carga de dados, a lógica de treino via `IsolationForest` e a instrumentação via `mlflow`.  
A automação aqui reduz o erro humano, garantindo que o modelo seja treinado exatamente sob as mesmas condições de pré-processamento.

**`git add . && git commit -m "..."` (Commit Atômico):**  
A prática de commits atômicos é a base da rastreabilidade.  
Cada commit descreve uma alteração única (ex: ajuste de *learning rate* ou adição de um *Guardrail*).  
Se uma regressão de desempenho ocorrer no modelo após um *push*, o desenvolvedor pode reverter apenas a mudança atômica problemática, mantendo o restante do pipeline íntegro.

**`mlflow models serve` (Deploy de Inferência):**  
Comando avançado para disponibilizar o modelo como um microserviço RESTful.  
Após o fine-tuning, utilizamos este comando para expor um endpoint onde o módulo de detecção pode receber URLs via HTTP e retornar a classificação em milissegundos.

**`torch.cuda.is_available()` (Diagnóstico de Hardware):**  
Comando vital dentro dos scripts de treinamento para verificar se o treinamento do `DistilBERT` pode ocorrer via GPU ou se deve falhar silenciosamente para CPU.  
A gestão consciente de recursos é fundamental para não onerar o pipeline de rede (IDS).

**`git pull origin main --rebase` (Sincronização Estratégica):**  
Comando fundamental para integrar alterações feitas remotamente (por outros membros da equipe ou edições no GitHub) sem quebrar o fluxo local, mantendo a história do projeto alinhada com o repositório principal.

## 6. Segurança Operacional e Deploy em Produção

A transição do pipeline de desenvolvimento para o ambiente de produção (online) exige uma camada robusta de proteção (*Guardrails*) e uma estratégia de orquestração de inferência (*Model Serving*).

### 6.1 Guardrails (Segurança de Entrada)

A camada de *Guardrails* atua como a primeira linha de defesa contra *Adversarial Attacks* e injeções de dados malformados, garantindo que apenas inputs validados alcancem os modelos.

**Fundamentação:**  
Em sistemas de cibersegurança, confiar cegamente no input do usuário é um risco crítico.  
URLs maliciosas ou logs corrompidos podem causar estouro de buffer ou manipulação indevida do modelo.

**Abordagem via Pydantic:**  
Utilizamos o `pydantic` para a definição de um `URLSchema` rigoroso.  
Este esquema valida não apenas o tipo (string), mas a conformidade com protocolos de rede (ex: `http/https`).

**Validação de Schema:**  
O uso de `BaseModel` permite validar o input de forma estruturada antes do processamento.  
Se um input falha na validação (`ValidationError`), o sistema rejeita a inferência, registrando um evento de segurança, o que protege a integridade e a latência do modelo frente a entradas maliciosas ou lixo computacional.

---

### 6.2 Estratégia de Deploy

O deploy não é estático; ele é o estágio final do ciclo de vida do modelo (*ML System*).

**Infraestrutura (Model Serving):**  
O modelo é promovido via *Model Registry* do MLflow.  
Utilizamos o `mlflow models serve` para expor uma API RESTful, desacoplando a lógica de detecção (phishing/IDS) da aplicação consumidora (ex: um browser ou firewall corporativo).

**Escalabilidade e Containers:**  
O pipeline é desenhado para ser encapsulado em *Docker containers*, isolando o ambiente de execução (`torch`, `transformers`) e garantindo paridade entre o ambiente de treino e produção.

**Monitoramento de Latência:**  
Em cibersegurança, cada milissegundo é vital.  
Monitoramos a latência via logs estruturados (JSON), disparando alertas caso o tempo de resposta exceda o *SLA* definido.

**Canary Deployment:**  
Antes de uma atualização total, novos modelos são expostos a uma pequena fração do tráfego (Canary) para validar se a acurácia se mantém estável antes de assumir 100% da carga de tráfego (estratégia Blue-Green).

---

## 7. Informações Relevantes sobre os Datasets

A qualidade do modelo de ML é limitada pela qualidade dos dados (Garbage In, Garbage Out).  
O projeto utiliza dois datasets distintos com desafios de ingestão singulares:

### 1.1 Dataset CICIDS2017 (IDS)

Este dataset representa o estado da arte na simulação de tráfego de rede corporativa.

**Complexidade Estrutural:**  
Composto por mais de 70 atributos por fluxo de rede (NetFlow), que incluem métricas temporais, tamanho de pacotes, flags TCP/UDP e inter-arrival times.

**Desafios de Engenharia:**  
A alta dimensionalidade introduz o problema da "Maldição da Dimensionalidade", onde a distância entre pontos no espaço de features torna-se menos informativa.  
A seleção de features (*feature selection*) foi essencial para manter a latência de inferência abaixo de milissegundos.

**Integridade dos Dados:**  
O dataset exige uma limpeza rigorosa.  
Encontramos uma prevalência significativa de valores `NaN` e `Infinity`, resultado de fluxos de rede incompletos.  
A estratégia de `dropna()` aliada à substituição por `np.nan` garante que o modelo `IsolationForest` não tente processar valores não finitos, que causariam a falha total do pipeline matemático.

**Relevância:**  
Este dataset é fundamental por simular ataques reais de *Port Scanning*, *DoS* e *Botnet*, permitindo que o sistema aprenda o comportamento basal da rede antes de identificar desvios anômalos.

---

### 1.2 Dataset de URLs (Phishing Detection)

**Natureza dos Dados:**  
Consiste em strings textuais que codificam intenção maliciosa através de técnicas como *typosquatting* (imitação de domínios legítimos) e *homoglyphs*.

**Processamento de Linguagem Natural (NLP):**  
Ao contrário dos dados numéricos do IDS, aqui tratamos URLs como sequências de tokens.  
A limpeza envolve remover caracteres especiais irrelevantes, normalizar URLs para minúsculas e estruturar o label binário (1 = Phishing, 0 = Legítimo).

**Diversidade:**  
O dataset inclui URLs de bancos, redes sociais e sites de download de software, o que força o `DistilBERT` a aprender padrões globais de escrita maliciosa em vez de apenas memorizar domínios específicos.

---

## 2. Engenharia de ML e Arquitetura de Sistemas

A arquitetura foi desenhada para separar claramente a lógica de pré-processamento, treinamento e registro, garantindo modularidade.

**Pipeline de Ingestão:**  
Criamos uma classe de pré-processamento que abstrai a carga dos dados, permitindo que a limpeza ocorra sempre da mesma forma, seja para treino ou para inferência em produção.  
Isso elimina o *Training-Serving Skew* (quando os dados de treino não batem com os de produção).

**Pipeline de Treinamento:**  
O script `src/ids/model_training.py` atua como um orquestrador.  
Ele não apenas treina o `IsolationForest`, mas também realiza a instrumentação de observabilidade, enviando métricas cruciais (`n_anomalies`) para o servidor do MLflow.

**MLflow:**  
O uso desta ferramenta é o que separa um script acadêmico de um *ML System* real.  
Cada execução do treinamento gera um *Run ID* único, armazenando não apenas o modelo, mas o ambiente de execução completo (versão do Python, pacotes instalados).  
Isso garante a reprodutibilidade absoluta dos experimentos.

**Estratégia de Deploy:**  
Optamos pelo deploy de script local via registro do MLflow, mas a arquitetura já prevê a transição para `mlflow models serve` (REST API), o que tornaria o sistema consumível por qualquer microserviço da infraestrutura de segurança da rede.

---

## 8. Glossário Técnico

* **Anomaly Detection (Detecção de Anomalias):** Técnica de ML que identifica padrões de comportamento que se desviam significativamente da norma estatística, operando sem a necessidade de rótulos prévios de ataque.  
* **Artifact (Artefato):** Qualquer objeto persistido durante o ciclo de vida do modelo pelo MLflow, incluindo binários de modelos (pickle/pt), gráficos de performance e logs de treino.  
* **Batch Normalization:** Técnica de regularização em redes neurais que normaliza as ativações de cada camada, estabilizando o gradiente e acelerando a convergência em modelos como o DistilBERT.  
* **Data Drift (Desvio de Dados):** Ocorre quando a distribuição estatística dos dados de entrada sofre alteração temporal, tornando o modelo treinado anteriormente obsoleto e menos preciso.  
* **Dependency Hell:** Problema enfrentado quando diferentes pacotes exigem versões incompatíveis de uma mesma biblioteca, resolvido no projeto com o uso de `requirements.txt` e `pyenv`.  
* **DistilBERT:** Versão otimizada e destilada do modelo BERT, mantendo 97% da performance com 40% menos parâmetros, ideal para inferência de baixa latência em URLs.  
* **Fine-tuning (Transfer Learning):** Processo de ajustar pesos de um modelo pré-treinado em um dataset específico (Phishing URLs) para especializar sua capacidade de predição.  
* **Guardrails:** Camada lógica de segurança implementada antes da inferência para validar schemas de entrada (via `pydantic`) e evitar injeções de dados malformados.  
* **Inference Latency:** Tempo decorrido desde a recepção de uma URL até a predição. Em sistemas de segurança, esse tempo é crítico para o bloqueio em tempo real.  
* **Isolation Forest:** Algoritmo baseado em árvores que isola anomalias em vez de descrever pontos normais; sua eficácia reside na baixa profundidade necessária para segregar observações raras.  
* **MLOps:** Conjunto de práticas que visam a automação e melhoria da qualidade, versionamento e monitoramento de modelos de Machine Learning em produção.  
* **NLP (Natural Language Processing):** Subcampo da IA que permite ao sistema processar sintaxe e semântica de URLs para detectar intenção maliciosa oculta.  
* **Overfitting:** Falha onde o modelo "decora" o dataset de treino, perdendo a capacidade de generalizar para novas URLs ou ataques de rede nunca vistos.  
* **Parquet:** Formato de arquivo columnar altamente comprimido e eficiente em I/O, recomendado para substituir CSV em pipelines de Big Data.  
* **Tokenização:** Processo de fragmentação de textos (URLs) em unidades menores (tokens) para alimentar os Transformers.  
* **Training-Serving Skew:** Discrepância entre os dados utilizados no treinamento e os dados que o sistema recebe em produção; mitigado com pré-processamento modular.
   
## 9. Desafios Enfrentados

O desenvolvimento de um sistema de ML voltado para cibersegurança apresenta desafios complexos que transcendem o simples treinamento de modelos, exigindo uma infraestrutura resiliente e adaptável.

**Consistência de Pathing:**  
Um dos obstáculos iniciais foi a gestão de caminhos relativos em ambientes distribuídos.  
A solução definitiva consistiu em adotar o caminho absoluto a partir da raiz do repositório (`/home/ingrid/Ingrid/unb/26/machine/Projetos-Individuais-2026-1/ingrid-soares/projeto-2/`), o que garantiu portabilidade total entre o ambiente de desenvolvimento e o ambiente de orquestração.

**Volume e Qualidade dos Dados:**  
O dataset `CICIDS2017` possui uma massa crítica de dados (centenas de milhares de linhas) que frequentemente contêm inconsistências numéricas, como divisões por zero em métricas de fluxo de rede.  
O desafio foi implementar uma camada de pré-processamento que não apenas descartasse esses registros, mas que preservasse a integridade estatística do restante, evitando que o `IsolationForest` fosse treinado sobre um conjunto enviesado.

**Ambiente de Dependências:**  
O ecossistema de *Transformers* da Hugging Face, aliado ao PyTorch, possui requisitos de versões de bibliotecas (como `accelerate` e `datasets`) que frequentemente colidem com versões de pacotes estáveis do sistema.  
A adoção de um ambiente `pyenv` com Python 3.10.12 foi o divisor de águas para estabilizar o pipeline, resolvendo o "Dependency Hell" que impedia o carregamento correto dos pesos do `DistilBERT`.

**Observabilidade e Debugging:**  
Identificar por que um modelo não convergia ou por que uma predição estava incorreta exigiu a implementação de uma instrumentação granular no MLflow.  
O maior desafio foi transformar métricas técnicas brutas (como contagem de anomalias) em dados visuais que permitissem um *tuning* rápido de hiperparâmetros.

**I/O e Latência:**  
A leitura massiva de arquivos CSV se provou um gargalo para a escalabilidade.  
O desafio de integrar modelos complexos em sistemas de rede onde cada milissegundo é vital forçou o design de uma arquitetura pronta para migração para formatos colunares (`parquet`), visando otimizar a carga de dados na memória.

**Complexidade do Fine-tuning:**  
O ajuste de pesos de modelos pré-treinados requer cuidados com a inicialização de camadas superiores.  
Lidamos com warnings de `MISSING` ou `UNEXPECTED` keys, que exigiram uma compreensão profunda de como as arquiteturas de *Transformers* funcionam, distinguindo erros de configuração de comportamentos normais de inicialização de *Transfer Learning*.

---

## 10. Observabilidade e Registro de Modelos (MLflow Registry)

**Estrutura de Artefatos:**  
A inspeção via `Artifacts` revela a maturidade da persistência do modelo.  
O MLflow gera automaticamente:

- **MLmodel:** Manifesto que encapsula os metadados e os *flavors* (ex: `sklearn`), permitindo que o modelo seja lido por diferentes ferramentas sem necessidade de re-implementar código.  
- **Conda/Python Environment:** Captura exata das dependências, eliminando conflitos de versão entre desenvolvimento e deploy.  
- **Cloudpickle:** Formato robusto de serialização para objetos `scikit-learn`, permitindo a deserialização precisa dos pesos do modelo.

**Inspeção Técnica:**  
A navegação pelos arquivos (`MLmodel`, `conda.yaml`) permite que auditores de segurança validem a conformidade do ambiente de treino sem ter acesso ao código-fonte, um requisito essencial para *compliance* em sistemas críticos de rede.

---

## 11. Próximos Passos (Evolução do Sistema)

O sistema, embora funcional, encontra-se em uma fase de arquitetura de base, sendo o roteiro de evolução focado na robustez de produção, redução de latência e automação:

**Fine-tuning Refinado e Validação:**  
Avançar na etapa de treinamento do *DistilBERT* para o módulo de Phishing.  
O próximo ciclo de desenvolvimento foca no aumento do número de épocas (*epochs*) e na implementação de uma estratégia de *hyperparameter tuning* (ex: via *Optuna*) para otimizar o *learning rate* e o tamanho do *batch*, garantindo a convergência da perda (*Loss*) em um dataset de validação independente.

**Implementação de Guardrails de Entrada:**  
Desenvolver uma camada de segurança com `pydantic` para validação de schemas de entrada.  
O objetivo é garantir que apenas inputs que sigam o formato estrito de URLs e pacotes de rede (ex: campos de IP, portas, sinalizadores TCP) sejam processados pelo pipeline, impedindo ataques de injeção de dados malformados (*adversarial inputs*).

**Migração de Formato (I/O Otimizado):**  
Substituir a carga de dados `csv` por `parquet`.  
Em sistemas de detecção de anomalias com 500k+ registros, o overhead de I/O é um gargalo crítico.  
O uso de `parquet` oferece compressão columnar, que reduz drasticamente o consumo de memória RAM e acelera a carga inicial do pipeline de treinamento.

**Monitoramento de Data Drift:**  
Configurar um sistema de alerta baseado em threshold estatístico que compare a distribuição do tráfego de entrada em tempo real com a distribuição de treino do modelo original.  
Se o desvio (drift) exceder um limite configurado, o sistema deve disparar um alerta para retreinamento automático.

**Integração com Pipelines CI/CD:**  
Automatizar a execução do pipeline de treino em servidores dedicados (ex: *GitHub Actions* ou *Jenkins*), disparando testes de regressão sempre que o código fonte for alterado, garantindo que mudanças no pré-processamento não quebrem a acurácia dos modelos registrados no MLflow Registry.

**Dashboard de Performance em Tempo Real:**  
Desenvolver painéis de observabilidade em ferramentas como *Grafana* ou *Dash* (Plotly), integrados ao MLflow, para monitorar latência de inferência e número de anomalias detectadas por segundo (EPS - Events Per Second), provendo um *SLA* claro para a equipe de SOC.

**Orquestração de Inferência:**  
Evoluir o script de inferência para um serviço de *API RESTful* (via `mlflow models serve` ou `FastAPI`), permitindo que a detecção de ameaças seja consumida de forma síncrona por outros serviços do ecossistema de segurança.

## 12. Checklist de Ações Relevantes

Este checklist organiza as entregas em níveis de criticidade e maturidade, servindo para validação de requisitos funcionais e técnicos do pipeline de MLOps.

### 12.1 Funcionalidades Implementadas e Validadas (Core MLOps)

- [x] **Estrutura de Repositório:** Organização centralizada em `ingrid-soares/projeto-2/`, garantindo portabilidade absoluta.
- [x] **Ingestão IDS:** Scripts em `src/ids/` (limpeza, sanitização `inf/NaN` e normalização) validados.
- [x] **Treinamento IDS:** Pipeline de treino (*Isolation Forest*) operacional com registro completo no MLflow.
- [x] **Instrumentação IDS:** Logs de métricas dinâmicas (`n_anomalies`, `n_normal`) integrados ao MLflow.
- [x] **Integração Phishing:** Estrutura base de processamento (NLP/Tokenização) utilizando `DistilBERT` (Hugging Face).
- [x] **Documentação Técnica:** Relatórios e Detalhes Técnicos consolidados e versionados no repositório.
- [x] **Governança de Ambiente:** Fixação de dependências via `requirements.txt` e `pyenv` (Python 3.10.12).

---

### 12.2 Módulo de Segurança Operacional 

- [x] **Fine-Tuning de Performance:** Execução de ciclos de treinamento longo para o `DistilBERT` com otimização de hiperparâmetros (Optuna).
- [x] **Guardrails de Validação:** Implementação de schemas de entrada usando `pydantic` para garantir a integridade dos dados antes da inferência.
- [x] **Monitoramento de Data Drift:** Configuração de alertas automáticos baseados em threshold estatístico quando a distribuição dos dados de rede desviar do treino.

---

### 12.3 Performance e Otimização 

- [x] **Otimização de I/O (Parquet):** Migração do formato de persistência de dados de `csv` para `parquet`, visando redução drástica de latência de leitura e consumo de memória em grandes volumes.
- [x] **Dashboards de Observabilidade:** Configuração de painéis em *Grafana/Dash* para monitoramento de eventos por segundo (EPS) e latência de inferência.

---

### 12.4 Deploy e CI/CD 

- [x] **Deploy RESTful:** Disponibilização do modelo via API (Flask/FastAPI ou `mlflow models serve`) para consumo síncrono.
- [x] **Testes de Regressão (CI/CD):** Automação de testes de qualidade do modelo via *GitHub Actions* para cada novo commit no pipeline, garantindo qualidade contínua.

OBS: O sistema atingiu um estado de maturidade de produção, com o core de inferência, fine-tuning automatizado e serviços de API validados. As pendências restantes referem-se a escalabilidade em larga escala (Parquet), monitoramento em tempo real (Grafana/Drift) e automação de esteira (CI/CD).



