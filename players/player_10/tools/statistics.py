"""Shared statistical utilities for Player10 simulation analysis.

This module centralizes the data-munging and statistical helpers that used to
live exclusively inside the Jupyter notebook (``Analyse_results.ipynb``).
Keeping them here lets the CLI, Plotly dashboard, and any future scripts reuse
identical logic without copy/paste.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np

try:  # pandas and seaborn tooling are optional at runtime
	import pandas as pd
except Exception:  # pragma: no cover - pandas might not be installed
	pd = None  # type: ignore


SimulationResult = Any  # Avoid importing heavy simulation modules at import time


def _require_pandas() -> None:
	"""Raise a helpful error if pandas is unavailable."""
	if pd is None:  # pragma: no cover - exercised only when pandas missing
		raise ImportError(
			'pandas is required for this analysis helper. '
			'Install it with `pip install pandas` or add it to your environment.'
		)


def _config_value(config: Any, attr: str, default: Any = None) -> Any:
	"""Return ``attr`` from ``config`` whether it is an object or mapping."""
	if config is None:
		return default
	if hasattr(config, attr):
		return getattr(config, attr)
	if isinstance(config, Mapping):
		return config.get(attr, default)
	return default


def _get(source: Any, attr: str, default: Any = None) -> Any:
	if isinstance(source, Mapping):
		return source.get(attr, default)
	return getattr(source, attr, default)


def results_to_records(results: Sequence[SimulationResult]) -> list[dict[str, Any]]:
	"""Flatten raw simulation results into plain dictionaries.

	The structure mirrors the dataframe produced in the legacy notebook and
	includes:
	- core configuration knobs
	- weight parameters
	- standard run-level outcomes
	- optional score breakdown components (prefixed with ``shared_``)
	- derived ``length_utilization`` when possible
	"""
	records: list[dict[str, Any]] = []
	for result in results:
		config = _get(result, 'config')
		row: dict[str, Any] = {
			'altruism_prob': _config_value(config, 'altruism_prob'),
			'tau_margin': _config_value(config, 'tau_margin'),
			'epsilon_fresh': _config_value(config, 'epsilon_fresh'),
			'epsilon_mono': _config_value(config, 'epsilon_mono'),
			'subjects': _config_value(config, 'subjects'),
			'memory_size': _config_value(config, 'memory_size'),
			'conversation_length_cfg': _config_value(config, 'conversation_length'),
			'seed': _config_value(config, 'seed'),
			'min_samples_pid': _config_value(config, 'min_samples_pid'),
			'ewma_alpha': _config_value(config, 'ewma_alpha'),
			'importance_weight': _config_value(config, 'importance_weight'),
			'coherence_weight': _config_value(config, 'coherence_weight'),
			'freshness_weight': _config_value(config, 'freshness_weight'),
			'monotony_weight': _config_value(config, 'monotony_weight'),
			'total_score': _get(result, 'total_score'),
			'player10_score': _get(result, 'player10_total_mean'),
			'player10_individual': _get(result, 'player10_individual_mean'),
			'player10_rank': _get(result, 'player10_rank_mean'),
			'player10_gap_to_best': _get(result, 'player10_gap_to_best'),
			'player10_instances': _get(result, 'player10_instances'),
			'best_total_score': _get(result, 'best_total_score'),
			'conversation_length': _get(result, 'conversation_length'),
			'early_termination': float(_get(result, 'early_termination', 0.0)),
			'pause_count': _get(result, 'pause_count'),
			'unique_items_used': _get(result, 'unique_items_used'),
			'execution_time': _get(result, 'execution_time'),
		}

		score_breakdown = _get(result, 'score_breakdown', {}) or {}
		for component, value in score_breakdown.items():
			if component == 'total':
				continue
			row[f'shared_{component}'] = value

		conversation_length_cfg = row.get('conversation_length_cfg')
		conversation_length = row.get('conversation_length')
		if conversation_length_cfg and conversation_length:
			with np.errstate(divide='ignore', invalid='ignore'):
				row['length_utilization'] = (
					float(conversation_length) / float(conversation_length_cfg)
					if conversation_length_cfg
					else None
				)
		records.append(row)
	return records


def results_dataframe(results: Sequence[SimulationResult]) -> pd.DataFrame:
	"""Return a pandas ``DataFrame`` mirroring the notebook's structure."""
	_require_pandas()
	return pd.DataFrame(results_to_records(results))  # type: ignore[return-value]


