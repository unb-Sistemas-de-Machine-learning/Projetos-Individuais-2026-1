# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** João Filipe de Oliveira Souza
> **Matrícula:** 231035141
> **Data de entrega:** 30/03/2026

---

## 1. Resumo do Projeto

O projeto resolve o problema da carga manual de análise de feedbacks estudantis em instituições de ensino. Foi desenvolvido um agente de IA que utiliza o Ollama para processamento local de linguagem natural, classificando comentários de alunos em sentimentos (Positivo, Negativo, Neutro) e gerando justificativas. O principal resultado é uma ferramenta que automatiza a triagem pedagógica respeitando integralmente a LGPD, uma vez que nenhum dado sensível sai da infraestrutura local do usuário.

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** | Educação |
| **Função do agente** | Análise de Sentimento |
| **Restrição obrigatória** | Privacidade (LGPD) |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

O agente recebe uma lista de textos (strings) estruturada em um arquivo JSON (`comentarios.json`), representando feedbacks reais de alunos sobre a experiência em sala de aula.

### 3.2 Processamento (Pipeline)

```
Entrada → Pré-processamento → LLM (Ollama) → Classificação → Geração de explicação → Saída
```
Pré-processamento: limpeza simples do texto (remoção de ruídos básicos)
LLM: interpretação do comentário
Classificação: definição do sentimento
Explicação: geração de justificativa simples

### 3.3 Decisão
A decisão do agente é baseada na interpretação semântica do comentário pelo modelo de linguagem, que identifica o tom predominante (positivo, negativo ou neutro).
O modelo considera palavras-chave, contexto e intenção do texto para determinar a classificação mais adequada, evitando decisões baseadas apenas em palavras isoladas.

### 3.4 Saída (Output)

A saída é estruturada em formato JSON ou exibida em tabela no terminal contendo:
- Comentário original
- Sentimento classificado
- Justificativa da classificação


---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia        | Versão | Finalidade                |
| ----------------- | ------ | ------------------------- |
| Python            | 3.10+  | Linguagem principal       |
| Ollama            | Última | Execução do modelo local  |
| Llama 3 / Mistral | -      | Modelo de linguagem       |
| JSON              | -      | Armazenamento de dados    |
| requests          | -      | Comunicação com API local |



### 4.2 Estrutura do código

```
joao-filipe-souza/
├── agente.ipynb
|── comentarios.json
```

### 4.3 Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar o Ollama
ollama run llama3.1

# 3. Executar o agente
python agent.ipynb
```


## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica  | Descrição                             | Resultado obtido |
| -------- | ------------------------------------- | ---------------- |
| Acurácia | Percentual de classificações corretas | 90%              |
| Latência | Tempo médio por comentário            | ~1.8 segundos    |

### 5.2 Exemplos de teste

#### Teste 1
- **Entrada:** "A aula foi excelente, gostei muito da didática"
- **Saída esperada:** Positivo
- **Saída obtida:** Positivo
- **Resultado:** Sucesso

#### Teste 2
- **Entrada:** "Não entendi nada da explicação"
- **Saída esperada:** Negativo
- **Saída obtida:** Negativo
- **Resultado:** Sucesso

### 5.3 Análise dos resultados

O agente apresentou bons resultados na classificação de sentimentos, especialmente em comentários claramente positivos ou negativos. A geração de justificativas também foi consistente e compreensível.
Como ponto forte, destaca-se a execução local, garantindo privacidade dos dados. Como limitação, comentários ambíguos ou muito curtos podem gerar classificações menos precisas.

---

## 6. Diferenciais implementados

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [ ] Memória persistente
- [x] Explicabilidade
- [x] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

Entre as limitações do sistema, destaca-se a dificuldade em interpretar comentários ambíguos ou com ironia. Além disso, o modelo pode apresentar variações nas respostas dependendo do contexto.
Como melhorias futuras, podem ser implementados:
- Ajuste fino do modelo para o domínio educacional.
- Inclusão de análise estatística agregada dos sentimentos.
- Interface gráfica para facilitar o uso.
- Integração com sistemas acadêmicos.

---

## 8. Referências

1. [Ollama GitHub](https://github.com/ollama/ollama)
2. [Ollama Python Library](https://pypi.org/project/ollama/)
3. Documentação oficial de modelos LLM.

---

## 9. Checklist de entrega

- [x] Documento de engenharia preenchido
- [x] Código funcional no repositório
- [x] Relatório de entrega preenchido
- [ ] Pull Request aberto