# Mission Brief

> **Aluno(a):** Gabryel Nicolas Soares de Sousa
> **Matrícula:** 221022570
> **Domínio:** Suporte técnico e atendimento ao cliente

---

## 1. Objetivo do agente

Automatizar a triagem de chamados de suporte recebidos via webhook, classificando cada demanda por categoria e urgência e direcionando automaticamente o fluxo para a ação adequada — notificação por email ou registro no Google Sheets — sem intervenção humana no caminho padrão.

---

## 2. Problema que ele resolve

Equipes de suporte recebem mensagens de diferentes naturezas e urgências ao longo do dia. A triagem manual é lenta, sujeita a erros e atrasa o atendimento, especialmente em situações críticas. O agente resolve esse gargalo classificando cada chamado automaticamente e garantindo que demandas urgentes sejam escaladas imediatamente, enquanto as demais são registradas para acompanhamento.

---

## 3. Usuários-alvo

- Analistas e gestores de equipes de suporte técnico
- Times de atendimento ao cliente que recebem alto volume de chamados
- Administradores que precisam de visibilidade e rastreabilidade sobre as demandas recebidas

---

## 4. Contexto de uso

O sistema é acionado toda vez que uma nova mensagem chega via webhook, simulando o recebimento de um formulário web ou integração de chat. O agente processa a mensagem em tempo real e o n8n executa a ação correspondente automaticamente. O fluxo opera de forma contínua, sem necessidade de intervenção humana no caminho padrão.

---

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Mensagem de texto enviada pelo usuário via requisição HTTP POST |
| **Formato da entrada** | JSON com os campos `mensagem` (string), `nome` (string) e `email` (string) |
| **Saída** | Classificação estruturada da demanda + ação executada (email ou registro) |
| **Formato da saída** | JSON com os campos `categoria`, `urgencia`, `resumo` e `confianca` |

---

## 6. Limites do agente

### O que o agente faz:
- Recebe e valida a mensagem de entrada
- Classifica a demanda em uma das categorias: `suporte_tecnico`, `financeiro`, `comercial`, `outros`
- Define o nível de urgência: `alta`, `media` ou `baixa`
- Gera um resumo objetivo da demanda com até 100 caracteres
- Indica o nível de confiança da classificação
- Direciona o fluxo com base na urgência e confiança

### O que o agente NÃO deve fazer:
- Responder diretamente ao usuário com conteúdo gerado pela IA
- Acessar ou modificar dados em sistemas externos além do Google Sheets
- Tomar decisões de negócio (aprovar reembolsos, conceder acessos, etc.)
- Classificar em categorias fora das quatro definidas
- Inventar informações que não estejam na mensagem original

---

## 7. Critérios de aceitação

- [ ] Mensagens recebidas via webhook são classificadas corretamente em ≥ 80% dos casos de teste
- [ ] Chamados com urgência alta geram notificação por email em menos de 30 segundos
- [ ] Todos os chamados são registrados no Google Sheets independentemente do caminho executado
- [ ] Entradas inválidas ou com baixa confiança ativam o caminho de fallback sem quebrar o fluxo
- [ ] Falhas na API da IA são capturadas e registradas sem interromper o sistema

---

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| IA classifica incorretamente a urgência | Média | Alto | Fallback para revisão manual quando `confianca` for `baixa` |
| API da OpenAI indisponível | Baixa | Alto | Nó de tratamento de erro registra o caso no Sheets para revisão |
| Entrada com campo `mensagem` ausente | Média | Médio | Validação no nó IF antes de chamar a IA |
| Expiração do OAuth do Gmail | Baixa | Médio | Reautenticação manual nas credenciais do n8n |

---

## 9. Evidências necessárias

- [ ] Print do workflow completo no n8n com todos os nós visíveis
- [ ] Print da execução com chamado de alta urgência (email enviado)
- [ ] Print da execução com chamado de baixa urgência (apenas Sheets)
- [ ] Print da execução com entrada inválida (fallback ativado)
- [ ] Print do Google Sheets com registros dos chamados
- [ ] Workflow exportado em `src/workflow.json`
