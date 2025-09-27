# Player10 Monte Carlo Experiment Plans

This document groups the upcopython -m players.player_10.tools.run \
  --name exp_mixed_cohorts_p10x10 \
  --altruism 0.0 0.2 0.5 1.0  --players '{"p10": 5, "{px}": 1}' '{"p10": 5, "{px}": 2}' '{"p10": 5, "{px}": 3}' '{"p10": 5, "{px}": 4}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 15 \
  --parallel --tau -0.05 0 0.05 \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 3 5 \
  --w-importance 1 \
  --w-coherence 1 1.05 \
  --w-freshness 1 \
  --w-monotony 1 2 \
  --players '{"p10": 10}' \
  --subjects 50 --memory-size 25 --conversation-length 100 \
  --simulations 15 \
  --parallelo campaigns into themed experiment blocks. Each block specifies the purpose, recommended parameter ranges, and sample CLI invocations using the enhanced runner.

All commands assume execution from the project root with the existing CLI:

```
python -m players.player_10.tools.run [options]
```

Use `--stats-ci`, `--stats-pairwise`, and `--analysis-columns` during post-processing to summarise outcomes.

---

## 1. `exp_selfplay_grid` – Pure Self-Play Parameter Sweep

**Purpose**: explore the altruism / τ / ε / weight grid when all agents are Player10. Identifies internal trade-offs without external noise.

**Key ranges** (optimized for ≤10k simulations):
- `--altruism 0.0 0.2 0.5 1.0`
- `--tau -0.05 0 0.05`
- `--epsilon-fresh 0.03 0.05 0.1`
- `--epsilon-mono 0.03 0.05 0.1`
- `--min-samples 3 5`
- `--w-importance 1`
- `--w-coherence 1 1.05`
- `--w-freshness 1`
- `--w-monotony 1 2`
- `--players '{"p10": 10}'`
- `--subjects 30` `--memory-size 25` `--conversation-length 100` (defaults can be overridden later)

**Sample command**:

```
python -m players.player_10.tools.run \
  --name exp_selfplay_grid \
  --altruism 0.0 0.2 0.5 1.0 \
  --tau -0.05 0 0.05 \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 3 5 \
  --w-importance 1 \
  --w-coherence 1 1.05 \
  --w-freshness 1 \
  --w-monotony 1 2 \
  --players '{"p10": 10}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 15 \
  --parallel
```

---

## 2. `exp_roster_effects` – Roster Composition Impact

**Purpose**: How does roster composition affect P10's performance? Uses optimal parameters from exp_selfplay_grid to isolate roster effects.

**Rosters to iterate** (prefer one of each archetype unless otherwise noted):
1. `{"p10": 10}` (pure baseline)
2. `{"p10": 5, "p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1}` (one each numbered agent)
3. `{"p10": 5, "p1": 2, "p2": 2, "p3": 2, "p4": 2, "p5": 2}` (two each — optional if runtime allows)
4. `{"p10": 4, "prp": 1, "pr": 1, "ps": 1, "pc": 1}` (one each of random/strategy archetypes)
5. `{"p10": 2, "prp": 2}` (balanced random-pausing stress)
6. `{"p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1}` (no P10 baseline with one each)

**Approach**: Use optimal parameters from exp_selfplay_grid results, vary only roster composition. Focus on roster effects, not parameter effects.

**Sample command (per roster)**:

```
python -m players.player_10.tools.run \
  --name exp_roster_effects \
  --altruism 0.5 \
  --tau 0 \
  --epsilon-fresh 0.05 \
  --epsilon-mono 0.05 \
  --min-samples 3 \
  --w-importance 1 \
  --w-coherence 1.05 \
  --w-freshness 1 \
  --w-monotony 2 \
  --players '{"p10": 10}' '{"p10": 8, "p1": 1, "p2": 1}' '{"p10": 6, "p1": 2, "p2": 2}' '{"p10": 5, "p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1}' '{"p1": 2, "p2": 2, "p3": 2, "p4": 2, "p5": 2}' \
  --subjects 50 --memory-size 25 --conversation-length 100 \
  --simulations 20 \
  --parallel
```

**Sample command (per roster)**:

```
python -m players.player_10.tools.run \
  --name exp_mixed_cohorts_p10x10 \
  --altruism 0.0 0.1 0.2 0.4 0.8 1.0 \
  --tau -0.2 -0.1 -0.05 0 0.05 0.1 0.2 0.4 \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 1 3 5 8 \
  --w-importance 0.5 1 1.5 \
  --w-coherence 0.5 1 1.05 1.5 \
  --w-freshness 0.5 1 1.5 \
  --w-monotony 0.5 1 1.5 2 2.5 \
  --players '{"p10": 10}' \
  --subjects 50 --memory-size 25 --conversation-length 100 \
  --simulations 10 \
  --parallel
```

Duplicate the run for each roster, adjusting `--name` and the `--players` payload. Keep a no-P10 run (`exp_mixed_cohorts_no_p10`) to quantify value-add.

---

## 3. `exp_noise_tolerance` – Random Player Stress Test

**Purpose**: How does P10's performance degrade as random player ratio increases? Tests robustness to unpredictable opponents.

**Approach**: Use optimal parameters, systematically increase random player ratio from 0% to 90%.

**Command template**:

```
python -m players.player_10.tools.run \
  --name exp_noise_tolerance \
  --altruism 0.5 \
  --tau 0 \
  --epsilon-fresh 0.05 \
  --epsilon-mono 0.05 \
  --min-samples 3 \
  --w-importance 1 \
  --w-coherence 1.05 \
  --w-freshness 1 \
  --w-monotony 2 \
  --players '{"p10": 10}' '{"p10": 9, "pr": 1}' '{"p10": 8, "pr": 2}' '{"p10": 6, "pr": 4}' '{"p10": 4, "pr": 6}' '{"p10": 2, "pr": 8}' '{"p10": 1, "pr": 9}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 15 \
  --parallel
```

