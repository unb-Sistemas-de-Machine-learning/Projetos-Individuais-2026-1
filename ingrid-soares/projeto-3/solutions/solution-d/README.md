# Solution D: Infraestrutura de Testes Automatizados

Esta solução implementa a camada de garantia de qualidade (QA) do framework de segurança.

## Objetivo
Automatizar a validação dos workflows A, B e C, garantindo que qualquer alteração no código não quebre a integração ou a estrutura dos dados JSON esperados.

## Procedimento de Teste
Para executar a suíte de testes de integração, siga os passos no seu terminal:

1. Instale as dependências:
   ```bash
   pip install requests
   ```

2. Execute o script de validação:
   ```bash
   python3 ingrid-soares/projeto-3/solutions/solution-d/tests/test_framework.py
   ```

Este script disparará o webhook do orquestrador (Solution C) e verificará a resposta de sucesso da integração.

## Roadmap de Implementação
- [ ] Definir suíte de testes unitários para os nós de validação (Code nodes).
- [x] Implementar script de teste de integração (disparo de webhook -> validação de resposta).
- [ ] Configurar CI/CD básico para execução automática dos testes após cada commit.
