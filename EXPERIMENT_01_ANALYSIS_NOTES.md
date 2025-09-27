# Player10 Experiment Results Analysis

## Experiment 1: `exp_selfplay_grid` - Pure Self-Play Parameter Sweep

**Date**: September 27, 2025  
**Status**: ✅ **COMPLETED SUCCESSFULLY**  
**Results File**: `players/player_10/results/20250927_132912_exp_selfplay_grid.json`  
**Dashboard**: `players/player_10/results/dashboards/20250927_142050_exp_selfplay_grid_dashboard.html`  

---

## 📊 Execution Summary

- **Total Simulations**: 12,960 (100% completed)
- **Parameter Combinations**: 864 unique configurations
- **Simulations per Combination**: 15
- **File Size**: 54.1 MB
- **Execution Time**: ~30 minutes with parallel processing
- **Runtime Environment**: Pure self-play (all Player10 agents)

### Parameter Grid Coverage
- **Altruism**: [0.0, 0.2, 0.5, 1.0] → 4 values
- **Tau Margin**: [-0.05, 0.0, 0.05] → 3 values  
- **Epsilon Fresh**: [0.03, 0.05, 0.1] → 3 values
- **Epsilon Mono**: [0.03, 0.05, 0.1] → 3 values
- **Min Samples**: [3, 5] → 2 values
- **Coherence Weight**: [1.0, 1.05] → 2 values
- **Monotony Weight**: [1.0, 2.0] → 2 values
- **Fixed Parameters**: subjects=30, memory_size=25, conversation_length=100

**Grid Validation**: 4×3×3×3×2×2×2 = 864 combinations ✓

---

## 🎯 Key Findings

### 1. **Performance Distribution**
- **Total Score Range**: 80.94 - 149.95
- **Mean Score**: 124.80 ± 17.32
- **Score Variance**: Moderate spread indicating meaningful parameter effects

### 2. **Component Score Breakdown**
| Component | Mean | Std Dev | Observations |
|-----------|------|---------|--------------|
| **Importance** | 46.85 | 4.56 | Stable, low variance |
| **Coherence** | 33.08 | 37.74 | ⚠️ **HIGH VARIANCE** - strong parameter sensitivity |
| **Freshness** | 45.45 | 24.23 | Moderate variance |
| **Non-monotony** | -0.58 | 0.86 | Small negative impact, consistent |

### 3. **🚨 CRITICAL DISCOVERY: Altruism Impact**

**Performance by Altruism Level** (3,240 runs each):

| Altruism | Mean Score | Std Dev | Performance vs Baseline |
|----------|------------|---------|------------------------|
| **0.0** | 134.50 | 4.22 | Baseline (optimal) |
| **0.2** | 134.68 | 4.07 | +0.18 (negligible) |
| **0.5** | 134.05 | 4.22 | -0.45 (minimal) |
| **1.0** | 95.96 | 6.21 | ⚠️ **-38.54 (SEVERE PENALTY)** |

**Key Insight**: **Extreme altruism (1.0) is severely detrimental in self-play contexts**, causing a 29% performance drop. This suggests that pure altruistic behavior prevents effective strategic coordination among identical agents.

---

## 💡 Strategic Insights

### 1. **Optimal Parameter Ranges**
Based on this analysis, for subsequent experiments focus on:
- **Altruism**: 0.0 - 0.5 range (avoid 1.0)
- **Coherence Investigation**: High variance suggests strong interactions with other parameters
- **Baseline Configuration**: Altruism 0.0-0.2 provides most consistent performance

### 2. **Parameter Interaction Hypotheses**
- **Coherence volatility** (σ=37.74) suggests epsilon, tau, or weight interactions
- **Altruism threshold effect** around 0.5-1.0 boundary needs investigation
- **Self-play vs mixed-roster**: Altruism penalty may behave differently with diverse opponents

### 3. **Experimental Design Validation**
- ✅ **15 simulations per combination** provided adequate statistical power
- ✅ **Parameter grid coverage** successfully captured key behavioral regimes  
- ✅ **Computational efficiency** achieved with parallel processing
- ✅ **Dashboard generation** provides comprehensive visualization

---

## 🔄 Next Experiment Recommendations

### Immediate Actions for `exp_roster_effects`:
1. **Use optimal configurations** from altruism 0.0-0.2 range
2. **Test altruism 1.0** in mixed-roster context to see if penalty persists
3. **Focus on coherence parameter interactions** in heterogeneous environments

### Parameter Selection for Roster Effects:
```bash
--altruism 0.0 0.2 0.5  # Include 0.5 for comparison, avoid 1.0 initially
--tau 0                 # Use neutral tau as baseline
--epsilon-fresh 0.05    # Mid-range epsilon values
--epsilon-mono 0.05
--min-samples 3         # Conservative sampling
--w-coherence 1.05      # Slightly enhanced coherence
--w-monotony 2          # Enhanced monotony weight
```

### Research Questions for Next Phase:
1. **Does altruism 1.0 penalty persist in mixed rosters?**
2. **Which roster compositions amplify coherence variance?**
3. **Do optimal self-play parameters transfer to competitive contexts?**

---

## 📈 Dashboard Features Generated

The interactive dashboard includes:
- **Parameter heatmaps** showing score distributions across altruism/tau combinations
- **Component score breakdowns** with violin plots
- **Performance rankings** by parameter configuration
- **Statistical summaries** with confidence intervals
- **Correlation matrices** between parameters and outcomes

**Dashboard Location**: `players/player_10/results/dashboards/20250927_142050_exp_selfplay_grid_dashboard.html`

---

## 🏁 Conclusion

This experiment successfully established the foundational parameter landscape for Player10 in self-play contexts. The dramatic altruism penalty at 1.0 is the most significant finding and will guide parameter selection for all subsequent experiments. The framework is now validated and ready for the remaining 6 experiments.

**Status**: ✅ Ready to proceed with `exp_roster_effects`