# ADR-004: autoMapInputData + Code node de flatten para o Google Sheets

## Status
Aceito

## Contexto
O workflow precisa registrar uma linha no Google Sheets com 12 campos (timestamp,
issue_number, type, severity, etc.). O nó `n8n-nodes-base.googleSheets` oferece
dois modos de mapeamento de colunas: `defineBelow` e `autoMapInputData`.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| `mappingMode: "defineBelow"` com colunas explícitas no JSON | Mapeamento visível e auditável no arquivo `.json` | Exige `columns.schema` que o n8n popula via UI ao conectar à planilha real — não pode ser importado via JSON; causa erro `"Could not get parameter: columns.schema"` |
| `mappingMode: "autoMapInputData"` | Funciona ao importar via JSON; n8n mapeia automaticamente chaves do input aos cabeçalhos da planilha | Requer que os dados estejam no nível raiz do JSON (não aninhados) |

## Decisão

Usar **`autoMapInputData`** precedido de um Code node "Prepare Sheets Row" que achata
`sheets_row` do nível aninhado para o nível raiz do JSON.

```javascript
const row = $input.first().json.sheets_row;
return [{ json: row }];
```

Motivo: `defineBelow` falhou com erro `"Could not get parameter: columns.schema"`
ao importar o workflow via JSON — o schema só existe quando o nó é configurado
manualmente na UI do n8n conectado à planilha real. A abordagem com `autoMapInputData`
e flatten funciona sem configuração adicional após o import.

## Consequências

- A planilha deve ter os cabeçalhos na linha 1 com os nomes exatos:
  `timestamp`, `issue_number`, `title`, `url`, `type`, `severity`, `component`,
  `confidence`, `low_confidence`, `ai_flagged`, `summary`, `reasoning`
- O nó "Log to Sheets" ainda precisa ter o documento e a aba configurados
  manualmente na UI após importar (credencial OAuth + ID da planilha)
- Padrão deve ser replicado nas Solutions B e C

## Evidências
Erro `"Could not get parameter"` para `columns.schema` recebido ao executar o nó
Google Sheets após importar o workflow via JSON — confirmou que `defineBelow` não
é portável sem configuração via UI.
