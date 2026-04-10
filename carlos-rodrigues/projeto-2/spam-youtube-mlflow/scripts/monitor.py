import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.monitoring import print_recent_runs, summarize_serving_kpis


if __name__ == "__main__":
    print_recent_runs()
    print("\n=== SERVING KPIs ===")
    print(summarize_serving_kpis())
