# Relatório Técnico: Sistema de Segurança Integrado (IDS & Phishing)

Este documento detalha a implementação do sistema de segurança, fornecendo uma visão profunda sobre a arquitetura de ML, escolhas de modelos e integração com o MLflow, servindo como guia de estudos e inspeção técnica.

---

## 1. Arquitetura do Sistema
O sistema foi desenhado para ser modular, permitindo a independência entre o módulo de detecção de tráfego de rede (IDS) e o módulo de detecção de Phishing.

- **Módulo IDS:** Foca em identificar anomalias (Port Scanning) através do dataset `CICIDS2017`.
- **Módulo Phishing:** Foca em classificar URLs como maliciosas ou legítimas usando modelos pré-treinados via `Hugging Face`.

## 2. Pipeline de ML
O fluxo foi construído priorizando a reprodutibilidade:
1. **Ingestão:** Scripts dedicados em `src/ids/` e `src/phishing/`.
2. **Pré-processamento:** Limpeza rigorosa e tratamento de dados corrompidos.
3. **Treinamento:** Execução com logging automático via `mlflow`.
4. **Avaliação:** Comparação de métricas entre diferentes experimentos.
5. **Inferência:** Disponibilização de scripts locais.

## 3. Integração MLflow
O MLflow é utilizado para:
- **Rastreamento:** Registro de parâmetros (ex: taxas de contaminação, arquitetura de rede).
- **Versionamento:** Modelos versionados e salvos como artefatos prontos para deploy.
- **Observabilidade:** Interface de comparação para garantir que o melhor modelo seja promovido ao ambiente de produção.
