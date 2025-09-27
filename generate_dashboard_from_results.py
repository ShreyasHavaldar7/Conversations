#!/usr/bin/env python3
"""Generate dashboard from existing results file."""

import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from players.player_10.tools.dashboard import generate_dashboard


def main():
    # Load the results file
    results_file = Path(
        "players/player_10/results/20250927_132912_exp_selfplay_grid.json"
    )

    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        return

    print(f"Loading results from: {results_file}")
    print(f"File size: {results_file.stat().st_size / 1024 / 1024:.1f} MB")

    # Load the JSON data
    with open(results_file, "r") as f:
        data = json.load(f)

    # Extract the results list from the data structure
    if isinstance(data, dict) and "results" in data:
        results = data["results"]
        metadata = data.get("metadata", {})
        print(
            f"Loaded {len(results)} simulation results from {metadata.get('run_name', 'unknown')}"
        )
    else:
        results = data
        print(f"Loaded {len(results)} simulation results")

    # Convert to the expected format (list of objects with .config attribute)
    from types import SimpleNamespace

    converted_results = []
    for result in results:
        # Create a namespace object that mimics the expected structure
        ns_result = SimpleNamespace()
        ns_result.config = SimpleNamespace(**result["config"])

        # Copy all other attributes
        for key, value in result.items():
            if key != "config":
                setattr(ns_result, key, value)

        converted_results.append(ns_result)

    # Create dashboards directory
    dashboard_dir = Path("players/player_10/results/dashboards")
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # Generate dashboard
    try:
        dashboard_path = generate_dashboard(
            converted_results,
            {},  # No additional analysis
            type("Config", (), {"name": "exp_selfplay_grid"}),  # Mock config
            dashboard_dir,
            open_browser=True,
        )

        if dashboard_path:
            print(f"Dashboard generated successfully: {dashboard_path}")
            print(f"Open in browser: file://{dashboard_path.resolve()}")
        else:
            print("Dashboard generation failed")

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
