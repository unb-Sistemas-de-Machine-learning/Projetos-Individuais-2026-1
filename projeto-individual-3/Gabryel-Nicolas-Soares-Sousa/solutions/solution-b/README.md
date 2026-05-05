# Solution-B — Com Base de Conhecimento (FAQ)

**Abordagem:** Igual à solution-a, mas chamados de baixa urgência consultam uma planilha de FAQ no Google Sheets antes de enviar a resposta automática ao usuário.

## Fluxo

```
Webhook → Validar entrada → OpenAI (classificar) → Switch (urgência) →
  ├── Alta urgência → Email + Google Sheets
  ├── Média/Baixa urgência → Consultar FAQ (Sheets) → Resposta automática + Sheets
  └── Confiança baixa → Fallback + Google Sheets
```

## Vantagens
- Respostas automáticas mais úteis para o usuário
- Reduz necessidade de intervenção humana em casos simples

## Desvantagens
- Depende de manutenção contínua da base de FAQ
- Maior complexidade no fluxo
- FAQ desatualizado pode gerar respostas incorretas

## Adequação
Boa para produção real, mas excessiva para o escopo acadêmico. **Descartada.**
