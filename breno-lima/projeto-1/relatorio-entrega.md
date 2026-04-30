# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** Breno Queiroz Lima
> **Matrícula:** 211063069
> **Data de entrega:** 28/03/2026

---

## 1. Resumo do Projeto

O agente analisa as últimas mudanças realizadas no código e então gera um mensagem de commit

---

## 2. Combinação Atribuída

| Item                      | Valor |
| ------------------------- | ----- |
| **Domínio**               | 10    |
| **Função do agente**      | 3     |
| **Restrição obrigatória** |       |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

A entrada é o resultado de um `git diff --staged`

### 3.2 Processamento (Pipeline)

```
Resultado do diff -> agente -> git commit -e -m mensagem
```

### 3.3 Decisão

São utilizados dois prompts `You are a helpful assistant that summarizes git diffs into concise commit messages`.
E resultado do `git diff --staged`

### 3.4 Saída (Output)

Texto com uma mensagem de commit das últimas alterações do código.

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade          |
| ---------- | ------ | ------------------- |
| Python     | 3.14.3 | Linguagem principal |

### 4.2 Estrutura do código

```
projeto-1/
├── src/
│   ├── ...
├── requirements.txt
└── README.md
```

### 4.3 Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
`cp .env-dev .env`
adicionar api_key do Gemini

# 3. Executar
python src/main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
| ------- | --------- | ---------------- |
|         |           |                  |
|         |           |                  |

### 5.2 Exemplos de teste

As mensagens de commits feitas a partir do `01cc9ea4` foram geradas utilizando o agente.

### 5.3 Análise dos resultados

- As mensagens de commit geradas estavam de acordo com as mudanças feitas no código.
- É necessário definir melhor o contexto para que a mensagem sigam padrões de commits.

---

## 6. Diferenciais implementados

_Marque os diferenciais que foram implementados:_

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [x] Uso de ferramentas (tools)
- [ ] Memória persistente
- [ ] Explicabilidade
- [ ] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

- Fazer integração com outros modelos.
- Permitir definição de linguagem e padrões de commits.
- Adicionar suporte para arquivo de configurações.
- Adicionar loading.

---

## 8. Referências

1.
2.
3.

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [x] Pull Request aberto
