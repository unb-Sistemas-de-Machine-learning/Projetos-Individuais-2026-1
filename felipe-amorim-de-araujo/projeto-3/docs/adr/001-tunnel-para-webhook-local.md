# ADR-001: Uso de ngrok para expor webhook do n8n localmente

## Status
Aceito

## Contexto
O workflow-runbook exige que o n8n receba webhooks do GitHub em ambiente local de
desenvolvimento. Para isso, o n8n precisa de uma URL pública acessível pela internet.
O `docker-compose.yml` inicial utilizava `N8N_TUNNEL_ENABLED=true`, variável que
ativava um tunnel nativo baseado em `localtunnel` em versões antigas do n8n.

Ao subir o ambiente com a imagem `docker.n8n.io/n8nio/n8n:latest` (v2.18.5), a URL
do tunnel não foi gerada — o n8n iniciou normalmente sem nenhuma mensagem de tunnel
nos logs, confirmando que o suporte nativo foi removido nessa versão.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| `N8N_TUNNEL_ENABLED=true` (nativo) | Zero configuração extra; integrado ao container | Removido no n8n 2.x — não funciona com a imagem latest |
| ngrok | Amplamente documentado; URL estável durante a sessão; dashboard de inspeção de requests | Requer instalação separada; URL muda a cada restart (free tier) |
| localtunnel (`lt --port 5678`) | Sem cadastro necessário | Instável; URLs aleatórias; sem dashboard |
| Cloudflare Tunnel | URL persistente; sem restart issues | Configuração mais complexa; exige conta Cloudflare |

## Decisão

Usar **ngrok** (`ngrok http 5678`) como solução de tunnel durante o desenvolvimento
local. A variável `N8N_TUNNEL_ENABLED` foi removida do `docker-compose.yml`.

Motivo: ngrok é a alternativa mais direta dado que o tunnel nativo foi removido —
tem dashboard de inspeção útil para debugar payloads do GitHub webhook, e o custo de
configuração é mínimo (um comando). A troca de URL a cada restart é aceitável para
o contexto de testes pontuais exigidos pelo runbook.

## Consequências

- A URL pública do ngrok muda a cada `ngrok http 5678` — ao reiniciar, atualizar
  o webhook no GitHub antes de executar novos casos de teste
- O `docker-compose.yml` não contém mais referência ao tunnel; a responsabilidade
  de expor a porta é externa ao container
- Adicionar ao fluxo de setup de cada solução: rodar ngrok em paralelo ao
  `docker-compose up -d`

## Evidências
Logs do n8n 2.18.5 confirmando ausência do tunnel: `docs/evidence/solution-a/` —
o startup log mostra apenas `"n8n ready on ::, port 5678"` sem URL de tunnel,
mesmo com `N8N_TUNNEL_ENABLED=true` configurado.
