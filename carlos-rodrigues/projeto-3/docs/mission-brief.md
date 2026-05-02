# Mission Brief

> **Aluno(a):** Carlos Eduardo Rodrigues
> **Matrícula:** 221031265
> **Domínio:** Curadoria Automática de Artigos Científicos

---

## 1. Objetivo do agente

Triar automaticamente artigos científicos recebidos por diferentes canais, classificando relevância, extraindo metadados úteis e encaminhando cada item para armazenamento, revisão humana ou descarte controlado.

---

## 2. Problema que ele resolve

Pesquisadores, grupos de estudo e bibliotecas digitais recebem grande volume de artigos e precisam identificar rapidamente quais documentos merecem atenção. O processo manual é lento, sujeito a inconsistência e dificulta rastrear por que um artigo foi priorizado ou rejeitado.

---

## 3. Usuários-alvo

- Pesquisadores e estudantes que fazem curadoria de referências.
- Bibliotecários e assistentes de laboratório.
- Coordenadores de grupos de pesquisa que precisam filtrar leituras.

---

## 4. Contexto de uso

O agente será usado quando novos artigos precisarem de triagem. O fluxo deve funcionar como uma camada de triagem antes da leitura completa ou da inclusão em uma base de conhecimento.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Título, resumo, palavras-chave, DOI, fonte e, quando disponível, texto parcial ou metadados bibliográficos |
| **Formato da entrada** | JSON recebido por webhook ou payload de integração |
| **Saída** | Classificação de relevância, metadados extraídos, nível de confiança, decisão de roteamento e justificativa |
| **Formato da saída** | JSON estruturado e notificação em tempo real via Telegram Bot |

---

## 6. Limites do agente

### O que o agente faz:

- Classifica artigos por relevância temática e decide automaticamente o roteamento.
- Roteia automaticamente: artigos muito relevantes -> notificar aprovação; moderados -> notificar para revisão humana; não relevantes -> notificar rejeição.
- Extrai metadados bibliográficos e tópicos de forma estruturada.
- Detecta sinais de baixa confiança e notifica para revisão humana (com justificativa).
- Notifica todas as decisões de roteamento em tempo real via Telegram Bot.
- O roteamento influencia diretamente o fluxo do n8n (caminhos diferentes e notificação no Telegram).


### O que o agente NÃO faz:

- Não confirma originalidade, validade científica ou impacto real (isso é responsabilidade de revisores).
- Não inventa citações, DOI ou autores (apenas usa dados fornecidos ou valida com APIs externas).
- Não substitui julgamento editorial ou decisão de publicação (que é sempre humana).

---

## 7. Critérios de aceitação

- [x] O fluxo classifica artigos com saída estruturada.
- [x] O agente influencia a decisão de roteamento no n8n.
- [x] Existem caminhos diferentes para alta e baixa confiança.
- [x] As decisões ficam registradas para auditoria.
- [x] Há fallback quando a IA falha ou a entrada é insuficiente.

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Classificação incorreta por resumo ambíguo | Média | Alto | Usar confiança mínima e revisão humana para casos duvidosos |
| Metadados incompletos ou inconsistentes | Média | Médio | Validar com Crossref antes de persistir |
| Alucinação de DOI/autores | Média | Alto | Proibir criação de metadados não verificados |
| Duplicidade de artigos | Média | Médio | Verificar título, DOI e similaridade semântica |

---

## 9. Evidências necessárias

- [x] Exportação do workflow n8n em JSON.
- [x] Prints ou logs demonstrando a classificação.
- [x] Registro da decisão notificado via Telegram Bot.
- [x] Evidência de fallback para baixa confiança.
- [x] Documento ADR com comparação das alternativas.
