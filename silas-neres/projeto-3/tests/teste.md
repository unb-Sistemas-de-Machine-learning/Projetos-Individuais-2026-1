Aqui está o documento formatado em Markdown (**MD**), pronto para ser salvo como `test-cases.md` no seu repositório:

---

# Casos de Teste — Agente de Triagem Jurídica (CDC)

Este documento detalha os cenários de teste executados para validar a lógica de classificação, o embasamento legal e o roteamento de ações do sistema de triagem baseado no Código de Defesa do Consumidor.

---

## Caso 1 — Entrada Inválida (Texto Insuficiente)

### Entrada
```json
{
  "nome_consumidor": "silas",
  "descricao_problema": "Oi, tudo bem?"
}
```

### Resultado Observado
*   **Análise**: O relato apresenta apenas 4 palavras, o que aciona a regra de segurança para textos com menos de 10 palavras.
*   **Classificação da IA**: `INVALIDO`.
*   **Artigo Identificado**: `artigo_nao_identificado`.
*   **Ação Sugerida**: `arquivar`.
*   **Rota Executada**: Registro no Google Sheets como inválido para posterior revisão humana.

---

## Caso 2 — Reclamação Padrão (Direito de Arrependimento)

### Entrada
```json
{
  "nome_consumidor": "Silas",
  "descricao_problema": "Comprei um produto pela internet, me arrependi e a loja se recusa a devolver meu dinheiro e aceitar o produto de volta."
}
```

### Resultado Observado
*   **Categoria**: `RECLAMACAO_PADRAO`.
*   **Artigo Identificado**: `Artigo 49` (Direito de Arrependimento) e possivelmente `Artigo 35` (Descumprimento de Oferta).
*   **Confiança**: `0,95`.
*   **Resumo Jurídico**: O consumidor busca exercer o direito de arrependimento em compra realizada fora do estabelecimento comercial.
*   **Ação Sugerida**: `responder_email`.
*   **Rota Executada**: Envio de e-mail automático via Gmail e registro na planilha de reclamações padrão.

---

##  Caso 3 — Urgência Crítica (Serviço Essencial)

### Entrada
```json
{
  "nome_consumidor": "roberto",
  "descricao_problema": "Minha energia elétrica foi cortada mesmo com as contas pagas no débito automático."
}
```

### Resultado Observado
*   **Categoria**: `URGENTE`.
*   **Artigo Identificado**: `Art. 22` (Continuidade de Serviços Essenciais).
*   **Resumo Jurídico**: Suspensão indevida de serviço essencial com quitação comprovada, violando o dever de continuidade previsto no CDC.
*   **Ação Sugerida**: `notificar_imediato`.
*   **Rota Executada**: Disparo de alerta via **Telegram** para a equipe de plantão e registro priorizado no Google Sheets.

---

##  Caso 4 — Vício de Qualidade (Produto Defeituoso)

### Entrada
```json
{
  "nome_consumidor": "geislaine",
  "descricao_problema": "O produto que comprei parou de funcionar dentro da garantia e o fabricante não resolve."
}
```

### Resultado Observado
*   **Categoria**: `RECLAMACAO_PADRAO`.
*   **Artigo Identificado**: `Artigo 18` (Vício de Qualidade).
*   **Confiança**: `0,98`.
*   **Justificativa**: Conforme o Art. 18 do CDC, o fornecedor tem o prazo de 30 dias para sanar o vício em bens duráveis.
*   **Ação Sugerida**: `responder_email`.
*   **Rota Executada**: Registro no Google Sheets e encaminhamento para fila de atendimento por e-mail.