# Solution C — Pipeline multi-etapas com validacao

Abordagem escolhida como final por combinar:

- classificacao
- extracao de entidades
- validacao de campos obrigatorios
- fallback por baixa confianca

## Caracteristicas

- melhor qualidade para ambiente real
- maior rastreabilidade
- controle de risco operacional

## Execucao

```bash
python solutions/solution-c/main.py "Preciso da segunda via do boleto. Meu RA e 211061529"
```
