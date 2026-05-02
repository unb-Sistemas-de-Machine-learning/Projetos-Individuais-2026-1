# Solution B: Validação Prática de Red Team

Esta solução implementa a segunda fase do framework: a **Validação Prática**.

## Objetivo
Transformar o plano gerado pela **Solution A** em ações concretas de segurança. O objetivo é automatizar a execução de testes contra o alvo identificado.

## Requisitos Técnicos
1.  **Integração:** Receber o JSON de saída da Solution A (fases de reconhecimento e validação).
2.  **Automação:** Executar scanners ou consultas a APIs de segurança baseadas no plano recebido.
3.  **Processamento:** Normalizar os resultados dos scans para um formato legível pelo SOC.

## Arquitetura Proposta
- **Entrada:** Webhook que recebe o plano de ataque da Solution A.
- **Processamento:** Nós no n8n que realizam chamadas a APIs de segurança (ex: VirusTotal, Shodan, ou execução de scripts via Docker/Node).
- **Saída:** Relatório técnico detalhado com as evidências coletadas.

## Roadmap
- [ ] Definir APIs de segurança para integração.
- [ ] Desenhar o workflow de execução no n8n.
- [ ] Implementar lógica de normalização de dados.
- [ ] Validar integração entre Solution A e B.

## Referências
- [Solution A: Planejamento Tático](../solution-a/README.md)
