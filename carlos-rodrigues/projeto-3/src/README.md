# Scripts auxiliares

Este diretório contém pequenos scripts de suporte usados pelos workflows.

- `normalize.js`: traz funções de normalização e validação de metadados de artigos (título, resumo, DOI, palavras-chave) para preparar o payload antes do processamento.
- `solution-b-retriever.js`: servidor HTTP local simples que expõe um endpoint `/search` para consulta ao arquivo de conhecimento usado pela solução B (RAG). Use `node src/solution-b-retriever.js` para executar.

