# Roadmap de Engenharia de ML: Evoluções Futuras

Este documento define o plano de evolução técnica para transformar o pipeline de MLOps atual (operacional em ambiente local) em um sistema de escala empresarial em nuvem.

### I. Infraestrutura de Nuvem e Escalabilidade (Cloud-Native)
- [ ] **Containerização (Docker/Kubernetes):** Empacotamento dos módulos de inferência (FastAPI) e treinamento em containers Docker, com orquestração via Kubernetes para auto-scaling em nuvem (AWS/GCP/Azure).
- [ ] **Provisionamento de Infraestrutura como Código (IaC):** Utilização de Terraform ou Pulumi para provisionar ambientes de produção de forma reprodutível e versionada.
- [ ] **Gerenciamento de Modelos em Nuvem:** Migração do MLflow local para um servidor de produção (Managed MLflow) com armazenamento de artefatos em S3 ou Google Cloud Storage.

### II. Inteligência Adaptativa e Monitoramento (Nível SOC)
- [ ] **Data Drift Detection (Estatística Bayesiana):** Implementar um monitor de desvio (Drift) em tempo real utilizando divergência de Kullback-Leibler ou o Teste de Kolmogorov-Smirnov.
- [ ] **Closed-loop Retraining:** Automação de gatilho para retreinamento do modelo de IDS assim que o drift atingir um limiar crítico, garantindo que o sistema não perca acurácia frente a novos ataques.

### III. Engenharia de Performance e Concorrência
- [ ] **Model Serving de Baixa Latência (gRPC):** Implementação de endpoints gRPC em paralelo ao REST/FastAPI para reduzir o overhead de serialização JSON em sistemas de rede de altíssima latência crítica.
- [ ] **Quantização de Modelo (INT8):** Aplicação de técnicas de quantização no DistilBERT (via ONNX Runtime ou TensorRT) para reduzir o footprint do modelo e acelerar a inferência em ambientes com restrição de hardware (Edge Computing).

### IV. Observabilidade de Nível Corporativo
- [ ] **Dashboards (Grafana + Prometheus):** Exportação de métricas de infraestrutura (latência de inferência, RAM/CPU) e métricas de negócio (Eventos Por Segundo - EPS) para stack Prometheus/Grafana.
- [ ] **Sistema de Alertas (Alertmanager):** Configuração de alertas de anomalias críticas via Slack/PagerDuty disparados diretamente do sistema de monitoramento de drift.

### V. DevSecOps & Automação Industrial
- [ ] **CI/CD End-to-End:** Implementação de pipeline no GitHub Actions estendido para: (1) Testes de Regressão de Modelo em ambiente de staging, (2) Build e push de imagem Docker, (3) Deploy automático (Blue/Green Deployment).
- [ ] **Feature Store:** Implementação de uma Feature Store (ex: Feast) para garantir que as mesmas features usadas no treino sejam servidas de forma consistente na inferência, eliminando o Training-Serving Skew.
