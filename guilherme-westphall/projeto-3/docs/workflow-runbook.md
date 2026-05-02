# Workflow Runbook

> **Projeto:** Automação inteligente de emissão de notas fiscais com aprovação humana
> **Aluno(a):** Guilherme Westphall

---

## Processo obrigatório de execução

Siga as etapas abaixo na ordem indicada. Cada etapa deve gerar um artefato verificável e, quando possível, um commit com mensagem descritiva e racionalidade da decisão.

Este runbook existe para garantir que a construção do workflow seja auditável: primeiro define-se a missão, depois comparam-se alternativas, prototipam-se soluções, testam-se riscos e só então consolida-se a solução final.

### Etapa 1: Ler o Mission Brief

- [x] Ler e compreender o mission brief.
- [x] Identificar entradas, saídas e restrições.
- [x] Anotar dúvidas ou ambiguidades.

Artefato esperado:

- `docs/mission-brief.md`

Pontos já definidos:

- O fluxo automatiza apoio à emissão recorrente de notas fiscais para prestadores de serviço.
- Productive.io é a fonte de entradas de tempo.
- Cálculos financeiros devem ser determinísticos.
- O agente de IA valida, recomenda caminho e gera mensagens.
- Envio externo depende de aprovação humana explícita via Telegram.

Ambiguidades a resolver durante o projeto:

- [TO BE DEFINED] Modelo final de nota fiscal ou planilha usada para geração do PDF.
- [TO BE DEFINED] Destino final dos logs de auditoria.
- [TO BE DEFINED] Formato final da aprovação no Telegram.
- [TO BE DEFINED] Estratégia final para armazenamento seguro de credenciais.

### Etapa 2: Propor três soluções possíveis

- [ ] Descrever `solution-a` com abordagem simples baseada em prompt.
- [ ] Descrever `solution-b` com regras externas, base de conhecimento ou validação adicional.
- [ ] Descrever `solution-c` com fluxo multi-etapas, aprovação humana e validação robusta.

As três soluções propostas para este projeto são:

| Solução | Abordagem | Descrição |
|---------|-----------|-----------|
| `solution-a` | Prompt simples | O n8n calcula período, horas e total. A IA recebe o resumo e gera validação, mensagem de aprovação e e-mail em uma única chamada. |
| `solution-b` | Validação com regras externas | Além do resumo calculado, o fluxo aplica uma pequena base de regras de faturamento, limites esperados e política de e-mail antes ou depois da IA. |
| `solution-c` | Fluxo multi-etapas com aprovação humana | O fluxo separa cálculo, validação por IA, normalização de JSON, roteamento condicional, aprovação via Telegram, geração/exportação da nota fiscal, envio por Gmail e logging. |

Critério inicial de julgamento:

- `solution-a` deve servir como baseline simples.
- `solution-b` deve demonstrar melhoria de governança e validação.
- `solution-c` deve representar a solução mais adequada para produção, por ser mais segura e auditável.

### Etapa 3: Registrar cada solução em pasta separada

- [ ] Criar `solutions/solution-a/`.
- [ ] Criar `solutions/solution-b/`.
- [ ] Criar `solutions/solution-c/`.

Conteúdo mínimo esperado em cada pasta:

- `README.md` explicando a abordagem.
- Workflow, prompt, pseudo-workflow ou protótipo demonstrável.
- Limitações conhecidas.
- Evidência mínima ou instrução de execução.

Estrutura esperada:

```text
solutions/
├── solution-a/
│   └── README.md
├── solution-b/
│   └── README.md
└── solution-c/
    └── README.md
```

### Etapa 4: Implementar protótipos mínimos

- [ ] Implementar protótipo da `solution-a`.
- [ ] Implementar protótipo da `solution-b`.
- [ ] Implementar protótipo da `solution-c`.

Escopo mínimo dos protótipos:

- `solution-a`: entrada JSON simulada, prompt único e resposta esperada da IA.
- `solution-b`: entrada JSON simulada mais regras explícitas de validação, como zero entradas, zero horas, período ausente, total incomum e política de e-mail.
- `solution-c`: workflow n8n com etapas separadas para cálculo, consulta Productive.io, IA, parsing/normalização, condicional e aprovação humana.

Critérios para considerar um protótipo demonstrável:

- Deve receber ou simular dados de faturamento.
- Deve demonstrar como a IA influencia a decisão.
- Deve indicar o caminho seguinte: aprovação, revisão manual ou interrupção.
- Deve deixar claro o que ainda falta para produção.

### Etapa 5: Executar testes

- [ ] Criar testes em `tests/`.
- [ ] Executar testes para cada solução.
- [ ] Registrar resultados em `docs/evidence/`.

Casos mínimos de teste:

