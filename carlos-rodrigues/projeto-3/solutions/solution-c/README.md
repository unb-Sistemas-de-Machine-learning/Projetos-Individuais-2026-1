# Solution C - Fluxo multi-etapas com validação

Abordagem recomendada para curadoria automática de artigos científicos.

## Ideia

Separar a curadoria em etapas: normalização da entrada, extração de metadados, classificação de relevância, validação externa, cálculo de confiança e roteamento para armazenamento ou revisão humana.

## Fluxo

1. Receber artigo ou metadados.
2. Normalizar campos obrigatórios.
3. Classificar relevância com IA.
4. Validar DOI, título e autores em API externa.
5. Calcular confiança final.
6. Roteamento condicional.
7. Notificar a decisão via Telegram Bot e escalar casos ambíguos para fila de revisão humana.

## Vantagens

- Mais robusta e auditável.
- Lida melhor com baixa confiança.
- Alinha automação com revisão humana.

## Limitações

- Mais nós e maior esforço de configuração.
- Exige integrações externas.
- Precisa de testes para cobrir falhas e fallback.
