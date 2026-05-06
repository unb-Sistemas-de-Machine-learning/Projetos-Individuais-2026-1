# Resumo do Projeto Individual 2 - Sistema de ML (ML Systems & MLOps)

Essa é a entrega de uma infraestrutura de **Machine Learning Systems** de alta maturidade, desenhada para detecção de ameaças cibernéticas (IDS e Phishing). O sistema evoluiu de scripts isolados para um ecossistema de produção robusto, focado em escalabilidade e observabilidade.

### Visão Geral: Da Concepção à Produção
O projeto começou com a necessidade de desenvolver modelos de detecção de ameaças que fossem além de simples classificações, exigindo um pipeline que pudesse ser operado com segurança. Ao longo do desenvolvimento, transformamos dados brutos (CSV) em fluxos de trabalho otimizados (Parquet), garantindo que o sistema fosse rápido e não consumisse memória desnecessária. Implementamos "filtros de segurança" (Guardrails) em todas as entradas de dados, protegendo o sistema contra dados corrompidos ou maliciosos. Além disso, automatizamos o processo de treinamento e fine-tuning, garantindo que o sistema não dependa de ajustes manuais, e criamos uma API moderna que permite que o sistema seja consultado instantaneamente, monitorando sua própria saúde e performance através de dashboards e logs estruturados.

### Principais Entregas
1. **Pipeline de Produção (End-to-End):** Implementação dos módulos de IDS e Phishing otimizados, modulares e integrados.
2. **APIs de Inferência de Baixa Latência:** Serviço de inferência robusto utilizando **FastAPI**, com **Guardrails (Pydantic)** para proteger a integridade dos inputs em tempo real.
3. **Observabilidade Corporativa:** Ecossistema completo de monitoramento com **MLflow** (rastreamento de experimentos e registro de modelos) e **Dash** para visualização de métricas operacionais.
4. **Excelência em MLOps (Automação):** Configuração de esteira de integração contínua (CI/CD) via **GitHub Actions** e automação de hiperparâmetros com **Optuna**.
5. **Performance e I/O:** Migração de toda a camada de dados para formato colunar (**Parquet/Snappy**), reduzindo drasticamente o consumo de I/O e RAM.
6. **Roadmap Estratégico:** Documentação de evolução clara entre o que é operacional agora e o que escala para nível industrial.

### Detalhes Técnicos e Conformidade
* **Privacidade e Segurança:** Aplicação de *Data Minimization* e *Guardrails* rigorosos, alinhados às melhores práticas de segurança operacional (*Privacy-by-Design*).
* **Qualidade de Código:** Arquitetura desacoplada (`src/`), fixação de dependências (`requirements.txt`) e commits atômicos para rastreabilidade total.

---
**Status da Entrega:** O sistema atingiu um estado avançado de maturidade de produção, com o core de inferência, fine-tuning automatizado e serviços de API validados e prontos para ambientes de staging.