| Teste | Objetivo | Resultado esperado |
|-------|----------|--------------------|
| Período no dia 1 | Validar cálculo do período anterior, do dia 16 ao último dia do mês anterior. | Período correto. |
| Período no dia 16 | Validar cálculo do período atual, do dia 1 ao dia 15. | Período correto. |
| Entradas normais | Validar caminho feliz. | `request_approval`. |
| Zero entradas | Validar fallback. | `needs_manual_review` ou `stop`. |
| Zero horas | Validar fallback. | `needs_manual_review` ou `stop`. |
| Valor ausente | Evitar inferência financeira. | `stop`. |
| JSON inválido da IA | Validar normalização e bloqueio. | Revisão manual ou interrupção. |
| Sem aprovação Telegram | Garantir bloqueio de envio externo. | Gmail não é acionado. |

Evidências esperadas:

- Prints do workflow n8n.
- Logs de execução.
- Outputs dos nós de cálculo.
- Exemplo de resposta da IA.
- Print ou log da aprovação no Telegram.
- Evidência de que Gmail só ocorre após aprovação.

### Etapa 6: Comparar as soluções

| Critério | Solution A | Solution B | Solution C |
|----------|-----------|-----------|-----------|
| Custo | Baixo: menos nós e uma chamada de IA. | Médio: adiciona regras e validações. | Médio/alto: mais nós, integrações e tratamento de estado. |
| Complexidade | Baixa. | Média. | Alta. |
| Qualidade da resposta | Média, depende muito do prompt. | Melhor, pois combina IA com regras explícitas. | Melhor para o projeto, pois separa responsabilidades e reduz risco operacional. |
| Riscos | Alto risco de aceitar saída malformada ou insuficiente. | Risco médio, com melhor controle de casos conhecidos. | Risco menor, pois há aprovação humana, parsing e caminhos condicionais. |
| Manutenibilidade | Boa no curto prazo, fraca para evolução. | Boa, por isolar regras. | Boa se o workflow for bem documentado, apesar de mais componentes. |
| Adequação ao problema | Parcial: demonstra uso de IA, mas é frágil para processo financeiro. | Boa: aumenta controle e auditabilidade. | Muito boa: atende melhor aos requisitos de IA, decisão, integração, rastreabilidade e segurança. |

Observação:

- A comparação deve ser revisada após a implementação dos protótipos e registrada no ADR.

### Etapa 7: Escolher uma solução final

- [ ] Solução escolhida: `solution-c`.
- [ ] Justificativa: [TO BE VALIDATED AFTER PROTOTYPES]

Justificativa preliminar:

`solution-c` é a melhor candidata porque o problema envolve envio de nota fiscal, comunicação externa e dados financeiros. Separar cálculo determinístico, validação por IA, aprovação humana e envio reduz risco e demonstra melhor os requisitos do projeto: n8n como orquestrador, IA influenciando decisão, condicionais, integração com serviços externos, tratamento de erros e rastreabilidade.

### Etapa 8: Registrar a decisão em ADR

- [ ] Criar `docs/adr/001-escolha-da-solucao.md`.

O ADR deve conter:

- Contexto do problema.
- Alternativas A, B e C.
- Prós e contras de cada alternativa.
- Decisão final.
- Consequências da decisão.
- Referências para `mission-brief.md`, `agent.md`, `mentorship-pack.md` e evidências.

### Etapa 9: Gerar o Merge-Readiness Pack

- [ ] Preencher `docs/merge-readiness-pack.md`.

O merge-readiness pack deve reunir:

- Resumo da solução escolhida.
- Comparação final entre as três soluções.
- Testes executados.
- Evidências coletadas.
- Limitações conhecidas.
- Riscos e mitigações.
- Decisões arquiteturais.
- Instruções de execução.
- Checklist de revisão.
- Justificativa para merge.

### Etapa 10: Fazer commits separados por etapa

- [ ] Verificar que cada etapa tem pelo menos um commit ou registro equivalente de racionalidade.
- [ ] Verificar que cada commit contém mensagem clara e motivo da decisão.

Sequência mínima sugerida:

| # | Commit | Racionalidade esperada |
|---|--------|------------------------|
| 1 | Cria mission brief inicial | Define contrato do projeto e critérios de aceitação. |
| 2 | Adiciona agent.md com regras de comportamento | Delimita papel, formato de saída e restrições do agente. |
| 3 | Cria mentorship pack e workflow runbook | Define padrão de construção e processo auditável. |
| 4 | Implementa solution-a | Registra baseline simples baseado em prompt. |
| 5 | Implementa solution-b | Adiciona validação baseada em regras ou base de conhecimento. |
| 6 | Implementa solution-c | Consolida fluxo multi-etapas com aprovação humana. |
| 7 | Adiciona testes e evidências | Demonstra funcionamento e tratamento de falhas. |
| 8 | Registra ADR com comparação das soluções | Justifica a escolha arquitetural. |
| 9 | Adiciona merge-readiness pack | Organiza evidências para revisão. |
| 10 | Consolida solução final | Prepara entrega final e relatório. |

Formato recomendado para mensagens de commit:

```text
tipo: resumo curto da alteração

Racionalidade:
- Decisão tomada.
- Motivo.
- Alternativas consideradas.
- Evidência ou próximo passo.
```