def player_metrics_long(results: Sequence[SimulationResult]) -> pd.DataFrame:
	"""Explode ``player_metrics`` into a long-form dataframe."""
	_require_pandas()
	rows: list[dict[str, Any]] = []
	for result in results:
		metrics = _get(result, 'player_metrics', {}) or {}
		config = _get(result, 'config')
		base = {
			'altruism_prob': _config_value(config, 'altruism_prob'),
			'tau_margin': _config_value(config, 'tau_margin'),
			'epsilon_fresh': _config_value(config, 'epsilon_fresh'),
			'epsilon_mono': _config_value(config, 'epsilon_mono'),
			'seed': _config_value(config, 'seed'),
		}
		for label, data in metrics.items():
			rows.append(
				{
					**base,
					'label': label,
					'class_name': data.get('class_name'),
					'alias': data.get('alias'),
					'total': data.get('total'),
					'shared': data.get('shared'),
					'individual': data.get('individual'),
					'rank': data.get('rank'),
				}
			)
	return pd.DataFrame(rows)  # type: ignore[return-value]


def bootstrap_ci(
    df: pd.DataFrame,
	group_cols: Sequence[str],
	metric: str,
	*,
	iterations: int = 1000,
	confidence: float = 0.95,
	random_state: int | np.random.Generator | None = None,
) -> pd.DataFrame:
	"""
	Bootstrapped mean and confidence interval for ``metric`` grouped by ``group_cols``.
	"""
	_require_pandas()
	if not 0 < confidence < 1:
		raise ValueError('confidence must be between 0 and 1')
	if isinstance(random_state, np.random.Generator):
		rng = random_state
	else:
		rng = np.random.default_rng(random_state)
	alpha = (1 - confidence) / 2
	rows: list[dict[str, Any]] = []
	for key, group in df.groupby(list(group_cols)):
		values = group[metric].dropna().to_numpy()
		if not len(values):
			continue
		boot = rng.choice(values, size=(iterations, len(values)), replace=True).mean(axis=1)
		lo, hi = np.quantile(boot, [alpha, 1 - alpha])
		row = {
			'mean': float(values.mean()),
			'ci_low': float(lo),
			'ci_high': float(hi),
			'n': int(len(values)),
		}
		if isinstance(key, tuple):
			for col, value in zip(group_cols, key, strict=False):
				row[col] = value
		else:
			row[group_cols[0]] = key
		rows.append(row)
	return pd.DataFrame(rows)[[*group_cols, 'mean', 'ci_low', 'ci_high', 'n']]  # type: ignore[index]


def pairwise_deltas(
    df: pd.DataFrame,
	*,
	group_col: str = 'altruism_prob',
	metric: str = 'total_score',
) -> pd.DataFrame:
	"""Return mean deltas and Cohen's d for every pair of levels in ``group_col``."""
	_require_pandas()
	levels = sorted(df[group_col].dropna().unique())
	rows: list[dict[str, Any]] = []
	for i, a in enumerate(levels):
		x = df[df[group_col] == a][metric].dropna()
		if not len(x):
			continue
		for b in levels[i + 1 :]:
			y = df[df[group_col] == b][metric].dropna()
			if not len(y):
				continue
			delta = y.mean() - x.mean()
			pooled = np.sqrt(
				((x.var(ddof=1) * (len(x) - 1)) + (y.var(ddof=1) * (len(y) - 1)))
				/ (len(x) + len(y) - 2)
			)
			d = float(delta / pooled) if pooled > 0 else np.nan
			rows.append(
				{
					'a': a,
					'b': b,
					'delta_mean': float(delta),
					'cohens_d': d,
					'n_a': int(len(x)),
					'n_b': int(len(y)),
				}
			)
	return pd.DataFrame(rows)  # type: ignore[return-value]


