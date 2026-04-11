# Experiments — IMDb Sentiment Analysis

This document defines the MLflow tracking runs that satisfy ACTION.md Stage 4 ("Run Multiple Experiments"). Every run here is launched via `src/pipeline.py` with the `--track` flag, so all runs land in the same MLflow experiment (`sentiment-imdb`) and can be compared side-by-side in the UI.

**Prerequisites**
- Milestone 3 verified: `mlflow.transformers.log_model` works (torchvision installed) and a test registration has succeeded at least once
- `mlruns/` wiped clean before running the sweep (see "Recommended execution order" below), so the experiment contains only the runs listed here

**Fixed params across all experiments**
- `--data-dir data/raw/aclImdb` (default)
- `--split test` (default — the `train` split is the same size and equally unseen by the SST-2-finetuned model)
- `--batch-size 8` (default — inference batch size does not affect metric values, only wall time)

**Varied params**
- `--sample-size` — stability dimension
- `--max-length` — truncation dimension
- `--random-seed` — variance dimension
- `--register-model` — only on the blessed baseline run

---

## Dimension 1 — Stability sweep (`--sample-size`)

**Why this dimension matters.** Evaluating on 100 samples vs 1000 samples gives you the same pipeline but a statistically different measurement. Small-sample metrics bounce around by several percentage points run-to-run simply because of which reviews happened to be drawn; large-sample metrics converge to a stable value. This sweep answers: *"At what sample size can we trust the reported number?"* — which is both a legitimate engineering question and the justification for whatever sample size the final report ends up quoting.

### Exp-01 — size-100

```bash
python -m src.pipeline --sample-size 100 --track --run-name "size-100"
```

**Why:** The noisy end of the spectrum. Expect metrics to differ by ~2–3 percentage points from the larger-sample runs. This run establishes *how noisy* small samples are, which in turn justifies why we bothered running the larger ones.

### Exp-02 — size-250

```bash
python -m src.pipeline --sample-size 250 --track --run-name "size-250"
```

**Why:** An intermediate point. If accuracy on 250 samples already lines up with the 500 and 1000 runs, that tells us 250 is enough for fast iteration; if it still diverges, we learn that 500 is the real threshold. Either answer is useful.

### Exp-03 — size-500

```bash
python -m src.pipeline --sample-size 500 --track --run-name "size-500"
```

**Why:** The "probably stable" midpoint. Also doubles as the `random_seed=42` anchor for Dimension 3 (variance check) — we compare its metrics against the seed-43 and seed-44 runs at the same sample size.

### Exp-04 — baseline-1000 (registered)

```bash
python -m src.pipeline --sample-size 1000 --track --register-model --run-name "baseline-1000"
```

**Why:** The stable endpoint of the size sweep — by 1000 samples the measurement noise is negligible and we have a number we're confident enough to ship. This is also the **one run that registers a model version** in the `sentiment-imdb` Model Registry (via `--register-model`), because registering every run would clutter the registry with dev iterations. Picking the largest-sample run as the blessed version means the shipped model is associated with the most statistically reliable metric. This run produces the ~268MB `model.safetensors` in its artifact directory.

---

## Dimension 2 — Truncation sweep (`--max-length`)

**Why this dimension matters.** DistilBERT has a hard architectural cap at 512 tokens, and IMDb reviews routinely exceed that. The pipeline's default is 512, which means long reviews are silently truncated at the end — potentially dropping the most sentiment-laden passage, since reviewers often save their verdict for the last paragraph. This sweep quantifies *how much accuracy we lose by cutting inputs short*, which directly maps to the "truncation strategy" design decision ACTION.md Stage 1 locked in and the "real limitations" the report has to acknowledge in Stage 8.

All three runs in this dimension use `--sample-size 500` to isolate the max-length effect from the stability effect. The max-length=512 point of comparison is already covered by **Exp-03** (`size-500`), so we only need two new runs.

### Exp-05 — maxlen-128

```bash
python -m src.pipeline --sample-size 500 --max-length 128 --track --run-name "maxlen-128"
```

