# Solution B — Triagem com Base de Conhecimento (Contexto)

## Abordagem
A Solution B evolui a anterior ao focar na precisão técnica. Propõe-se o uso de um documento de referência (Texto do CDC) para que a IA consulte antes de classificar a demanda.

## Problema tratado
A falta de confiabilidade nas citações jurídicas da IA. O objetivo aqui é garantir que a classificação "URGENTE" ou "DÚVIDA" esteja embasada no texto real da lei.

## Fluxo proposto
n8n Form Trigger → AI Agent (com nó de Contexto/Vector Store) → Google Sheets.

## Pontos Positivos
- Redução drástica de alucinações jurídicas.
- Respostas mais ricas e fundamentadas em artigos específicos.

## Limitações e Riscos
- **Fluxo Linear:** Ainda não utiliza o roteamento inteligente (Switch) para disparar ações diferentes.
- **Complexidade de Dados:** Exige a gestão de arquivos externos de referência.

## Motivo do Descarte
Embora tecnicamente mais precisa no conteúdo, a Solution B ainda não aproveita o potencial do n8n como orquestrador multicanal. Ela não "age" sobre a urgência identificada, apenas a documenta melhor.