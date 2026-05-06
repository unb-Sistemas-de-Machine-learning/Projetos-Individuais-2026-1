# Evidencias de funcionamento

## Exemplo 1

Entrada:

```text
Nao consigo acessar o portal da disciplina desde ontem, preciso urgente para enviar trabalho.
```

Saida esperada (resumo):

- categoria: suporte_tecnico
- urgencia: alta
- decisao: notificar_plantao ou executar_fluxo_padrao (dependendo da solucao)

## Exemplo 2

Entrada:

```text
Preciso da segunda via do boleto da mensalidade. Meu RA e 211061529.
```

Saida esperada (resumo):

- categoria: financeiro
- ra extraido: 211061529
- decisao: encaminhar para financeiro

## Exemplo 3

Entrada:

```text
Oi, tudo bem?
```

Saida esperada (resumo):

- categoria: indefinido
- confianca: baixa
- decisao: escalar_humano
