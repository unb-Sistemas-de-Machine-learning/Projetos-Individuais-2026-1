# Mission Brief

> **Aluno(a):** Patricia Helena Macedo da Silva
> **Matrícula:** 221037993
> **Domínio:** Triagem automática de chamados de suporte técnico

---

## 1. Objetivo do agente

Automatizar a **triagem inicial** de pedidos de suporte técnico: classificar o tipo de problema, estimar **urgência** e **confiança** da classificação, **rotear** o chamado (escalação imediata, resposta orientada por FAQ ou revisão humana) e **registrar** tudo para auditoria.

---

## 2. Problema que ele resolve

Usuários enviam mensagens vagas ou misturadas (“não consigo entrar”, “está lento”). Sem triagem, tudo cai na mesma fila ou o time perde tempo com casos repetitivos. O agente de IA **estrutura** a demanda e o fluxo n8n **decide** o próximo passo com base nessa estrutura — não apenas gera texto solto.

---

## 3. Usuários-alvo

- **Usuários finais** de um sistema interno ou produto (funcionários, alunos ou clientes internos).
- **Equipe de suporte** que recebe escalonamentos e revisões priorizadas.

---

## 4. Contexto de uso

Canal assíncrono: formulário ou sistema envia **POST** para um **Webhook** do n8n (simula ticket por e-mail/chat). O processamento deve ser **rápido**, **registrado** em planilha e, em casos críticos, **notificar** um canal (ex.: Telegram) configurado pelo operador.

---

## 5. Entradas e saídas esperadas


| Item                   | Descrição                                                                               |
| ---------------------- | --------------------------------------------------------------------------------------- |
| **Entrada**            | Corpo JSON com pelo menos `message` (texto do chamado). Opcional: `email`, `userId`.    |
| **Formato da entrada** | `{ "message": "...", "email": "..." }`                                                  |
| **Saída**              | JSON de resposta ao cliente + linha de log em Google Sheets com rota e resumo da IA.    |
| **Formato da saída**   | Resposta HTTP JSON: `status`, `rota`, `resumo_ia`, `orientacao` (texto para o usuário). |


---

## 6. Limites do agente

### O que o agente faz:

- Classificar em categorias de suporte (acesso, performance, erro, dúvida de uso, outro).
- Estimar urgência (baixa, média, alta) e confiança (alta, baixa).
- Sugerir uma **primeira orientação** com base em FAQ quando a confiança for razoável.
- Acionar rotas automáticas de escalação ou revisão conforme regras.

### O que o agente NÃO deve fazer:

- Não acessar sistemas internos reais (LDAP, banco de produção) sem integração explícita aprovada.
- Não prometer prazos ou garantias legais.
- Não armazenar senhas ou dados sensíveis além do necessário para o ticket (evitar CPis completos em log).

---

## 7. Critérios de aceitação

- Workflow n8n importável, com múltiplos nós e **decisão condicional** baseada na saída estruturada da IA.
- Integração real (Google Sheets e, quando configurado, Telegram ou e-mail).
- Persistência de entrada + decisão + rota em **Sheets**.
- Tratamento de entrada inválida e de falha/ambiguidade da IA (rota de revisão ou mensagem segura).

---

## 8. Riscos


| Risco                                 | Probabilidade | Impacto | Mitigação                                                                  |
| ------------------------------------- | ------------- | ------- | -------------------------------------------------------------------------- |
| Classificação errada (urgência falsa) | Média         | Alto    | Rota “revisão humana” quando `confianca` é baixa; revisão manual amostral. |
| Falha da API Gemini                   | Baixa         | Médio   | Mensagem de erro ao cliente + log em Sheets com `erro_api`.                |
| Vazamento de dados em logs            | Baixa         | Alto    | Não logar texto completo se política exigir; truncar em produção.          |


---

## 9. Evidências necessárias

- [x] Prints do workflow ativo e de até **3 testes** (alta urgência, baixa com FAQ, entrada inválida).
- [x] Export JSON do workflow na pasta `src/workflows/`.
- [x] Planilha de exemplo com linhas de auditoria (pode ser print).
- [x] Relatório técnico preenchido (`docs/relatorio-entrega.md`).

