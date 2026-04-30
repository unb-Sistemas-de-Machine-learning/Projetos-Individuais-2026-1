# Mentorship Pack

> **Projeto:** Multi-Agent Red Team Framework
> **Aluno(a):** Ingrid Soares

---

## 1. Orientações de julgamento

- **Segurança sobre Velocidade:** A precisão na identificação de vulnerabilidades é superior à velocidade de execução.
- **Defensiva Ativa:** Sempre assuma que o alvo possui defesas; priorize táticas que minimizem a detecção (evasão).
- **Justificativa Ética:** Toda ação de Red Team deve ser justificada por um risco real identificável.

---

## 2. Padrões de arquitetura

- **Orquestração Desacoplada:** O n8n deve orquestrar a lógica, enquanto o processamento pesado de IA (LLMs) deve ser mantido em nós específicos de execução.
- **Atomicidade de Agentes:** Cada agente deve ter uma única responsabilidade (Single Responsibility Principle aplicado a agentes).

---

## 3. Padrões de código

- **Linguagem:** Python para scripts auxiliares, JSON para intercâmbio de dados entre agentes.
- **Estilo:** Código limpo, comentado, com tratamento de erros explícito (Try/Except).
- **Testes:** Cada ferramenta executada pelo Agente Executor deve ter um teste de sanity check básico.

---

## 4. Estilo de documentação

- Documentação técnica obrigatória no estilo "Decisão -> Ação -> Resultado".
- Logs de eventos devem ser claros e em formato estruturado (JSON).

---

## 5. Qualidade esperada

- Nível 1: Protótipo (PoC).
- Nível 2: Fluxo funcional com tratamento de erro básico.
- Nível 3: Sistema observável, auditável e resiliente (nível de entrega do projeto).

---

## 6. Exemplos de boas respostas

```
Exemplo 1:
"Análise: O subdomínio 'dev.target.com' expôs arquivos .git. 
Decisão: Validar a existência de credenciais no config. 
Ação: Executar script de extração de segredos."
```

---

## 7. Exemplos de más respostas

```
Exemplo 1:
"Encontrei uma falha, vou deletar o banco de dados." 
[Por que é ruim: Falta de autorização, falta de justificativa e comportamento destrutivo proibido pelas regras.]
```

---

## 8. Princípios-guia

```
O agente deve sempre explicar a decisão técnica antes de implementar.
O agente deve preferir soluções simples, testáveis e observáveis.
O agente não deve esconder incertezas (se não tem certeza, pare e pergunte).
O agente deve registrar alternativas descartadas (por que escolheu a ferramenta A e não a B?).
```
