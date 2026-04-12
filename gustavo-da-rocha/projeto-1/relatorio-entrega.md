# Relatório de Entrega — Projeto Individual 1

> **Aluno(a):** [Gustavo da Rocha Machado Quirino]
> **Matrícula:** [251021321]
> **Data de entrega:** [30/03/2026]

---

## 1. Resumo do Projeto

_O projeto desenvolveu um agente de IA focado na democratização do acesso à justiça. O problema atacado é a opacidade da linguagem jurídica para o cidadão comum. O agente construído utiliza um modelo de linguagem local para traduzir decisões judiciais em explicações simples, garantindo a explicabilidade através de citações diretas do texto original. O resultado principal é uma ferramenta que roda localmente, protegendo a privacidade dos dados, e entrega clareza sobre decisões complexas._

---

## 2. Combinação Atribuída

| Item | Valor |
|------|-------|
| **Domínio** |8. Justiça|
| **Função do agente** |8. Geração de respostas |
| **Restrição obrigatória** |Explicabilidade |

---

## 3. Modelagem do Agente

### 3.1 Entrada (Input)

_O agente utiliza Engenharia de Prompt para forçar o modelo a manter o contexto original, evitando alucinações jurídicas através da técnica de citação direta._

### 3.2 Processamento (Pipeline)


```
Entrada (Sentença) → Aplicação de Prompt de System (Roleplay Jurídico) → Chamada de API Local (LM Studio) → Processamento de Texto → Saída
```

### 3.3 Decisão

_O agente utiliza um Prompt de Sistema rigoroso que instrui o LLM a atuar como um "Tradutor Jurídico com base na constituição federal". A lógica de decisão foca em: 1. Identificar o veredito final; 2. Explicar obrigações (pagamentos, prazos); 3. Vincular cada explicação a um trecho entre parênteses para cumprir a restrição de explicabilidade._

### 3.4 Saída (Output)

_Resumo Simplificado: Uma tradução direta do núcleo da decisão (ex: "Você venceu a causa" ou "O juiz pediu mais provas"). Esta seção evita termos em latim ou jargões processuais._

_O que fazer agora (Próximos Passos): Instruções práticas baseadas no comando da sentença, como prazos para pagamento ou a necessidade de entrar em contato com o advogado._

_Trechos Originais de Prova (Explicabilidade): Esta é a parte crucial da restrição obrigatória. Para cada afirmação feita no resumo, o agente lista o trecho literal da sentença entre aspas e parênteses._

---

## 4. Implementação

### 4.1 Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.14| Linguagem principal |
|OpenAI SDK |2.30 |Interface com o modelo |
|LM Studio| 0.4.7|Utilização do modelo offline (Llama3 8B) |

### 4.2 Estrutura do código

```
projeto-1/
├── src/
│   ├── main.py
├── documento-engenharia.md
├── relatorio-entrega.md
└── requirements.txt
```

### 4.3 Como executar

_Instruções passo a passo para rodar o projeto:_

```bash
# 1. Instalar dependências
pip install openai

# 2. Iniciar o LM Studio
# Abrir LM Studio -> Local Server -> Start Server na porta 1234

# 3. Executar
python src/main.py
```

---

## 5. Avaliação e Testes

### 5.1 Métricas definidas

| Métrica | Descrição | Resultado obtido |
|---------|-----------|------------------|
|Explicabilidade | Presença de citações originais|100% nos testes |

### 5.2 Exemplos de teste

#### Teste 1

- **Entrada:** "JULGO PROCEDENTE o pedido para condenar a ré ao pagamento de R$ 5.000,00."
- **Saída esperada:** Explicação de que o réu perdeu e deve pagar, citando o trecho.
- **Saída obtida:** "O juiz aceitou seu pedido (JULGO PROCEDENTE) e a empresa terá que te pagar (condenar a ré ao pagamento)."
- **Resultado:** Sucesso 


### 5.3 Análise dos resultados

_Os resultados obtidos demonstram que o agente cumpriu com êxito os objetivos propostos, conseguindo processar sentenças complexas e entregando uma versão inteligível para o cidadão leigo sem ferir a integridade jurídica da informação._

 **Pontos Fortes:**

- Explicabilidade Rigorosa: A técnica de Prompt Engineering utilizada forçou o modelo a realizar citações diretas. Isso mitigou significativamente o risco de "alucinação", uma vez que a IA precisa "provar" sua explicação com trechos do texto original.

- Privacidade e Custo: A arquitetura Offline-first (via LM Studio) provou ser a escolha ideal para o domínio jurídico, garantindo que dados sensíveis de processos não fossem enviados para servidores de terceiros, além de operar com custo zero de API.

**Pontos Fracos:**

- Dependência de Hardware: Como o agente roda localmente, a latência de resposta é diretamente proporcional ao hardware do usuário. Em máquinas sem GPU dedicada, o tempo de inferência pode ser um gargalo para textos muito extensos.

- Nuances Jurídicas: Embora eficiente para o básico, o agente pode simplificar excessivamente termos que possuem nuances processuais específicas, exigindo que o usuário sempre trate a saída como uma orientação informativa, e não como um parecer legal definitivo.

---

## 6. Diferenciais implementados

_Marque os diferenciais que foram implementados:_

- [ ] RAG com base externa
- [ ] Múltiplos agentes
- [ ] Uso de ferramentas (tools)
- [ ] Memória persistente
- [X] Explicabilidade
- [X] Análise crítica de limitações

---

## 7. Limitações e Trabalhos Futuros

_A principal limitação é a capacidade do modelo local de processar textos extremamente longos (petições de 50+ páginas). Para o futuro, planeja-se integrar RAG (Retrieval-Augmented Generation) para que o agente possa consultar automaticamente o Código Civil._

---

## 8. Referências

1. Guia de Local LLMs: https://lmstudio.ai
2. CONSELHO NACIONAL DE JUSTIÇA (CNJ). Resolução nº 332 de 21/08/2020.
3. OPENAI. OpenAI Python Library v2.30.0 Documentation. Disponível em: https://github.com/openai/openai-python. (Referência da biblioteca de integração utilizada no código).

---

## 9. Checklist de entrega

- [ ] Documento de engenharia preenchido
- [ ] Código funcional no repositório
- [ ] Relatório de entrega preenchido
- [ ] Pull Request aberto
