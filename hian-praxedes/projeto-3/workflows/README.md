# Workflows n8n

Esta pasta contém o workflow exportado do n8n.

## Arquivo principal

agente-validacao-entrega-academica.json

## Descrição

O workflow implementa um agente de validação de entrega acadêmica usando n8n, Gemini e Google Sheets.

## Fluxo simplificado

Webhook
↓
Validar entrada
↓
Entrada válida?
├── false → Montar resultado inválido → Google Sheets
└── true → IA - Validar entrega
          ↓
          Normalizar IA
          ↓
          Precisa de correção?
          ├── true → Montar resultado pendente → Google Sheets
          └── false → Montar resultado ok → Google Sheets

## Integrações usadas

- Webhook para entrada.
- Gemini para classificação da entrega.
- Google Sheets para persistência e rastreabilidade.

## Como importar

1. Abrir o n8n.
2. Importar o arquivo `agente-validacao-entrega-academica.json`.
3. Configurar credenciais do Gemini.
4. Configurar credenciais do Google Sheets.
5. Executar os casos de teste descritos em `tests/casos-de-teste.md`.