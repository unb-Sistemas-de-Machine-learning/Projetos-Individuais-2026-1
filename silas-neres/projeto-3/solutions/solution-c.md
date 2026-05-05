# Solution C — Orquestração Multicanal e Roteamento Inteligente

## Abordagem
A Solution C é a solução final escolhida. Ela utiliza a IA como motor de decisão para um sistema adaptativo. O fluxo não apenas classifica, mas executa ações específicas (Telegram, Gmail, Sheets) baseadas no diagnóstico da IA.

## Problema tratado
A necessidade de uma resposta imediata para violações graves de consumo (ex: corte de energia) versus a automação de respostas para dúvidas simples.

## Desenho Lógico do Fluxo
1. **Entrada:** Formulário n8n captura os dados do consumidor.
2. **Inteligência:** O Agente de IA processa o relato e retorna um JSON estruturado.
3. **Normalização:** O nó `Parse AI Response` limpa e valida os dados recebidos.
4. **Decisão Automatizada (O Diferencial):**
   - **URGENTE:** Dispara alerta imediato via Telegram para a equipe de plantão.
   - **DÚVIDA:** Envia e-mail automático via Gmail com orientações baseadas no CDC.
   - **RECLAMAÇÃO/INVÁLIDO:** Registra no Google Sheets para auditoria humana.

## Persistência e Rastreabilidade
Todas as execuções são registradas no Google Sheets, contendo o Artigo do CDC citado, o Score de Urgência e a Confiança da IA, permitindo auditoria total do processo.

## Justificativa da Escolha
A Solution C foi escolhida pois atende 100% aos requisitos do projeto:
- **Uso de IA para Decisão:** O `Route by Category` é controlado pelo julgamento da IA.
- **Tratamento de Erros:** A rota "Inválido" e a análise de confiança agem como fallback.
- **Integração Real:** Usa Telegram e Gmail de forma simultânea e lógica.