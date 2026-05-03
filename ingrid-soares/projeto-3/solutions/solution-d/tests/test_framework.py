import requests
import time
import os

# CONFIGURAÇÕES
# Substitua pela sua URL base do n8n e sua API Key (se estiver usando Basic Auth ou Token no n8n)
N8N_URL = "https://ingrdsoares.app.n8n.cloud"
ORCHESTRATOR_WEBHOOK = f"{N8N_URL}/webhook/redteam-orchestrator"
TARGET = {"alvo": "exemplo.com"}

def test_integration():
    print(f"--- Iniciando Teste de Integração: {ORCHESTRATOR_WEBHOOK} ---")
    
    # 1. Dispara o Orquestrador
    response = requests.post(ORCHESTRATOR_WEBHOOK, json=TARGET)
    
    if response.status_code == 200:
        print("✅ Webhook disparado com sucesso!")
        print(f"Resposta: {response.json()}")
    else:
        print(f"❌ Erro ao disparar webhook: {response.status_code}")
        return

    # 2. Aguarda processamento
    print("⏳ Aguardando 10 segundos para processamento...")
    time.sleep(10)

    # 3. Validação (Nota: n8n Cloud pode exigir autenticação para listar execuções)
    print("--- Fim da fase de testes ---")
    print("Por favor, verifique a aba 'Executions' no seu n8n para confirmar o sucesso.")

if __name__ == "__main__":
    test_integration()
