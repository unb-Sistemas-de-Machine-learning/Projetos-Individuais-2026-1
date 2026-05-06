#!/bin/bash

# ==========================================
# Script de Teste Rápido - Monitoria IA
# Envia uma mensagem simulada para o bot
# ==========================================

# 1. Substitua pelas suas credenciais reais
TOKEN="SEU_TOKEN_DO_BOTFATHER_AQUI"
CHAT_ID="SEU_CHAT_ID_DO_TELEGRAM_AQUI"

# 2. Escolha qual rota você quer testar descomentando uma das linhas abaixo:

# ROTA 0: Técnica (Espera resposta Socrática)
MENSAGEM="Professor, meu loop while em Python não para de rodar, me dá o código certo?"

# ROTA 1: Administrativa (Espera mensagem fixa de registro)
# MENSAGEM="Qual é a data limite para entregar a documentação do projeto?"

# ROTA 2: Exceção (Espera alerta vermelho de escalonamento)
# MENSAGEM="Meu computador sofreu um curto-circuito e perdi todo o código."

echo "Disparando payload de teste via API do Telegram..."

curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
     -d chat_id="${CHAT_ID}" \
     -d text="${MENSAGEM}"

echo -e "\n\n✅ Teste disparado! Verifique a resposta no seu aplicativo do Telegram."
