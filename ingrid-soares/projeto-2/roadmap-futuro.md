# Roadmap de Engenharia de ML: Nível Avançado (Complementar ao Checklist Oficial)

Este documento define o plano de evolução técnica para transformar o pipeline de MLOps atual em um sistema de escala empresarial. As tarefas aqui listadas focam em resiliência, performance computacional e automação de nível industrial.

### I. Inteligência Adaptativa e Monitoramento (Nível SOC)
- [ ] **Data Drift Detection (Estatística Bayesiana):** Implementar um monitor de desvio (Drift) utilizando a divergência de Kullback-Leibler ou o Teste de Kolmogorov-Smirnov para comparar o baseline de treino com o tráfego em tempo real.
- [ ] **Closed-loop Retraining:** Automação de gatilho para retreinamento do modelo de IDS assim que o drift atingir um limiar crítico, garantindo que o sistema não perca acurácia frente a novos ataques.

### II. Engenharia de Performance e Concorrência
- [ ] **I/O Columnar de Alta Performance:** Migração total de CSV para Parquet com particionamento baseado em séries temporais (Data/Hora) para reduzir I/O de disco e consumo de RAM em 90%.
- [ ] **Model Serving de Baixa Latência (gRPC):** Implementação de endpoints gRPC em paralelo ao REST/FastAPI para reduzir o overhead de serialização JSON em sistemas de rede de altíssima latência crítica.
- [ ] **Quantização de Modelo (INT8):** Aplicação de técnicas de quantização no DistilBERT (via ONNX Runtime ou TensorRT) para reduzir o footprint do modelo e acelerar a inferência em ambientes com restrição de hardware (Edge Computing).

### III. Observabilidade de Nível Corporativo
- [ ] **Dashboards de Observabilidade (Grafana + Prometheus):** Exportação de métricas de infraestrutura (latência de inferência, RAM/CPU) e métricas de negócio (Eventos Por Segundo - EPS) para o stack Prometheus/Grafana.
- [ ] **Sistema de Alertas (Alertmanager):** Configuração de alertas de anomalias críticas via Slack/PagerDuty disparados diretamente do sistema de monitoramento de drift.

### IV. DevSecOps & Automação Industrial
- [ ] **CI/CD End-to-End:** Implementação de pipeline no GitHub Actions que execute: (1) Unit Tests no código, (2) Testes de Regressão de Modelo em ambiente de staging, (3) Build e push de imagem Docker para container registry.
- [ ] **Feature Store:** Implementação de uma Feature Store (ex: Feast) para garantir que as mesmas features usadas no treino sejam servidas de forma consistente na inferência, eliminando o Training-Serving Skew.

**OBS:** Este roadmap representa a transição do sistema de um protótipo validado para uma infraestrutura de segurança cibernética resiliente, capaz de lidar com petabytes de logs e cenários de ataque dinâmicos em produção.
