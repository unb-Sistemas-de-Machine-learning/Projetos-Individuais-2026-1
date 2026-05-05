# Mission Brief — Triagem Inteligente de Chamados de Suporte

**Projeto:** Projeto Individual 3 — Automação com n8n e Agentes de IA  
**Aluno:** Gabryel Nicolas Soares de Sousa  
**Matrícula:** 221022570  
**Data:** 05/05/2025

---

## 1. Objetivo do Agente

Automatizar a triagem de chamados de suporte recebidos via webhook, utilizando um agente de IA para classificar a demanda, extrair informações relevantes e direcionar o fluxo automaticamente para a ação adequada.

---

## 2. Problema que Resolve

Equipes de suporte recebem diariamente mensagens de diferentes naturezas (técnico, financeiro, comercial) e urgências variadas. A triagem manual é lenta, sujeita a erros e atrasa o atendimento. Este agente automatiza essa classificação e roteamento, garantindo que chamados urgentes sejam escalados imediatamente e os demais registrados adequadamente.

---

## 3. Usuários-Alvo

- Equipes de suporte técnico e atendimento ao cliente
- Gestores que precisam de visibilidade sobre os chamados recebidos
- Analistas que auditam o histórico de atendimentos

---

## 4. Contexto de Uso

O sistema é acionado toda vez que uma nova mensagem chega via webhook (simulando um formulário web ou integração de chat). O agente de IA processa a mensagem e o n8n executa automaticamente a ação correspondente, sem intervenção humana no fluxo padrão.

---

## 5. Entradas e Saídas Esperadas

### Entrada
```json
{
  "mensagem": "Meu acesso ao sistema não está funcionando desde ontem",
  "nome": "João Silva",
  "email": "joao@empresa.com"
}
```

### Saída da IA (JSON estruturado)
```json
{
  "categoria": "suporte_tecnico",
  "urgencia": "alta",
  "resumo": "Usuário sem acesso ao sistema há mais de 24h",
  "confianca": "alta"
}
```

### Ação executada pelo n8n
- **Alta urgência:** Envia email de alerta + registra no Google Sheets
- **Baixa urgência:** Registra no Google Sheets + envia resposta automática
- **Confiança baixa / inválido:** Fallback com mensagem padrão + registro

---

## 6. Limites do Agente

- O agente classifica apenas nas categorias: `suporte_tecnico`, `financeiro`, `comercial`, `outros`
- O agente não acessa sistemas externos para verificar dados do usuário
- O agente não toma decisões além da classificação e extração de informações
- Mensagens vazias ou sem sentido são tratadas como inválidas

---

## 7. O que o Agente NÃO deve fazer

- Responder diretamente ao usuário com conteúdo gerado pela IA
- Acessar ou modificar dados em sistemas de produção
- Tomar decisões de negócio (ex: aprovar reembolsos, conceder acessos)
- Armazenar dados sensíveis além do necessário para auditoria

---

## 8. Critérios de Aceitação

- [ ] Mensagem recebida via webhook é classificada corretamente em ≥ 80% dos casos de teste
- [ ] Chamados de alta urgência geram notificação por email em menos de 30 segundos
- [ ] Todos os chamados são registrados no Google Sheets
- [ ] Entradas inválidas ativam o caminho de fallback sem quebrar o fluxo
- [ ] O fluxo no n8n executa sem erros manuais de intervenção

---

## 9. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| IA classifica incorretamente a urgência | Média | Alto | Fallback para revisão manual em casos de baixa confiança |
| API da OpenAI indisponível | Baixa | Alto | Nó de tratamento de erro com resposta padrão |
| Entrada malformada no webhook | Média | Médio | Validação do JSON antes de enviar à IA |
| Limite de requisições da API | Baixa | Médio | Rate limiting e retry automático |

---

## 10. Evidências para Considerar a Missão Concluída

- Print do workflow funcionando no n8n
- Print do Google Sheets com registros de chamados
- Print do email de notificação enviado
- Log de pelo menos 3 testes diferentes (urgência alta, baixa e entrada inválida)
- Workflow exportado em `.json`
