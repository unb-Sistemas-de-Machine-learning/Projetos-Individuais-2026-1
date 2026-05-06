# Solution A — Triagem Simples via Prompt (MVP)

## Abordagem
A Solution A é a implementação mais básica do assistente. Ela utiliza o nó AI Agent para receber o relato do consumidor e gerar uma resposta direta. Não há separação de rotas ou lógica condicional complexa no n8n.

## Problema tratado
Validação da capacidade do modelo Gemini em compreender termos jurídicos do Código de Defesa do Consumidor (CDC) sem auxílio de ferramentas externas.

## Fluxo proposto
n8n Form Trigger → AI Agent (Gemini) → Google Sheets.

## Pontos Positivos
- Baixíssima complexidade técnica.
- Implementação em poucos minutos.
- Útil para validar se o "System Prompt" está sendo seguido.

## Limitações e Riscos
- **Inércia Operacional:** O fluxo não toma decisões automáticas (não envia e-mails ou alertas).
- **Risco de Alucinação:** Sem uma base de dados, a IA pode citar artigos do CDC incorretos.
- **Falta de Rastreabilidade:** Não há distinção entre casos urgentes e dúvidas simples na execução do fluxo.

## Motivo do Descarte
Foi descartada por ser passiva demais. O projeto exige que a IA influencie o fluxo, e na Solution A, ela apenas gera texto, deixando toda a carga de decisão para o humano que lerá a planilha..