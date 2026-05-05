# Solution-A — Prompt Simples

**Abordagem:** Uma única chamada à IA para classificar e extrair informações. O resultado influencia diretamente o roteamento do fluxo.

## Fluxo

```
Webhook → Validar entrada → OpenAI (classificar) → Switch (urgência) → 
  ├── Alta urgência → Email + Google Sheets
  ├── Média/Baixa urgência → Google Sheets
  └── Confiança baixa / inválido → Fallback + Google Sheets
```

## Vantagens
- Simples de entender e manter
- Custo baixo (uma chamada à API por chamado)
- Fácil de depurar no n8n

## Desvantagens
- Sem enriquecimento das respostas automáticas
- Depende 100% da qualidade do prompt

## Adequação
Suficiente para o escopo do projeto. **Solução escolhida como base final.**
