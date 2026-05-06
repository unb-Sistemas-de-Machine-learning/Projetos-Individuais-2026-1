# Roadmap de Implementações (Checklist Oficial)

Este documento centraliza as entregas validadas do pipeline de MLOps.

### Funcionalidades Comuns (IDS e Phishing)
- [x] **Arquitetura Modular:** Organização centralizada em `src/`, garantindo desacoplamento e portabilidade absoluta.
- [x] **Contratos de Dados (Guardrails):** Implementação de schemas de validação (`pydantic`) para garantir a integridade dos inputs antes da inferência.
- [x] **Serviço de Inferência (Deploy RESTful):** Disponibilização de microserviços síncronos via **FastAPI** com documentação interativa.
- [x] **Automação de CI/CD (Regressão):** Automação de testes de qualidade do modelo via **GitHub Actions**.
- [x] **Documentação Técnica:** Relatórios (Entrega e Detalhes Técnicos) consolidados e versionados.
- [x] **Governança de Ambiente:** Fixação de dependências via `requirements.txt` (suporte a `transformers`, `torch`, `pydantic`, `optuna`, `fastapi` e `pyarrow`).

### Módulo IDS (Detecção de Intrusão)
- [x] **Pipeline de Ingestão Otimizado:** Processamento robusto de dados (`CICIDS2017`) com sanitização automática (`inf/NaN`) e persistência em **Parquet**.
- [x] **Orquestração de Treinamento:** Pipeline de modelagem (*Isolation Forest*) com rastreamento completo de artefatos e instrumentação de métricas via **MLflow**.

### Módulo Phishing (NLP)
- [x] **Fine-Tuning de Performance:** Pipeline de NLP (`DistilBERT`) otimizado com busca bayesiana (**Optuna**), validação cruzada (*k-fold*) e métricas de acurácia.
- [x] **Pipeline de Ingestão Otimizado:** Processamento de tokens com persistência estruturada em formato **Parquet**.
- [x] **Observabilidade e Monitoramento:** Configuração completa do dashboard nativo do **MLflow UI** para inspeção em tempo real.

### Pendências e Evoluções (Roadmap Avançado)
- [x] **Monitoramento de Data Drift:** Script utilitário `src/common/drift_detector.py` com teste estatístico KS implementado.
- [ ] **Dashboards de Observabilidade (Grafana/Dash):** Configuração de painéis externos para monitoramento avançado de latência e EPS (Eventos Por Segundo).

---

**Status:** O sistema atingiu um estado avançado de maturidade de produção, com o core de inferência, fine-tuning automatizado e serviços de API já validados. O projeto encontra-se em fase de refinamento contínuo para escalabilidade em larga escala (Parquet), monitoramento em tempo real (Grafana/Drift) e automação de esteira (CI/CD). Todo o core de inferência, fine-tuning automatizado, API de baixo overhead (latência monitorada) e lógica de detecção de drift estão implementados e validados.

**Consulte os documentos para o roadmap viável da disciplina:**
- [roadmap-futuro.md](roadmap-futuro.md) para detalhes sobre as próximas evoluções técnicas.
- [relatorio-entrega.md](relatorio-entrega.md) para o documento oficial de submissão.
- [detalhes-tecnicos.md](detalhes-tecnicos.md) para a visão técnica aprofundada da arquitetura.