**Why:** The aggressive truncation extreme. 128 tokens is roughly the first 100 words of a review — enough to set up the topic, rarely enough to capture the verdict. Expect a visible accuracy drop vs. the 512 baseline. This run produces the most dramatic evidence that truncation matters.

### Exp-06 — maxlen-256

```bash
python -m src.pipeline --sample-size 500 --max-length 256 --track --run-name "maxlen-256"
```

**Why:** A middle point. If accuracy at 256 is close to 512, we learn that the marginal return from the last 256 tokens is small — interesting because it means the model is mostly making its decision from the first half of the review. If it's closer to the 128 run, we learn the opposite. Either way, the shape of the three-point curve (128 → 256 → 512) is the finding.

---

## Dimension 3 — Variance check (`--random-seed`)

**Why this dimension matters.** Every metric we report is a *single measurement*. Running the same pipeline with a different random seed draws a different 500-sample subset from the 25,000-review test set, and the metrics will differ slightly — not because the model changed, but because the sample did. This sweep measures that inherent noise. If metrics vary by ~0.2% across seeds, we can report our numbers with confidence; if they vary by ~2%, we know the reported number has a wide error bar and should be framed accordingly. This is the difference between "our accuracy is 0.89" and "our accuracy is 0.89 ± 0.01."

All three runs in this dimension fix `--sample-size 500` and vary only the seed. The `seed=42` point of comparison is already covered by **Exp-03** (`size-500`), so we only need two new runs.

### Exp-07 — seed-43

```bash
python -m src.pipeline --sample-size 500 --random-seed 43 --track --run-name "seed-43"
```

**Why:** A second draw of 500 reviews from the same test set. Should produce metrics within a small tolerance of Exp-03; the gap quantifies single-run noise.

### Exp-08 — seed-44

```bash
python -m src.pipeline --sample-size 500 --random-seed 44 --track --run-name "seed-44"
```

**Why:** A third draw. Three points (seed 42, 43, 44) let us compute a small range/standard-deviation of the metric and report it as an error bar, which is a sharper statement than a single point estimate.

---

## Recommended execution order

Run in roughly increasing wall-time order so that if something breaks you lose the fast runs first, not the slow one:

1. **Exp-01** (size-100) — smallest, fastest, ~30s
2. **Exp-05** (maxlen-128, size 500) — truncation amplifies speed slightly
3. **Exp-06** (maxlen-256, size 500)
4. **Exp-02** (size-250)
5. **Exp-07** (seed-43, size 500)
6. **Exp-08** (seed-44, size 500)
7. **Exp-03** (size-500) — note this run is both the size=500 and seed=42 baseline
8. **Exp-04** (baseline-1000, registered) — slowest; ~1000-sample inference + ~268MB model serialization

After Exp-04 completes, `mlflow ui` should show:
- One experiment (`sentiment-imdb`) containing 8 runs
- One registered model (`sentiment-imdb`) with Version 1 linked to Exp-04
- Compare view across any selection of runs showing params and metrics side-by-side

---

## Summary table

| ID     | Run name       | Dimension   | Sample size | Max length | Seed | Registered? |
|--------|----------------|-------------|-------------|------------|------|-------------|
| Exp-01 | `size-100`     | Stability   | 100         | 512        | 42   | No          |
| Exp-02 | `size-250`     | Stability   | 250         | 512        | 42   | No          |
| Exp-03 | `size-500`     | Stability   | 500         | 512        | 42   | No          |
| Exp-04 | `baseline-1000`| Stability   | 1000        | 512        | 42   | **Yes**     |
| Exp-05 | `maxlen-128`   | Truncation  | 500         | 128        | 42   | No          |
| Exp-06 | `maxlen-256`   | Truncation  | 500         | 256        | 42   | No          |
| Exp-07 | `seed-43`      | Variance    | 500         | 512        | 43   | No          |
| Exp-08 | `seed-44`      | Variance    | 500         | 512        | 44   | No          |

**Shared anchors (avoids duplicate runs):**
- Exp-03 (`size-500`) is the `max-length=512` point of the truncation sweep → compare against Exp-05 and Exp-06
- Exp-03 (`size-500`) is also the `seed=42` point of the variance sweep → compare against Exp-07 and Exp-08

**Total runs:** 8 tracked, 1 registered model version.
