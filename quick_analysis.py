#!/usr/bin/env python3
"""Quick analysis of experiment results."""

import json
from pathlib import Path


def analyze_results():
    results_file = Path(
        "players/player_10/results/20250927_132912_exp_selfplay_grid.json"
    )

    if not results_file.exists():
        return "Results file not found"

    file_size_mb = results_file.stat().st_size / 1024 / 1024
    print(f"File size: {file_size_mb:.1f} MB")

    try:
        with open(results_file, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            print(f"Number of simulation results: {len(data)}")

            if data:
                # Analyze first result to understand structure
                sample = data[0]
                print(f"\nSample result keys: {list(sample.keys())}")

                if "total_score" in sample:
                    scores = [
                        r.get("total_score", 0) for r in data if "total_score" in r
                    ]
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        max_score = max(scores)
                        min_score = min(scores)
                        print(f"\nScore summary:")
                        print(f"  Average: {avg_score:.2f}")
                        print(f"  Range: {min_score:.2f} - {max_score:.2f}")

                # Check parameter coverage
                if "altruism" in sample:
                    altruisms = sorted(
                        set(r.get("altruism") for r in data if "altruism" in r)
                    )
                    taus = sorted(set(r.get("tau") for r in data if "tau" in r))
                    print(f"\nParameter coverage:")
                    print(f"  Altruism values: {altruisms}")
                    print(f"  Tau values: {taus}")

        else:
            print("Unexpected data format")

    except Exception as e:
        print(f"Error reading file: {e}")
        return None


if __name__ == "__main__":
    analyze_results()
