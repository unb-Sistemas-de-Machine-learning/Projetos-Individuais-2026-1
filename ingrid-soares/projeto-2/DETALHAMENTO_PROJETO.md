# Detalhamento do Projeto: Sistema de Segurança Integrado (IDS & Phishing Detection)

Este documento serve como um guia didático para o **Projeto Individual 2**, focado em **ML Systems** aplicado à **Cibersegurança**. O objetivo é construir um sistema end-to-end que utilize Machine Learning para detectar ameaças em dois fronts principais: tráfego de rede e URLs maliciosas.

---

## 1. Tema e Contexto
O projeto aborda o desenvolvimento de um **Sistema de Segurança Integrado**. Na cibersegurança moderna, a detecção reativa baseada em assinaturas (como antivírus tradicionais) não é mais suficiente. O uso de **Machine Learning (ML)** permite identificar padrões anômalos e comportamentos suspeitos que ainda não foram catalogados.

### Módulos do Sistema:
1.  **IDS (Intrusion Detection System):** Monitoramento de tráfego de rede para detectar tentativas de intrusão.
2.  **Phishing Detection:** Análise de URLs para identificar sites fraudulentos que buscam roubar credenciais ou disseminar malware.

---

## 2. Objetivos Técnicos
*   **MLflow:** Centralizar o rastreamento de experimentos, versionamento de modelos e reprodutibilidade.
*   **Engenharia de Pipeline:** Construir um fluxo modular desde a aquisição de dados até o deploy para inferência.
*   **Guardrails:** Implementar restrições para garantir que o modelo opere dentro de limites seguros e confiáveis.
*   **Observabilidade:** Monitorar o comportamento do sistema em tempo real via logs e métricas.

---

## 3. Relação com Cibersegurança e Redes

### Red Team e Reconhecimento (IDS)
Para quem visa oportunidades em **Red Team**, entender como o tráfego de rede é monitorado é fundamental. 
*   **Port Scanning:** É frequentemente o primeiro passo de um atacante para mapear serviços expostos. Nosso módulo IDS foca especificamente em detectar esses padrões.
*   **Protocolos:** O projeto lida com dados de fluxos de rede (NetFlow/IPFIX), envolvendo conhecimentos de camadas de transporte (TCP/UDP) e rede (IP).

### Phishing e Engenharia Social
O phishing continua sendo o vetor de ataque número 1 para invasão de redes corporativas.
*   **Roubo de Credenciais:** Identificar URLs que mimetizam sites legítimos (ex: bancos, portais de login).
*   **Distribuição de Malware:** Detectar links que forçam o download de payloads maliciosos.

---

## 4. Tecnologias Utilizadas
*   **Linguagem:** Python 3.10.12 (configurado via `pyenv`).
*   **MLflow:** Para gestão de ciclo de vida de ML.
*   **Scikit-Learn:** Para algoritmos clássicos de detecção de anomalias (Isolation Forest, SVM).
*   **Hugging Face Transformers:** Para integração do modelo pré-treinado **DistilBERT** na classificação de URLs.
*   **Pandas/Numpy:** Manipulação e processamento de grandes datasets de segurança.

---

## 5. Estrutura de Instalação e Execução
1.  **Ambiente:** O projeto utiliza Python 3.10 para compatibilidade com bibliotecas de Deep Learning.
2.  **Dependências:** Instaladas via `pip install -r requirements.txt`.
3.  **Execução:** Os scripts estão organizados na pasta `src/`, divididos por responsabilidade (preparação, treinamento, inferência).

---

Este projeto não é apenas sobre "treinar um modelo", mas sobre **Engenharia de Sistemas de ML**, garantindo que o modelo seja útil, seguro e monitorável em um ambiente de produção de segurança.
