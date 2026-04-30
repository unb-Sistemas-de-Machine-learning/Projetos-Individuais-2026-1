#!/usr/bin/env python

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.finetune_train import run_finetuning_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Executa pipeline de treinamento com fine-tuning"
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Não registra o modelo no MLflow Model Registry",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("PIPELINE")
    print("=" * 80)
    print(f"Registrar modelo: {not args.no_register}")
    print("=" * 80 + "\n")

    result = run_finetuning_pipeline(register_model=not args.no_register)

    print("\n" + "=" * 80)
    print("RESULTADOS")
    print("=" * 80)
    print(f"Fine-tuning Run ID: {result['finetune_run_id']}")
    print(f"Evaluation Run ID: {result['evaluation_run_id']}")
    print(f"Model Type: {result['model_type']}")
    print(f"Model URI: {result['model_uri']}")
    print(f"\nMétricas:")
    for metric_name, metric_value in result['metrics'].items():
        print(f"  {metric_name}: {metric_value:.4f}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
