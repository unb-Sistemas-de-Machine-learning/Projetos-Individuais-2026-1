# Agente de Extração de Dados Open Source com Foco em Privacidade (LGPD)

## Resumo do Projeto
Este projeto visa desenvolver um agente de Inteligência Artificial capaz de extrair metadados de projetos de software open source, com foco principal em analisar tendências de licenciamento e adoção, garantindo estritamente a conformidade com a Lei Geral de Proteção de Dados (LGPD).

## Domínio
Open Source / Comunidades

## Função do Agente
Extração de Dados

## Restrição Obrigatória
Privacidade (LGPD)

## Objetivo Principal
Analisar a adoção e as tendências de licenças de software open source em projetos recém-criados em plataformas como GitHub, sem coletar ou processar dados pessoais identificáveis dos contribuidores.

## Fontes de Dados
*   API do GitHub (principal)

## Escopo e Formato dos Dados
Serão extraídos metadados públicos de projetos (nome do repositório, data de criação, linguagem principal, licença, descrição curta, estrelas, forks). A saída será em formato JSON, contendo apenas informações não pessoais.

## Estratégia de Conformidade com a LGPD
Foco em minimização de dados, extração de metadados não pessoais, e revisão contínua para evitar a coleta acidental de informações identificáveis.

## Modelo Open Source
Licença: MIT. Diretrizes de contribuição serão definidas conforme avanço do projeto.

## Requisitos Gerais do Projeto
- Seu projeto está localizado na pasta `ingrid-soares/projeto-1/` dentro deste repositório.
- Não fazer push direto para a branch principal; utilizar Pull Requests.
- Detalhar requisitos, arquitetura e implementação.

## Status Atual
As especificações iniciais (domínio, função, restrição, fontes, escopo, LGPD, modelo open source) foram definidas. A próxima etapa é a arquitetura detalhada e a implementação do protótipo.

---
**Observação:** Este README será atualizado conforme o projeto evolui.
