# Player10 Monte Carlo Experiment Plans

This document groups the upcoming Monte Carlo campaigns into themed experiment blocks. Each block specifies the purpose, recommended parameter ranges, and sample CLI invocations using the enhanced runner.

All commands assume execution from the project root with the existing CLI:

```
python -m players.player_10.tools.run [options]
```

Use `--stats-ci`, `--stats-pairwise`, and `--analysis-columns` during post-processing to summarise outcomes.

---

## 1. `exp_selfplay_grid` – Pure Self-Play Parameter Sweep

**Purpose**: explore the altruism / τ / ε / weight grid when all agents are Player10. Identifies internal trade-offs without external noise.

**Key ranges**:
- `--altruism 0.0 0.1 0.2 0.4 0.8 1.0`
- `--tau -0.2 -0.1 -0.05 0 0.05 0.1 0.2 0.4`
- `--epsilon-fresh 0.03 0.05 0.1`
- `--epsilon-mono 0.03 0.05 0.1`
- `--min-samples 1 3 5 8`
- `--w-importance 0.5 1 1.5`
- `--w-coherence 0.5 1 1.05 1.5`
- `--w-freshness 0.5 1 1.5`
- `--w-monotony 0.5 1 1.5 2 2.5`
- `--players '{"p10": 10}'`
- `--subjects 30` `--memory-size 25` `--conversation-length 100` (defaults can be overridden later)

**Sample command**:

```
python -m players.player_10.tools.run \
  --name exp_selfplay_grid \
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
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 80
```

---

## 2. `exp_mixed_cohorts` – Structured Mixed Rosters

**Purpose**: evaluate our policy alongside curated player archetypes; vary roster counts to detect synergies/conflicts.

**Rosters to iterate** (prefer one of each archetype unless otherwise noted):
1. `{"p10": 10}` (pure baseline)
2. `{"p10": 5, "p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1}` (one each numbered agent)
3. `{"p10": 5, "p1": 2, "p2": 2, "p3": 2, "p4": 2, "p5": 2}` (two each — optional if runtime allows)
4. `{"p10": 4, "prp": 1, "pr": 1, "ps": 1, "pc": 1}` (one each of random/strategy archetypes)
5. `{"p10": 2, "prp": 2}` (balanced random-pausing stress)
6. `{"p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1}` (no P10 baseline with one each)

**Shared ranges**: adopt the same altruism / τ / ε / weight grid as the self-play experiment, but consider a lower simulation count per roster to control runtime. Use `--subjects 50`, `--memory-size 25`, `--conversation-length 100`.

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
  --simulations 60
```

Duplicate the run for each roster, adjusting `--name` and the `--players` payload. Keep a no-P10 run (`exp_mixed_cohorts_no_p10`) to quantify value-add.

---

## 3. `exp_random_noise` – Random Player Stress Test

**Purpose**: stress-test our policy with varying random-agent presence while keeping other knobs manageable.

**Ranges (subset to reduce combinations)**:
- `--altruism 0.1 0.3 0.5 0.7 0.9`
- `--tau -0.1 -0.05 0 0.05 0.1`
- `--epsilon-fresh 0.03 0.05 0.1`
- `--epsilon-mono 0.03 0.05 0.1`
- `--min-samples 3 5 8`
- Weights: same as main grid.
- Players: `{"p10":8,"pr":2}`, `{"p10":6,"pr":4}`, `{"p10":4,"pr":6}`
- `--subjects 30`, `--memory-size 25`, `--conversation-length 100`

**Command template**:

```
python -m players.player_10.tools.run \
  --name exp_random_noise_mix1 \
  --altruism 0.1 0.3 0.5 0.7 0.9 \
  --tau -0.1 -0.05 0 0.05 0.1 \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 3 5 8 \
  --w-importance 0.5 1 1.5 \
  --w-coherence 0.5 1 1.05 1.5 \
  --w-freshness 0.5 1 1.5 \
  --w-monotony 0.5 1 1.5 2 2.5 \
  --players '{"p10": 8, "pr": 2}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 100
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
  --altruism 0.0 0.1 0.2 0.4 0.8 1.0 \
  --tau -0.2 -0.1 -0.05 0 0.05 0.1 0.2 0.4 \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 1 3 5 8 \
  --w-importance 0.5 1 1.5 \
  --w-coherence 0.5 1 1.05 1.5 \
  --w-freshness 0.5 1 1.5 \
  --w-monotony 0.5 1 1.5 2 2.5 \
  --players '{"p10": 5, "{px}": 1}' '{"p10": 5, "{px}": 2}' '{"p10": 5, "{px}": 3}' '{"p10": 5, "{px}": 4}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 60
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
  --altruism 0.2 0.5 0.8 \
  --tau -0.05 0 0.05 0.1 \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 3 5 8 \
  --w-importance 0.5 1 1.5 \
  --w-coherence 0.5 1 1.05 1.5 \
  --w-freshness 0.5 1 1.5 \
  --w-monotony 0.5 1 1.5 2 2.5 \
  --subjects 10 30 50 100 \
  --memory-size 5 10 25 50 100 1000 \
  --conversation-length 10 25 50 100 200 1000 \
  --players '{"p10": 10}' \
  --simulations 50
```

Set `--players '{"p10":5,"pr":5}'` for the noisy counterpart.

---

## 6. `exp_weight_focus` – Score Component Sensitivity

**Purpose**: isolate the component weights while keeping behaviour knobs tight; explains the marginal value of importance/coherence/freshness/monotony tuning.

**Configuration**:
- Fix altruism/τ around midpoints from earlier winners (e.g. `--altruism 0.2 0.4 0.8`, `--tau -0.05 0 0.05`).
- Retain `--epsilon-fresh 0.03 0.05`, `--epsilon-mono 0.03 0.05`, `--min-samples 3 5`.
- Expand weights aggressively: `--w-importance 0.5 1 1.5`, `--w-coherence 0.5 1 1.05 1.5`, `--w-freshness 0.5 1 1.5`, `--w-monotony 0.5 1 1.5 2 2.5`.
- Run both on self-play and mixed rosters (`{"p10":8,"p1":1,"p2":1}`) to see context shifts.

**Command**:

```
python -m players.player_10.tools.run \
  --name exp_weight_focus_mixed \
  --altruism 0.2 0.4 0.8 \
  --tau -0.05 0 0.05 \
  --epsilon-fresh 0.03 0.05 \
  --epsilon-mono 0.03 0.05 \
  --min-samples 3 5 \
  --w-importance 0.5 1 1.5 \
  --w-coherence 0.5 1 1.05 1.5 \
  --w-freshness 0.5 1 1.5 \
  --w-monotony 0.5 1 1.5 2 2.5 \
  --players '{"p10": 8, "p1": 1, "p2": 1}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 80
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
  --altruism <values> \
  --tau <values> \
  --epsilon-fresh 0.03 0.05 0.1 \
  --epsilon-mono 0.03 0.05 0.1 \
  --min-samples 3 5 8 \
  --w-importance 0.5 1 1.5 \
  --w-coherence 0.5 1 1.05 1.5 \
  --w-freshness 0.5 1 1.5 \
  --w-monotony 0.5 1 1.5 2 2.5 \
  --players '{"p10": 5, "p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1, "pr": 1, "prp": 1, "ps": 1, "pc": 1}' \
  --subjects 30 --memory-size 25 --conversation-length 100 \
  --simulations 100
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
