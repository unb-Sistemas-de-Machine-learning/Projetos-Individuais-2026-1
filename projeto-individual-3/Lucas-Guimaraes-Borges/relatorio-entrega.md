# Relatório de Entrega — Projeto Individual 3: Automação com n8n e Agentes de IA

> **Aluno(a):** Lucas Guimarães Borges  
> **Matrícula:** 222015159  
> **Data de entrega:** 05/05

---

## 1. Resumo do Projeto

Este projeto implementa uma automação inteligente para triagem de e-mails de suporte da Codzz usando n8n como orquestrador e IA como mecanismo de decisão. O fluxo recebe e-mails via IMAP, normaliza os campos essenciais, classifica a demanda em categoria operacional, atribui urgência numérica (0 a 10) e gera um resumo curto para atendimento. A decisão da IA direciona o roteamento condicional, com persistência dos resultados no Supabase para auditoria. Também foram prototipadas três abordagens (simples, com base de conhecimento e multi-etapas com validação/fallback), comparadas por custo, qualidade e risco. O principal resultado foi a consolidação de um fluxo rastreável, com testes automatizados, benchmark e evidências de execução, reduzindo esforço manual na triagem inicial.

---

## 2. Problema Escolhido

A operação de suporte recebe e-mails em linguagem natural, com conteúdo heterogêneo e múltiplas intenções. Sem triagem automática, o encaminhamento manual aumenta tempo de resposta, inconsistência na priorização e chance de erro operacional. O cenário é relevante porque impacta diretamente SLA de atendimento e experiência do cliente.

---

## 3. Desenho do Fluxo

O workflow no n8n foi implementado para capturar e-mails, extrair os campos necessários, aplicar classificação com IA e rotear ações por categoria.

```text
Entrada IMAP → Settings (normalização) → AI Agent + Structured Output Parser
→ Edit Fields → Switch (roteamento por categoria) → Notificações
                           ↘ Persistência no Supabase
```

### 3.1 Nós utilizados

| Nó | Tipo | Função no fluxo |
|----|------|-----------------|
| Email Trigger (IMAP) | `emailReadImap` | Ler e-mail de entrada |
| Settings | `set` | Normalizar `assunto`, `conteudo` e metadados |
| AI Agent | `@n8n/n8n-nodes-langchain.agent` | Classificar categoria, urgência e resumo |
| Structured Output Parser | `outputParserStructured` | Garantir JSON estruturado |
| Edit Fields | `set` | Mapear saída da IA para campos operacionais |
| Switch | `switch` | Direcionar fluxo por categoria |
| Create a row | `supabase` | Registrar rastreabilidade em banco |
| sendMessage* | `httpRequest` | Notificar canais externos por tipo de demanda |

---

## 4. Papel do Agente de IA

O agente de IA é responsável por decisão não trivial de triagem e priorização, não apenas geração de texto.

- **Modelo/serviço utilizado:** OpenAI Chat Model (nó `lmChatOpenAi`) com parser estruturado
- **Tipo de decisão tomada pela IA:** classificação de categoria, estimação de urgência e sumarização
- **Como a decisão da IA afeta o fluxo:** define o caminho no `Switch`, a prioridade operacional e o conteúdo de notificação/persistência

---

## 5. Lógica de Decisão

O fluxo implementa roteamento condicional baseado na categoria devolvida pelo agente.

- **Condição 1:** `categoria == "suporte tecnico"` ou `categoria == "bug no sistema"`
  - Caminho A → notificação técnica (`sendMessage3`)
  - Caminho B → seguir para outros caminhos, se não corresponder
- **Condição 2:** `categoria == "financeiro"` ou `categoria == "cancelamento"`
  - Caminho A → notificação financeira/conta (`sendMessage`)
  - Caminho B → fallback para notificação geral (`sendMessage1`)

---

## 6. Integrações

| Serviço | Finalidade |
|---------|------------|
| IMAP | Captura de e-mails de entrada |
| OpenAI | Classificação inteligente e resumo |
| Supabase | Persistência de categoria, urgência e resumo |
| API HTTP externa | Envio de notificações por categoria |

---

## 7. Persistência e Rastreabilidade

As entradas e decisões são armazenadas na tabela `suporte` no Supabase (categoria, urgência, resumo e e-mail remetente). O workflow exportado, os testes e as evidências em `docs/evidence/` permitem auditoria técnica da execução e da decisão arquitetural.

---

## 8. Tratamento de Erros e Limites

- **Falhas da IA:** uso de parser estruturado e fallback de fluxo para categoria residual
- **Entradas inválidas:** normalização inicial no nó `Settings` e tratamento por caminho genérico
- **Fallback (baixa confiança):** na comparação de soluções, a solução final proposta (Solution C) prevê escalonamento humano para baixa confiança

---

## 9. Diferenciais implementados

- [ ] Memória de contexto
- [x] Multi-step reasoning
- [x] Integração com base de conhecimento
- [ ] Uso de embeddings / busca semântica

---

## 10. Limitações e Riscos

Mensagens curtas, ambíguas ou com múltiplas intenções podem gerar classificação subótima. Há também dependência de serviços externos (IMAP, OpenAI, Supabase e API de notificação), o que pode causar falhas de integração. O risco principal é encaminhamento incorreto em casos limítrofes, mitigado com documentação de fallback e trilha de auditoria.

---

## 11. Como executar

```bash
# 1. Importar o workflow no n8n
# arquivo: src/workflows/fluxo_n8n_agente_email.json

# 2. Configurar credenciais necessárias
# IMAP, OpenAI, Supabase e endpoint HTTP de notificação

# 3. Ativar o workflow

# 4. Enviar uma entrada de teste por e-mail para a caixa monitorada

# 5. Validar resultados
python -m unittest discover -s tests -p "test_*.py" -v
python src/run_benchmark.py
```

---

## 12. Referências

1. [Documentação oficial do n8n](https://docs.n8n.io/)
2. [OpenAI Platform Documentation](https://platform.openai.com/docs)
3. [Vídeo de demonstração do fluxo](https://youtu.be/mlclCzgOFtY)

---

## 13. Checklist de entrega

- [x] Workflow exportado do n8n (.json)
- [x] Código/scripts auxiliares incluídos
- [x] Demonstração do fluxo (vídeo ou prints)
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto

