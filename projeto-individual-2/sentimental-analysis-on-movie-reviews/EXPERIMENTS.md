# Experimentos — Análise de Sentimento no IMDb

Este documento define as execuções rastreadas no MLflow que atendem à Etapa 4 do `ACTION.md` ("Run Multiple Experiments"). Todas as execuções aqui são iniciadas via `src/pipeline.py` com a flag `--track`, portanto todos os runs entram no mesmo experimento do MLflow (`sentiment-imdb`) e podem ser comparados lado a lado na interface.

**Pré-requisitos**

- Marco 3 verificado: `mlflow.transformers.log_model` funciona (`torchvision` instalado) e pelo menos um registro de teste foi concluído com sucesso.
- `mlruns/` limpo antes de executar a bateria de experimentos (ver "Ordem recomendada de execução" abaixo), para que o experimento contenha apenas os runs listados aqui.

**Parâmetros fixos em todos os experimentos**

- `--data-dir data/raw/aclImdb` (padrão)
- `--split test` (padrão — o split `train` tem o mesmo tamanho e também é não visto pelo modelo ajustado no SST-2)
- `--batch-size 8` (padrão — o tamanho do batch de inferência não afeta os valores das métricas, apenas o tempo de execução)

**Parâmetros variados**

- `--sample-size` — dimensão de estabilidade
- `--max-length` — dimensão de truncamento
- `--random-seed` — dimensão de variância
- `--register-model` — usado apenas no run baseline escolhido

---

## Dimensão 1 — Varredura de estabilidade (`--sample-size`)

**Por que esta dimensão importa.** Avaliar em 100 amostras versus 1.000 amostras usa o mesmo pipeline, mas produz uma medição estatisticamente diferente. Métricas em amostras pequenas oscilam alguns pontos percentuais de um run para outro simplesmente por causa das resenhas sorteadas; métricas em amostras maiores convergem para um valor mais estável. Esta varredura responde: *"Com qual tamanho de amostra podemos confiar no número reportado?"* — uma pergunta de engenharia legítima e também a justificativa para o tamanho de amostra citado no relatório final.

### Exp-01 — size-100

```bash
python -m src.pipeline --sample-size 100 --track --run-name "size-100"
```

**Por quê:** É o extremo mais ruidoso da comparação. Espera-se que as métricas difiram em torno de 2 a 3 pontos percentuais em relação aos runs com amostras maiores. Esse run estabelece *quão ruidosas* são amostras pequenas, o que justifica a execução dos tamanhos maiores.

### Exp-02 — size-250

```bash
python -m src.pipeline --sample-size 250 --track --run-name "size-250"
```

**Por quê:** É um ponto intermediário. Se a acurácia em 250 amostras já se alinhar aos runs de 500 e 1.000, isso indica que 250 é suficiente para iteração rápida; se ainda divergir, aprendemos que 500 é o limiar mais adequado. Qualquer um dos resultados é útil.

### Exp-03 — size-500

```bash
python -m src.pipeline --sample-size 500 --track --run-name "size-500"
```

**Por quê:** É o ponto médio "provavelmente estável". Também funciona como âncora com `random_seed=42` para a Dimensão 3 (verificação de variância), pois suas métricas são comparadas com os runs `seed-43` e `seed-44` usando o mesmo tamanho de amostra.

### Exp-04 — baseline-1000 (registrado)

```bash
python -m src.pipeline --sample-size 1000 --track --register-model --run-name "baseline-1000"
```

**Por quê:** É o ponto mais estável da varredura de tamanho de amostra — com 1.000 amostras, o ruído de medição já é baixo o suficiente para reportarmos o número com confiança. Este também é o **único run que registra uma versão do modelo** no Model Registry como `sentiment-imdb` (via `--register-model`), porque registrar todos os runs poluiria o registry com iterações de desenvolvimento. Escolher o run de maior amostra como versão oficial associa o modelo entregue à métrica estatisticamente mais confiável. Esse run produz o arquivo `model.safetensors` de aproximadamente 268 MB em seu diretório de artefatos.

---

## Dimensão 2 — Varredura de truncamento (`--max-length`)

**Por que esta dimensão importa.** O DistilBERT tem um limite arquitetural rígido de 512 tokens, e resenhas do IMDb frequentemente ultrapassam esse tamanho. O padrão do pipeline é 512, o que significa que resenhas longas são truncadas silenciosamente no final — potencialmente removendo o trecho mais carregado de sentimento, já que muitos usuários deixam o veredito para o último parágrafo. Esta varredura quantifica *quanta acurácia perdemos ao cortar entradas mais cedo*, o que se conecta diretamente à decisão de "estratégia de truncamento" definida na Etapa 1 do `ACTION.md` e às limitações reais que o relatório precisa reconhecer na Etapa 8.

Os três runs desta dimensão usam `--sample-size 500` para isolar o efeito de `max_length` do efeito de estabilidade. O ponto de comparação com `max_length=512` já está coberto pelo **Exp-03** (`size-500`), então são necessários apenas dois novos runs.

### Exp-05 — maxlen-128

```bash
python -m src.pipeline --sample-size 500 --max-length 128 --track --run-name "maxlen-128"
```

**Por quê:** É o extremo de truncamento agressivo. 128 tokens correspondem aproximadamente às primeiras 100 palavras de uma resenha — o suficiente para introduzir o assunto, mas raramente suficiente para capturar o veredito. Espera-se uma queda visível de acurácia em relação ao baseline de 512 tokens. Esse run produz a evidência mais forte de que o truncamento importa.

### Exp-06 — maxlen-256

```bash
python -m src.pipeline --sample-size 500 --max-length 256 --track --run-name "maxlen-256"
```

**Por quê:** É um ponto intermediário. Se a acurácia em 256 ficar próxima da de 512, aprendemos que o ganho marginal dos últimos 256 tokens é pequeno — interessante porque indicaria que o modelo decide majoritariamente a partir da primeira metade da resenha. Se ficar mais próxima do run de 128, aprendemos o oposto. Em ambos os casos, o formato da curva em três pontos (128 -> 256 -> 512) é o resultado relevante.

---

## Dimensão 3 — Verificação de variância (`--random-seed`)

**Por que esta dimensão importa.** Toda métrica reportada é uma *medição única*. Executar o mesmo pipeline com uma semente aleatória diferente sorteia um subconjunto diferente de 500 resenhas dentro das 25.000 resenhas do split de teste, e as métricas podem mudar levemente — não porque o modelo mudou, mas porque a amostra mudou. Esta varredura mede esse ruído inerente. Se as métricas variarem cerca de 0,2% entre sementes, podemos reportar os números com confiança; se variarem cerca de 2%, sabemos que o número reportado tem uma margem de erro maior e deve ser apresentado com essa ressalva. Essa é a diferença entre dizer "nossa acurácia é 0,89" e "nossa acurácia é 0,89 ± 0,01".

Os três runs desta dimensão fixam `--sample-size 500` e variam apenas a semente. O ponto de comparação com `seed=42` já está coberto pelo **Exp-03** (`size-500`), então são necessários apenas dois novos runs.

### Exp-07 — seed-43

```bash
python -m src.pipeline --sample-size 500 --random-seed 43 --track --run-name "seed-43"
```

**Por quê:** É uma segunda amostra de 500 resenhas do mesmo split de teste. Deve produzir métricas dentro de uma pequena tolerância em relação ao Exp-03; a diferença quantifica o ruído de uma execução individual.

### Exp-08 — seed-44

```bash
python -m src.pipeline --sample-size 500 --random-seed 44 --track --run-name "seed-44"
```

**Por quê:** É uma terceira amostra. Três pontos (seed 42, 43 e 44) permitem calcular uma pequena faixa ou desvio padrão da métrica e reportá-la como margem de erro, o que é mais informativo do que apresentar apenas um ponto estimado.

---

## Ordem recomendada de execução

Execute em ordem aproximadamente crescente de tempo de execução para que, se algo quebrar, os runs rápidos sejam perdidos primeiro, não o mais lento:

1. **Exp-01** (size-100) — menor, mais rápido, aproximadamente 30s
2. **Exp-05** (maxlen-128, size 500) — o truncamento reduz um pouco o tempo
3. **Exp-06** (maxlen-256, size 500)
4. **Exp-02** (size-250)
5. **Exp-07** (seed-43, size 500)
6. **Exp-08** (seed-44, size 500)
7. **Exp-03** (size-500) — este run é ao mesmo tempo o baseline de size=500 e seed=42
8. **Exp-04** (baseline-1000, registrado) — mais lento; inferência em ~1.000 amostras + serialização de ~268 MB do modelo

Após a conclusão do Exp-04, `mlflow ui` deve mostrar:

- Um experimento (`sentiment-imdb`) contendo 8 runs
- Um modelo registrado (`sentiment-imdb`) com a Versão 1 vinculada ao Exp-04
- Uma visão de comparação entre quaisquer runs selecionados, mostrando parâmetros e métricas lado a lado

---

## Tabela-resumo

| ID     | Nome do run     | Dimensão      | Tamanho da amostra | Max length | Seed | Registrado? |
|--------|-----------------|---------------|--------------------|------------|------|-------------|
| Exp-01 | `size-100`      | Estabilidade  | 100                | 512        | 42   | Não         |
| Exp-02 | `size-250`      | Estabilidade  | 250                | 512        | 42   | Não         |
| Exp-03 | `size-500`      | Estabilidade  | 500                | 512        | 42   | Não         |
| Exp-04 | `baseline-1000` | Estabilidade  | 1000               | 512        | 42   | **Sim**     |
| Exp-05 | `maxlen-128`    | Truncamento   | 500                | 128        | 42   | Não         |
| Exp-06 | `maxlen-256`    | Truncamento   | 500                | 256        | 42   | Não         |
| Exp-07 | `seed-43`       | Variância     | 500                | 512        | 43   | Não         |
| Exp-08 | `seed-44`       | Variância     | 500                | 512        | 44   | Não         |

**Âncoras compartilhadas (evitam runs duplicados):**

- Exp-03 (`size-500`) é o ponto `max-length=512` da varredura de truncamento -> comparar com Exp-05 e Exp-06
- Exp-03 (`size-500`) também é o ponto `seed=42` da varredura de variância -> comparar com Exp-07 e Exp-08

**Total de runs:** 8 rastreados, 1 versão de modelo registrada.
