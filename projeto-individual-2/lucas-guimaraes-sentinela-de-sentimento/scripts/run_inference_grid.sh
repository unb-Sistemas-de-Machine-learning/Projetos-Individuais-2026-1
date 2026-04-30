#!/usr/bin/env bash
set -euo pipefail

# Gera múltiplos runs no experimento base,
# variando seed e subconjunto de validação.

export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-sqlite:///mlflow.db}"
export MAX_TRAIN_SAMPLES="${MAX_TRAIN_SAMPLES:-5000}"

SEEDS=(42 7)
EVAL_MAX_VALUES=(300 800)

run_idx=0
total_runs=$(( ${#SEEDS[@]} * ${#EVAL_MAX_VALUES[@]} ))

echo "Iniciando bateria do modelo base..."
echo "Tracking URI: ${MLFLOW_TRACKING_URI}"
echo "MAX_TRAIN_SAMPLES=${MAX_TRAIN_SAMPLES}"
echo "Total de runs planejados: ${total_runs}"
echo

for seed in "${SEEDS[@]}"; do
  for eval_max in "${EVAL_MAX_VALUES[@]}"; do
    run_idx=$((run_idx + 1))
    run_name="baseline-s${seed}-eval${eval_max}"
    echo "[$run_idx/$total_runs] Rodando ${run_name}"

    PIPELINE_SEED="${seed}" \
    EVAL_VALIDATION_MAX="${eval_max}" \
    PIPELINE_RUN_NAME="${run_name}" \
    python scripts/pipeline_run.py

    echo
  done
done

echo "Bateria finalizada. Compare os runs no MLflow UI."
