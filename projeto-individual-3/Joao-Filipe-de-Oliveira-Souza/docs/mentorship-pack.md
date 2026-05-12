# Mentorship Pack

> **Projeto:** Sistema de Triagem Automatica de Demandas Academicas
> **Aluno(a):** Joao Filipe de Oliveira Souza

---

## 1. Orientacoes de julgamento

- Priorizar previsibilidade do fluxo sobre criatividade da resposta da IA.
- Em caso de incerteza, escolher sempre o caminho mais seguro (fallback).
- Decisoes devem ser explicaveis com base em categoria, urgencia e confianca.

---

## 2. Padroes de arquitetura

- Arquitetura orientada a workflow no n8n com etapas claras: entrada, contexto, inferencia, validacao, persistencia e acao.
- Separar decisao da IA de regras deterministicas (limiar de confianca e roteamento).
- Integracoes externas devem acontecer depois da validacao e persistencia.

---

## 3. Padroes de codigo

- Linguagem: JSON de workflow n8n e expressoes n8n.
- Estilo: nomes de nos descritivos e parametros explicitos.
- Testes: validacao por execucao de casos de baixa/media/alta urgencia e verificacao das rotas.

---

## 4. Estilo de documentacao

- Descrever decisoes tecnicas antes de listar implementacao.
- Registrar regras de negocio em formato objetivo (tabelas/checklists).
- Sempre incluir riscos, limites e criterios de aceite.

---

## 5. Qualidade esperada

- Workflow reproduzivel com importacao direta no n8n.
- Roteamento funcional para os tres niveis de urgencia.
- Persistencia dos principais campos de classificacao.
- Artefatos obrigatorios do projeto preenchidos e consistentes.

---

## 6. Exemplos de boas respostas

```text
Exemplo 1:
"A confianca retornada foi 0.62. O fluxo marcou classificacao_valida=false,
forcou categoria_final='outro' e urgencia_final='media', e seguiu para
encaminhamento padrao com rastreabilidade preservada."
```

```text
Exemplo 2:
"Para urgencia alta, a automacao envia email de alta prioridade e inclui
resumo, acao sugerida e palavras-chave para acelerar o atendimento humano."
```

---

## 7. Exemplos de mas respostas

```text
Exemplo 1:
"A demanda parecia importante, entao defini urgencia alta manualmente"
(erro: ignora criterio explicito do fluxo e reduz auditabilidade).
```

```text
Exemplo 2:
"Nao sei classificar, mas vou enviar como suporte_tecnico para testar"
(erro: sem fallback seguro e sem transparencia de incerteza).
```

---

## 8. Principios-guia

```text
O agente deve explicar a decisao tecnica por campos estruturados.
O agente deve preferir solucoes simples, testaveis e observaveis.
O agente nao deve esconder incertezas de classificacao.
O agente deve manter trilha de auditoria das decisoes.
```
