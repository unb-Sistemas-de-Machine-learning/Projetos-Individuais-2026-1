# Mission Brief

> **Aluno:** Lucas Guimarães Borges  
> **Domínio:** Suporte por e-mail para SaaS (Codzz)

## 1. Objetivo do agente

Automatizar a triagem inicial de e-mails de suporte, transformando texto livre em dados estruturados para roteamento rápido no n8n.

## 2. Problema que ele resolve

O suporte recebe mensagens heterogêneas e sem padrão, o que aumenta tempo de resposta e chance de encaminhamento incorreto.

## 3. Usuários-alvo

- Time de suporte técnico
- Time financeiro
- Operação de atendimento da Codzz

## 4. Contexto de uso

Fluxo assíncrono de caixa de entrada compartilhada (`suporte@codzz.com.br`) com alto volume e necessidade de priorização.

## 5. Entradas e saídas esperadas

| Item | Descrição |
|------|-----------|
| **Entrada** | Assunto e conteúdo do e-mail |
| **Formato da entrada** | Texto UTF-8 vindo do trigger IMAP |
| **Saída** | Categoria, urgência e resumo |
| **Formato da saída** | JSON estruturado |

## 6. Limites do agente

### O que o agente faz:

- Classifica intenção principal do e-mail
- Estima urgência de 0 a 10
- Gera resumo curto para o atendente
- Sinaliza casos para escalonamento humano

### O que o agente NAO deve fazer:

- Responder o cliente com informação jurídica/financeira definitiva
- Alterar dados de cobrança diretamente
- Ignorar incerteza alta

## 7. Critérios de aceitação

- [x] Classificação em categoria permitida
- [x] Urgência coerente com o impacto
- [x] Resumo claro em português
- [x] Fluxo roteia casos para caminho correto

## 8. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Classificação incorreta | Média | Alto | Fallback para humano quando confiança baixa |
| Mensagem ambígua | Alta | Médio | Solicitar complemento e não auto-resolver |
| Falha de integração externa | Média | Médio | Retry + registro para reprocessamento |

## 9. Evidências necessárias

- [x] Workflow n8n exportado
- [x] Três soluções prototipadas
- [x] Testes automatizados passando
- [x] ADR com justificativa da escolha final

