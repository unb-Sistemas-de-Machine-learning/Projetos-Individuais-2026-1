"""
Automated evaluation script for the Literary Recommendation Agent.

Measures objective metrics for each test profile:
- Latency (seconds)
- Price coverage (% of recommendations with at least one price found)

Recommendations and justifications are printed for manual evaluation.

Usage:
    python tests/evaluate.py
    python tests/evaluate.py --k 3
    python tests/evaluate.py --output results.json
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import argparse
import json
import time
from agent import Agent

TEST_PROFILES = [
    {
        "name": "Ficção Científica",
        "books": ["Duna", "Fundação", "Neuromancer", "Fahrenheit 451"],
    },
    {
        "name": "Literatura Brasileira",
        "books": ["Dom Casmurro", "A Hora da Estrela", "Vidas Secas"],
    },
    {
        "name": "Mistério e Thriller",
        "books": ["O Nome da Rosa", "O Silêncio dos Inocentes", "Garota Exemplar", "O Código Da Vinci"],
    },
    {
        "name": "Filosofia",
        "books": ["O Mundo de Sofia", "A República", "Assim Falou Zaratustra"],
    },
    {
        "name": "Fantasia",
        "books": ["O Senhor dos Anéis", "Harry Potter e a Pedra Filosofal", "O Nome do Vento", "As Crônicas de Nárnia"],
    },
]


def evaluate_profile(agent: Agent, profile: dict, k: int) -> dict:
    print(f"\n{'='*60}")
    print(f"Profile: {profile['name']}")
    print(f"Books:   {', '.join(profile['books'])}")
    print(f"{'='*60}")

    start = time.time()
    recommendations = agent.recommend(profile["books"], k=k)
    latency = round(time.time() - start, 2)

    results = []
    for i, rec in enumerate(recommendations, 1):
        has_price = bool(rec.get("offers"))
        print(f"\n  [{i}] {rec['title']}")
        print(f"      Justification : {rec['justification']}")
        if has_price:
            print(f"      Cheapest      : R$ {rec['minimum_price']:.2f} at {rec['cheapest_store']}")
            for offer in rec["offers"]:
                print(f"                      {offer.store}: R$ {offer.price:.2f}")
        else:
            print(f"      Price         : not found")

        results.append({
            "title": rec["title"],
            "justification": rec["justification"],
            "has_price": has_price,
            "minimum_price": rec.get("minimum_price"),
            "cheapest_store": rec.get("cheapest_store", ""),
            "offers": [{"store": o.store, "price": o.price} for o in rec.get("offers", [])],
        })

    price_coverage = round(sum(r["has_price"] for r in results) / len(results) * 100, 1) if results else 0

    print(f"\n  Latency        : {latency}s")
    print(f"  Price coverage : {price_coverage}% ({sum(r['has_price'] for r in results)}/{len(results)})")

    return {
        "profile": profile["name"],
        "input_books": profile["books"],
        "latency_seconds": latency,
        "price_coverage_pct": price_coverage,
        "recommendations": results,
    }


def print_summary(profile_results: list[dict]) -> None:
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Profile':<25} {'Latency':>9} {'Price coverage':>15}")
    print(f"{'-'*60}")
    for r in profile_results:
        print(f"{r['profile']:<25} {r['latency_seconds']:>8}s {r['price_coverage_pct']:>14}%")

    avg_latency = round(sum(r["latency_seconds"] for r in profile_results) / len(profile_results), 2)
    avg_coverage = round(sum(r["price_coverage_pct"] for r in profile_results) / len(profile_results), 1)

    print(f"{'-'*60}")
    print(f"{'AVERAGE':<25} {avg_latency:>8}s {avg_coverage:>14}%")


def main():
    parser = argparse.ArgumentParser(description="Evaluate the Literary Recommendation Agent.")
    parser.add_argument("--k", type=int, default=5, help="Recommendations per profile (default: 5)")
    parser.add_argument("--output", type=str, default=None, help="Save results to JSON file")
    args = parser.parse_args()

    print("Loading agent...")
    agent = Agent()
    print(f"Running {len(TEST_PROFILES)} profiles with k={args.k}...")

    profile_results = []
    for profile in TEST_PROFILES:
        result = evaluate_profile(agent, profile, k=args.k)
        profile_results.append(result)

    print_summary(profile_results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(profile_results, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
