# Merge-Readiness Pack — Agente de Triagem Jurídica (CDC)

## Resumo da solução escolhida

A solução final escolhida foi a **Solution C**, baseada em um fluxo agêntico multicanal no n8n.

O sistema atua como um triador inteligente que:

- Recebe reclamações de consumo  
- Identifica o embasamento legal no CDC  
- Executa ações automáticas (notificações ou registros) dependendo da gravidade do relato  

---

## Fluxo Final

- **Entrada:** Captura de dados via n8n Form  
- **Inteligência:** IA (Gemini) analisa o texto e gera um JSON estruturado  
- **Normalização:** Nó de código limpa a resposta da IA  
- **Roteamento (Switch):**
  - **URGENTE:** Envia alerta via Telegram e salva no Google Sheets  
  - **DUVIDA:** Envia orientação via Gmail e salva no Google Sheets  
  - **PADRÃO / INVÁLIDO:** Registra no Google Sheets para auditoria  

---

## Comparação entre alternativas

| Critério               | Solution A        | Solution B             | Solution C                     |
|-----------------------|------------------|------------------------|--------------------------------|
| Abordagem             | Prompt simples   | Base de Conhecimento   | Fluxo Agêntico Multicanal     |
| Complexidade          | Baixa            | Média                  | Alta                           |
| Qualidade da Decisão  | Média            | Boa                    | Alta                           |
| Ação Automática       | Não              | Não                    | Sim (Telegram/Gmail)          |
| Rastreabilidade       | Baixa            | Média                  | Alta (Google Sheets)          |
| Solução Final         | Não              | Não                    | Sim                           |

---

## Testes Executados

### Teste 1 — Urgência Crítica (Corte de Energia)

- **Entrada:** Relato de corte de luz indevido com contas pagas  
- **Resultado esperado:**  
  - IA classifica como URGENTE  
  - Cita Art. 22 do CDC  
  - Dispara mensagem no Telegram  

---

### Teste 2 — Dúvida Simples (Arrependimento)

- **Entrada:** Pergunta sobre prazo de devolução de compra online  
- **Resultado esperado:**  
  - IA identifica Art. 49  
  - Classifica como DUVIDA  
  - Envia e-mail explicativo via Gmail  

---

### Teste 3 — Entrada Inválida

- **Entrada:** Texto sem sentido ou muito curto ("Oi")  
- **Resultado esperado:**  
  - Sistema classifica como INVALIDO  
  - Apenas registra no log  
  - Nenhuma notificação é disparada  

---

## Evidências de Funcionamento

As evidências estão organizadas na pasta:

Arquivos incluídos:

- `workflow-completo.png`: Visão geral do fluxo no n8n  
- `telegram-alert.png`: Notificação de urgência recebida  
- `gmail-outbox.png`: Registro do e-mail enviado  
- `google-sheets-log.png`: Auditoria dos casos testados  

---

## Limitações Conhecidas

- A precisão da citação dos artigos depende da clareza do relato do usuário  
- O sistema depende de conectividade com APIs externas (Telegram e Google)  
- A classificação de "URGENTE" é limitada a serviços essenciais e saúde  

---

## Decisões Arquiteturais

- n8n como orquestrador principal  
- Gemini 3 Flash como motor de decisão  
- Telegram para alertas críticos (baixa latência)  
- Gmail para respostas automatizadas  
- Google Sheets como mecanismo de persistência e auditoria  

---

## Instruções de Execução

1. Importar o arquivo `workflow-cdc-triagem.json`  
2. Configurar as credenciais:
   - Google Gemini  
   - Telegram Bot  
   - Gmail  
   - Google Sheets  
3. Abrir o formulário gerado pelo nó **On form submission**  
4. Submeter os casos de teste  
5. Validar as saídas nos canais correspondentes  

---

## Checklist de Revisão

- [x] agent.md configurado no nó AI Agent  
- [x] Nó de parsing validando o JSON da IA  
- [x] Roteamento condicional funcionando  
- [x] Persistência em Google Sheets estruturada  
- [x] Integrações externas (Telegram e Gmail) testadas  

---

## Justificativa para Merge

A solução está pronta para entrega pois demonstra o uso efetivo de IA como mecanismo de decisão dentro de um fluxo automatizado.

O sistema:

- Classifica demandas com base em critérios jurídicos  
- Executa ações automáticas conforme a criticidade  
- Mantém rastreabilidade completa das decisões  

Atende integralmente aos requisitos de:

- Automação  
- Integração  
- Uso de IA para decisão  
- Persistência e auditoria  