Repeat for the other random mixes.

---

## 4. `exp_pairwise_opponents` – Pairwise Comparisons with Single Archetypes

**Purpose**: avoid roster bias by pairing Player10 with one opponent archetype at a time, scaling that opponent count from 1→4. Provides clean matchup profiles.

**Loop**:
- For each opponent code `px` in `{p1, p2, p3, p4, p5, pr, prp}` run:

```
python -m players.player_10.tools.run \
  --name exp_pairwise_{px} \
  --altruism 0.0 0.5 1.0 \
  --tau -0.05 0 0.05 \
  --epsilon-fresh 0.05 \
  --epsilon-mono 0.05 \
  --min-samples 3 \
  --w-importance 1 \
  --w-coherence 1 1.05 \
  --w-freshness 1 \
  --w-monotony 1 2 \
  --players '{"p10": 5, "{px}": 1}' '{"p10": 5, "{px}": 2}' '{"p10": 5, "{px}": 3}' '{"p10": 5, "{px}": 4}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 15 \
  --parallel
```

- Mirror each run without Player10 (`{"{px}": n}`) to estimate value-add.

---

## 5. `exp_resource_scaling` – Resource Sensitivity Study

**Purpose**: hold promising altruism/τ combinations and vary conversation length, subject count, and memory capacity to map performance vs resource availability.

**Core settings**:
- Use mid-range behavioural settings identified earlier (e.g. `--altruism 0.2 0.5 0.8`, `--tau -0.05 0 0.05 0.1`).
- `--subjects 10 30 50 100`
- `--memory-size 5 10 25 50 100 1000`
- `--conversation-length 10 25 50 100 200 1000`
- Players: run twice: once with `{"p10": 10}`, once with `{"p10": 5, "pr": 5}` to see scaling with noise.

**Command skeleton**:

```
python -m players.player_10.tools.run \
  --name exp_resource_scaling_selfplay \
  --altruism 0.0 0.5 1.0 \
  --tau 0 \
  --epsilon-fresh 0.05 \
  --epsilon-mono 0.05 \
  --min-samples 3 \
  --w-importance 1 \
  --w-coherence 1 \
  --w-freshness 1 \
  --w-monotony 1 \
  --subjects 10 30 50 \
  --memory-size 5 25 100 \
  --conversation-length 25 50 100 \
  --players '{"p10": 10}' \
  --simulations 15 \
  --parallel
```

Set `--players '{"p10":5,"pr":5}'` for the noisy counterpart.

---

## 6. `exp_component_ablation` – Score Component Ablation Study

**Purpose**: What happens when you disable each scoring component? Tests which components are essential vs optional for good performance.

**Configuration**:
- Use optimal parameters as baseline, then systematically disable each component by setting its weight to 0
- Test: importance-only, coherence-only, freshness-only, monotony-only, and all-components
- Run on both self-play and mixed roster to see if component importance changes with context

**Command**:

```
python -m players.player_10.tools.run \
  --name exp_component_ablation \
  --altruism 0.5 \
  --tau 0 \
  --epsilon-fresh 0.05 \
  --epsilon-mono 0.05 \
  --min-samples 3 \
  --w-importance 0 1 \
  --w-coherence 0 1.05 \
  --w-freshness 0 1 \
  --w-monotony 0 2 \
  --players '{"p10": 10}' '{"p10": 6, "p1": 2, "p2": 2}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 20 \
  --parallel
```

---

## 7. `exp_value_add` – With vs Without Player10

**Purpose**: quantify Player10’s contribution across contexts using unbiased opponent selections.

**Procedure**:
- Choose 3–4 top-performing (altruism, τ, ε) configurations from earlier experiments.
- For each configuration run two scenarios:
  1. All archetypes, including Player10: `--players '{"p10": 5, "p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1, "pr": 1, "prp": 1, "ps": 1, "pc": 1}'`
  2. All archetypes without Player10: `--players '{"p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1, "pr": 1, "prp": 1, "ps": 1, "pc": 1}'`

**Command template**:

```
python -m players.player_10.tools.run \
  --name exp_value_add_case1 \
  --altruism 0.0 0.5 1.0 \
  --tau -0.05 0 0.05 \
  --epsilon-fresh 0.05 \
  --epsilon-mono 0.05 \
  --min-samples 3 \
  --w-importance 1 \
  --w-coherence 1 \
  --w-freshness 1 \
  --w-monotony 1 2 \
  --players '{"p10": 5, "p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1, "pr": 1, "prp": 1, "ps": 1, "pc": 1}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 15 \
  --parallel
```

Follow with the no-P10 roster to measure delta.

---

## Analysis Checklist

For each experiment run:
- Save result JSONs into experiment-specific subfolders (e.g. `players/player_10/results/exp_selfplay_grid/`).
- Run the analyzer CLI:

```
python -m players.player_10.tools.analyze <results.json> \
  --analysis \
  --analysis-columns total_score player10_score player10_rank player10_gap_to_best \
  --ci --pairwise \
  --dtype-filter float
```

- Capture key observations (top configs, CI overlaps, effect sizes) in a companion report to build the narrative around “why” certain parameterizations work in specific contexts.

This suite balances exhaustive behavioural coverage with scenario-focused studies, enabling a thorough understanding of Player10’s parameter sensitivities and contextual strengths.