def heatmap_matrix(
	results: Sequence[SimulationResult],
	*,
	row_attr: str,
	col_attr: str,
	metric: str,
) -> tuple[list[Any], list[Any], list[list[float | None]]] | None:
	"""Aggregate results into a grid for heatmap visualisations."""
	matrix = defaultdict(lambda: defaultdict(list))
	row_values: set[Any] = set()
	col_values: set[Any] = set()
	for result in results:
		config = getattr(result, 'config', None)
		row_value = _config_value(config, row_attr)
		col_value = _config_value(config, col_attr)
		metric_value = getattr(result, metric, None)
		if metric in {'total_score', 'player10_score', 'player10_individual', 'best_total_score'}:
			metric_value = getattr(result, metric, metric_value)
		if row_value is None or col_value is None or metric_value is None:
			continue
		matrix[row_value][col_value].append(float(metric_value))
		row_values.add(row_value)
		col_values.add(col_value)
	if not row_values or not col_values:
		return None
	row_order = sorted(row_values)
	col_order = sorted(col_values)
	grid: list[list[float | None]] = []
	for row_value in row_order:
		row_data: list[float | None] = []
		for col_value in col_order:
			bucket = matrix.get(row_value, {}).get(col_value, [])
			row_data.append(sum(bucket) / len(bucket) if bucket else None)
		row_data_clean = row_data
		grid.append(row_data_clean)
	return row_order, col_order, grid


def score_buckets_by_altruism(
	results: Sequence[SimulationResult],
) -> dict[Any, dict[str, list[float]]]:
	"""Return total & Player10 score buckets grouped by altruism probability."""
	buckets: dict[Any, dict[str, list[float]]] = defaultdict(lambda: {'total': [], 'player10': []})
	for result in results:
		config = getattr(result, 'config', None)
		a = _config_value(config, 'altruism_prob')
		if a is None:
			continue
		total_value = getattr(result, 'total_score', None)
		if total_value is not None:
			buckets[a]['total'].append(float(total_value))
		p10_value = getattr(result, 'player10_total_mean', None)
		if p10_value is not None:
			buckets[a]['player10'].append(float(p10_value))
	return dict(sorted(buckets.items(), key=lambda item: item[0]))


def component_means_by_altruism(
	results: Sequence[SimulationResult],
	components: Iterable[str] = ('importance', 'coherence', 'freshness', 'nonmonotonousness'),
) -> tuple[list[Any], dict[str, list[float]]] | None:
	"""Average shared component contribution per altruism level."""
	sums: dict[Any, dict[str, float]] = defaultdict(lambda: defaultdict(float))
	counts: dict[Any, dict[str, int]] = defaultdict(lambda: defaultdict(int))
	for result in results:
		config = getattr(result, 'config', None)
		a = _config_value(config, 'altruism_prob')
		if a is None:
			continue
		breakdown = getattr(result, 'score_breakdown', None) or {}
		for key in components:
			value = breakdown.get(key)
			if value is None:
				continue
			try:
				value = float(value)
			except (TypeError, ValueError):
				continue
			sums[a][key] += value
			counts[a][key] += 1
	if not sums:
		return None
	altruism_levels = sorted(sums.keys())
	series: dict[str, list[float]] = {key: [] for key in components}
	for level in altruism_levels:
		for key in components:
			count = counts[level].get(key, 0)
			series[key].append(sums[level][key] / count if count else 0.0)
	return altruism_levels, series


