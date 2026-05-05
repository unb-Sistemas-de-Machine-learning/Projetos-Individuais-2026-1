# Casos de Teste (execução manual)

> Projeto: Triagem de suporte técnico com n8n + Gemini  
> Aluna: Patricia Helena Macedo da Silva  
> Matrícula: 221037993

---

## Instruções rápidas

1. Executar cada caso no n8n via webhook da solução correspondente.
2. Conferir resposta HTTP, execução no n8n e linha criada na aba `Tickets`.
3. Preencher a coluna **Resultado obtido** e marcar **Status**.

Legenda de status:

- `[ ]` Não executado
- `[x]` Passou
- `[!]` Falhou

---

## Solução A — Prompt único + roteamento


| ID   | Entrada (JSON)                                                                              | Resultado esperado                                                                        | Resultado obtido (preencher manualmente) | Status |
| ---- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| A-01 | `{"message":"Esqueci minha senha de acesso.","email":"teste.a1@empresa.com"}`               | `ok: true`; rota coerente (`auto` ou `revisao`); linha criada em `Tickets`.               |                                          | [x]    |
| A-02 | `{"message":"O sistema caiu para todo o setor financeiro.","email":"teste.a2@empresa.com"}` | `ok: true`; urgência tendendo a `alta` ou rota de priorização; linha criada em `Tickets`. |                                          | [x]    |
| A-03 | `{"message":"oi","email":"teste.a3@empresa.com"}`                                           | Entrada inválida; resposta de erro de validação; não deve seguir fluxo normal.            |                                          | [!]    |


---

## Solução B — RAG leve com FAQ (solução final)


| ID   | Entrada (JSON)                                                                                       | Resultado esperado                                                                                         | Resultado obtido (preencher manualmente) | Status |
| ---- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| B-01 | `{"message":"Esqueci minha senha, como redefinir?","email":"teste.b1@empresa.com"}`                  | `ok: true`; orientação deve refletir FAQ de senha; linha criada em `Tickets`.                              |                                          | [x]    |
| B-02 | `{"message":"A aplicacao esta lenta para toda a equipe desde cedo.","email":"teste.b2@empresa.com"}` | `ok: true`; classificação de performance/lentidão; orientação coerente com FAQ; linha criada em `Tickets`. |                                          | [x]    |
| B-03 | `{"message":"oi","email":"teste.b4@empresa.com"}`                                                    | Entrada inválida; resposta de erro de validação (`Respond Erro Validação`).                                |                                          | [!]    |


---

## Solução C — Multi-etapas (classificar -> redigir -> validar rota)


| ID   | Entrada (JSON)                                                                                                             | Resultado esperado                                                                      | Resultado obtido (preencher manualmente) | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| C-01 | `{"message":"Nao consigo acessar o sistema e preciso finalizar uma entrega urgente hoje.","email":"teste.c1@empresa.com"}` | `ok: true`; resposta com `modo: multietapas`; rota coerente; linha criada em `Tickets`. |                                          | [x]    |
| C-02 | `{"message":"Esqueci minha senha e fui bloqueada.","email":"teste.c2@empresa.com"}`                                        | `ok: true`; classificação e orientação coerentes; linha criada em `Tickets`.            |                                          | [x]    |
| C-03 | `{"message":"oi","email":"teste.c3@empresa.com"}`                                                                          | Entrada inválida; resposta de erro de validação.                                        |                                          | [!]    |


---

## Evidências associadas (preencher)

- Prints da Solução A:
  - [A-01-powershell-resposta.png](../docs/evidence/A-T1-powershell-resposta.png)
  - [A-01-sheets-linha-gerada.png](../docs/evidence/A-T1-sheets-linha-gerada.png)
  - [A-02-powershell-resposta.png](../docs/evidence/A-T2-powershell-resposta.png)
  - [A-02-sheets-linha-gerada.png](../docs/evidence/A-T2-sheets-linha-gerada.png)
  - [A-03-n8n-respond-erro-validacao.png](../docs/evidence/A-T3-n8n-respond-erro-validacao.png)
  - [A-03-powershell-resposta-invalida.png](../docs/evidence/A-T3-powershell-resposta-invalida.png)

- Prints da Solução B:
  - [B-01-powershell-resposta.png](../docs/evidence/B-T1-powershell-resposta.png)
  - [B-01-sheets-linha-gerada.png](../docs/evidence/B-T1-sheets-linha-gerada.png)
  - [B-02-powershell-resposta.png](../docs/evidence/B-T2-powershell-resposta.png)
  - [B-02-sheets-linha-gerada.png](../docs/evidence/B-T2-sheets-linha-gerada.png)
  - [B-03-n8n-respond-erro-validacao.png](../docs/evidence/B-T3-n8n-respond-erro-validacao.png)
  - [B-03-powershell-resposta-invalida.png](../docs/evidence/B-T3-powershell-resposta-invalida.png)

- Prints da Solução C:
  - [C-01-powershell-resposta.png](../docs/evidence/C-T1-powershell-resposta.png)
  - [C-01-sheets-linha-gerada.png](../docs/evidence/C-T1-sheets-linha-gerada.png)
  - [C-02-powershell-resposta.png](../docs/evidence/C-T2-powershell-resposta.png)
  - [C-02-sheets-linha-gerada.png](../docs/evidence/C-T2-sheets-linha-gerada.png)
  - [C-03-n8n-respond-erro-validacao.png](../docs/evidence/C-T3-n8n-respond-erro-validacao.png)
  - [C-03-powershell-resposta-invalida.png](../docs/evidence/C-T3-powershell-resposta-invalida.png)

---