# Roadmap de Implementações (Checklist Oficial)

Este documento centraliza as entregas validadas do pipeline de MLOps.

### 12.1 Funcionalidades Implementadas e Validadas (Core MLOps)

- [x] **Estrutura de Repositório:** Organização modular centralizada em `src/`, garantindo separação de responsabilidades e portabilidade absoluta.
- [x] **Ingestão IDS:** Pipeline de dados robusto com sanitização automática (`inf/NaN`) e normalização estatística para o dataset CICIDS2017.
- [x] **Treinamento IDS:** Pipeline de treino (*Isolation Forest*) operacional com registro completo no MLflow e instrumentação.
- [x] **Fine-Tuning de Phishing:** Pipeline de NLP (`DistilBERT`) com otimização bayesiana (Optuna), validação cruzada e métricas de acurácia.
- [x] **Guardrails de Validação:** Implementação de contratos de dados (via `pydantic`) para garantir a integridade dos inputs antes da inferência.
- [x] **Deploy RESTful:** Disponibilização de serviços de inferência síncronos via **FastAPI**, com documentação automática.
- [x] **Automação de CI/CD (Regressão):** Automação de testes de qualidade do modelo e integridade do pipeline via **GitHub Actions**.
- [x] **Documentação Técnica:** Relatórios e Detalhes Técnicos consolidados e versionados no repositório.
- [x] **Governança de Ambiente:** Fixação de dependências via `requirements.txt` (suporte a `transformers`, `torch`, `pydantic`, `optuna` e `fastapi`).

---

### 12.2 Módulo de Segurança Operacional 

- [ ] **Monitoramento de Data Drift:** Configuração de alertas automáticos baseados em threshold estatístico quando a distribuição dos dados de rede desviar do treino.

---

### 12.3 Performance e Otimização 

- [ ] **Otimização de I/O (Parquet):** Migração do formato de persistência de dados de `csv` para `parquet`, visando redução drástica de latência de leitura e consumo de memória.
- [ ] **Dashboards de Observabilidade (Grafana/Dash):** Configuração de painéis externos para monitoramento avançado de latência e EPS (Eventos Por Segundo).

---

### 12.4 Deploy e CI/CD 

- [ ] **Testes de Regressão (CI/CD):** Automação de testes de qualidade do modelo via *GitHub Actions* para cada novo commit no pipeline, garantindo qualidade contínua.

**OBS:** O sistema atingiu um estado avançado de maturidade de produção, com o core de inferência, fine-tuning automatizado e serviços de API já validados. As pendências restantes referem-se a escalabilidade em larga escala (Parquet), monitoramento avançado em tempo real (Grafana/Drift) e automação de esteira (CI/CD). 

**Consulte os documentos para o roadmap viável da disciplina:**
- [roadmap-futuro.md](roadmap-futuro.md) para detalhes sobre as próximas evoluções técnicas.
- [relatorio-tecnico.md](relatorio-tecnico.md) para o documento oficial de submissão.
- [detalhes-tecnicos.md](detalhes-tecnicos.md) para a visão técnica aprofundada da arquitetura.