def pareto_points(results: Sequence[SimulationResult]) -> list[dict[str, Any]]:
	"""Aggregate Player10 individual vs total score for Pareto-style scatter plots."""
	groups: dict[tuple[Any, Any, Any, Any], dict[str, Any]] = defaultdict(
		lambda: {
			'total_sum': 0.0,
			'total_count': 0,
			'p10_sum': 0.0,
			'p10_count': 0,
			'early_sum': 0.0,
			'early_count': 0,
		}
	)
	for result in results:
		config = getattr(result, 'config', None)
		key = (
			_config_value(config, 'altruism_prob'),
			_config_value(config, 'tau_margin'),
			_config_value(config, 'epsilon_fresh'),
			_config_value(config, 'epsilon_mono'),
		)
		if any(v is None for v in key):
			continue
		total_value = getattr(result, 'total_score', None)
		if total_value is not None:
			groups[key]['total_sum'] += float(total_value)
			groups[key]['total_count'] += 1
		p10_value = getattr(result, 'player10_individual_mean', None)
		if p10_value is not None:
			groups[key]['p10_sum'] += float(p10_value)
			groups[key]['p10_count'] += 1
		early_value = getattr(result, 'early_termination', None)
		if early_value is not None:
			groups[key]['early_sum'] += float(early_value)
			groups[key]['early_count'] += 1
	points: list[dict[str, Any]] = []
	for (altruism, tau, fresh, mono), data in groups.items():
		if not data['total_count'] or not data['p10_count']:
			continue
		points.append(
			{
				'altruism': altruism,
				'tau': tau,
				'fresh': fresh,
				'mono': mono,
				'total': data['total_sum'] / data['total_count'],
				'player10': data['p10_sum'] / data['p10_count'],
				'early': (data['early_sum'] / data['early_count']) if data['early_count'] else None,
				'runs': data['total_count'],
			}
		)
	return sorted(
		points,
		key=lambda item: (item['altruism'], item['tau'], item['fresh'], item['mono']),
	)


def seed_stability_curves(
    df: pd.DataFrame,
	*,
	group_col: str = 'altruism_prob',
	metric: str = 'total_score',
	order_col: str = 'seed',
) -> dict[Any, list[float]]:
	"""Return cumulative mean curves for ``metric`` ordered by ``order_col``."""
	_require_pandas()
	curves: dict[Any, list[float]] = {}
	ordered = df.sort_values(order_col)
	for level, group in ordered.groupby(group_col):
		values = group[metric].dropna()
		if not len(values):
			continue
		curves[level] = list(values.expanding().mean())
	return curves


def correlation_matrix(
    df: pd.DataFrame,
	*,
	columns: Sequence[str] | None = None,
) -> pd.DataFrame:
	"""Return a correlation matrix for the requested columns (numeric only)."""
	_require_pandas()
	cols = list(columns) if columns is not None else df.columns.tolist()
	available = [col for col in cols if col in df.columns]
	return df[available].corr(numeric_only=True)  # type: ignore[return-value]


def multi_heatmap_pivots(
	df: pd.DataFrame,
	*,
	fixed: str,
	row_col: str,
	col_col: str,
	metric: str,
) -> dict[Any, pd.DataFrame]:
	"""Return pivot tables used for faceted heatmaps."""
	_require_pandas()
	frames: dict[Any, pd.DataFrame] = {}
	for level, group in df.groupby(fixed):
		pivot = group.pivot_table(index=row_col, columns=col_col, values=metric, aggfunc='mean')
		frames[level] = pivot
	return frames


__all__ = [
	'results_to_records',
	'results_dataframe',
	'player_metrics_long',
	'bootstrap_ci',
	'pairwise_deltas',
	'heatmap_matrix',
	'score_buckets_by_altruism',
	'component_means_by_altruism',
	'pareto_points',
	'seed_stability_curves',
	'correlation_matrix',
	'multi_heatmap_pivots',
]
