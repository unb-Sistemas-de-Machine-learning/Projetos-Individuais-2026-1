from mlflow.tracking import MlflowClient

from src.config import MLFLOW_EXPERIMENT_FINETUNING, MLFLOW_EXPERIMENT_SERVING, MLFLOW_TRACKING_URI


def summarize_recent_runs(experiment_name, n_runs=5):
    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        return []

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=n_runs,
        order_by=["attributes.start_time DESC"],
    )

    summary = []
    for run in runs:
        summary.append(
            {
                "run_id": run.info.run_id,
                "status": run.info.status,
                "metrics": run.data.metrics,
                "params": run.data.params,
            }
        )
    return summary


def print_recent_runs():
    print("\n=== FINETUNING / EVALUATION RUNS ===")
    for run in summarize_recent_runs(MLFLOW_EXPERIMENT_FINETUNING):
        print(run)

    print("\n=== SERVING RUNS ===")
    for run in summarize_recent_runs(MLFLOW_EXPERIMENT_SERVING):
        print(run)


def summarize_serving_kpis(n_runs=20):
    runs = summarize_recent_runs(MLFLOW_EXPERIMENT_SERVING, n_runs=n_runs)
    if not runs:
        return {}

    latencies = [run["metrics"].get("latency_ms") for run in runs if "latency_ms" in run["metrics"]]
    accepted_ratio = [run["metrics"].get("accepted_ratio") for run in runs if "accepted_ratio" in run["metrics"]]
    rejected_ratio = [run["metrics"].get("rejected_ratio") for run in runs if "rejected_ratio" in run["metrics"]]

    summary = {
        "runs_analyzed": len(runs),
        "avg_latency_ms": sum(latencies) / len(latencies) if latencies else None,
        "avg_accepted_ratio": sum(accepted_ratio) / len(accepted_ratio) if accepted_ratio else None,
        "avg_rejected_ratio": sum(rejected_ratio) / len(rejected_ratio) if rejected_ratio else None,
    }
    return summary
