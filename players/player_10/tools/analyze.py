"""Standalone CLI for inspecting saved Monte Carlo results.

Examples
--------
python -m players.player_10.tools.analyze results.json --analysis --plot heatmap \
    --param1 altruism_prob --param2 tau_margin
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
	import pandas as pd
except Exception:  # pragma: no cover - pandas may be optional
	pd = None  # type: ignore

if pd is None:  # pragma: no cover - guard for missing dependency
	raise SystemExit(
		'pandas is required for players.player_10.tools.analyze. '
		'Install it with `pip install pandas` before running this CLI.'
	)

from .statistics import (
	bootstrap_ci,
	multi_heatmap_pivots,
	pairwise_deltas,
	pareto_points,
	player_metrics_long,
	results_dataframe,
	results_to_records,
	score_buckets_by_altruism,
)


def _format_float(value: float | None, digits: int = 2) -> str:
	if value is None or (isinstance(value, float) and math.isnan(value)):
		return 'n/a'
	return f'{value:.{digits}f}'


def _load_results(path: Path) -> list[Any]:
	with path.open('r', encoding='utf-8') as handle:
		payload = json.load(handle)
	if isinstance(payload, dict) and 'results' in payload:
		return payload['results']
	if isinstance(payload, list):
		return payload
	raise ValueError(f'Unrecognised results schema in {path}')


def _print_table(df: pd.DataFrame, title: str) -> None:
	if df.empty:
		print(f'\n=== {title} ===\n(no data)')
		return
	print(f'\n=== {title} ===')
	print(df.to_string(index=False))


def _coerce_numeric(df: pd.DataFrame, columns: list[str]) -> None:
	"""Ensure selected columns are numeric for aggregation."""
	for col in columns:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors='coerce')


def _plot_with_matplotlib(args, df, results):  # pragma: no cover - plotting side effects
	try:
		import matplotlib.pyplot as plt
		import seaborn as sns
	except ImportError as exc:
		print(f'Plotting requires matplotlib/seaborn: {exc}')
		return

	plot = args.plot
	if plot == 'altruism':
		group = df.groupby('altruism_prob')['total_score'].agg(['mean', 'std']).reset_index()
		plt.errorbar(group['altruism_prob'], group['mean'], yerr=group['std'], marker='o')
		plt.xlabel('Altruism probability')
		plt.ylabel('Total score')
		plt.title('Total score vs altruism')
	elif plot == 'heatmap':
		pivot = df.pivot_table(
			index=args.param1,
			columns=args.param2,
			values=args.metric,
			aggfunc='mean',
		)
		sns.heatmap(pivot, annot=True, fmt='.2f', cmap='viridis')
		plt.title(f'{args.metric} heatmap')
	elif plot == 'components':
		buckets = score_buckets_by_altruism(results)
		plt.figure()
		for prob, series in buckets.items():
			plt.hist(series['total'], bins=20, alpha=0.6, label=f'{prob:.2f}')
		plt.title('Total score distribution by altruism')
		plt.legend()
	elif plot == 'pareto':
		points = pareto_points(results)
		plt.scatter([p['player10'] for p in points], [p['total'] for p in points])
		plt.xlabel('Player10 individual mean')
		plt.ylabel('Total score mean')
		plt.title('Pareto trade-off')
	elif plot == 'rank':
		dfp = player_metrics_long(results)
		if dfp.empty:
			print('No per-player metrics available.')
			return
		p10 = dfp[dfp['class_name'] == 'Player10']
		sns.violinplot(data=p10, x='altruism_prob', y='rank', inner='quartile', cut=0)
		plt.gca().invert_yaxis()
		plt.title('Player10 rank distribution')
	elif plot == 'seed':
		ordered = df.sort_values('seed')
		for prob, group in ordered.groupby('altruism_prob'):
			plt.plot(
				range(1, len(group) + 1),
				group[args.metric].expanding().mean(),
				label=f'{prob:.2f}',
			)
		plt.title(f'Seed stability for {args.metric}')
		plt.xlabel('Runs (ordered by seed)')
		plt.ylabel('Cumulative mean')
	elif plot == 'corr':
		columns = [
			'altruism_prob',
			'tau_margin',
			'epsilon_fresh',
			'epsilon_mono',
			'importance_weight',
			'coherence_weight',
			'freshness_weight',
			'monotony_weight',
			'total_score',
			'player10_score',
			'early_termination',
			'pause_count',
			'unique_items_used',
			'length_utilization',
		]
		corr = df[[c for c in columns if c in df.columns]].corr(numeric_only=True)
		sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
		plt.title('Correlation matrix')
	elif plot == 'multi-heatmap':
		pivots = multi_heatmap_pivots(
			df,
			fixed=args.fixed,
			row_col=args.param1,
			col_col=args.param2,
			metric=args.metric,
		)
		cols = len(pivots)
		fig, axes = plt.subplots(1, cols, figsize=(6 * cols, 5), sharey=True)
		if cols == 1:
			axes = [axes]
		for ax, (level, frame) in zip(axes, pivots.items(), strict=False):
			sns.heatmap(frame, ax=ax, annot=True, fmt='.2f', cmap='viridis')
			ax.set_title(f'{args.metric} | {args.fixed}={level}')
	else:
		print(f'Unknown plot type: {plot}')
		return

	if args.save:
		Path(args.save).parent.mkdir(parents=True, exist_ok=True)
		plt.savefig(args.save, dpi=300, bbox_inches='tight')
		print(f'Saved plot to {args.save}')
	else:
		plt.show()


def main() -> None:
	parser = argparse.ArgumentParser(description='Inspect saved Monte Carlo results')
	parser.add_argument('results_file', type=Path, help='Path to results JSON file')
	parser.add_argument('--analysis', action='store_true', help='Print text summary tables')
	parser.add_argument(
		'--analysis-columns',
		nargs='+',
		help='Restrict summary tables to these columns (expects exact dataframe column names)',
	)
	parser.add_argument(
		'--ci',
		action='store_true',
		help='Compute bootstrap confidence intervals by group (requires pandas).',
	)
	parser.add_argument(
		'--ci-group', nargs='+', default=['altruism_prob'], help='Grouping columns for CI'
	)
	parser.add_argument('--ci-metric', default='total_score', help='Metric used in bootstrap CI')
	parser.add_argument(
		'--ci-iterations', type=int, default=1000, help='Bootstrap iterations (default 1000)'
	)
	parser.add_argument(
		'--ci-confidence', type=float, default=0.95, help='Confidence level (default 0.95)'
	)
	parser.add_argument(
		'--pairwise', action='store_true', help='Report pairwise mean deltas & effect sizes'
	)
	parser.add_argument(
		'--pairwise-group', default='altruism_prob', help='Column defining pairwise cohorts'
	)
	parser.add_argument(
		'--pairwise-metric', default='total_score', help='Metric analysed for pairwise deltas'
	)
	parser.add_argument(
		'--plot',
		choices=[
			'altruism',
			'heatmap',
			'components',
			'pareto',
			'rank',
			'seed',
			'corr',
			'multi-heatmap',
		],
		help='Generate a quick matplotlib plot',
	)
	parser.add_argument(
		'--param1', default='altruism_prob', help='Primary parameter (rows) for heatmap plots'
	)
	parser.add_argument(
		'--param2', default='tau_margin', help='Secondary parameter (cols) for heatmap plots'
	)
	parser.add_argument(
		'--metric', default='total_score', help='Metric for heatmaps / stability / pairwise'
	)
	parser.add_argument(
		'--fixed', default='altruism_prob', help='Facet parameter for multi-heatmap'
	)
	parser.add_argument('--save', help='Save plot to this path instead of showing interactively')
	parser.add_argument('--seed', type=int, help='Random seed for bootstrap sampling')

	args = parser.parse_args()
	results_path = args.results_file
	if not results_path.exists():
		raise SystemExit(f'File not found: {results_path}')

	results_raw = _load_results(results_path)
	df_records = results_to_records(results_raw)
	if not df_records:
		raise SystemExit('No runs found in results file.')
	df = results_dataframe(results_raw)
	numeric_columns = [
		'total_score',
		'player10_score',
		'player10_individual',
		'player10_rank',
		'player10_gap_to_best',
		'best_total_score',
		'conversation_length',
		'early_termination',
		'pause_count',
		'unique_items_used',
		'execution_time',
		'altruism_prob',
		'tau_margin',
		'epsilon_fresh',
		'epsilon_mono',
		'subjects',
		'memory_size',
		'min_samples_pid',
		'ewma_alpha',
		'importance_weight',
		'coherence_weight',
		'freshness_weight',
		'monotony_weight',
	]
	_coerce_numeric(df, numeric_columns)

	if args.analysis:
		analysis_cols: list[str] = []
		if args.analysis_columns:
			requested = [col.strip() for col in args.analysis_columns if col.strip()]
			analysis_cols = [col for col in requested if col in df.columns]
			missing = sorted(set(requested) - set(analysis_cols))
			if missing:
				print(f'Warning: columns not found in dataframe: {", ".join(missing)}')

		dtype_series = df.dtypes.astype(str)
		if args.dtype_filter:
			tokens = [token.lower() for token in args.dtype_filter]
			dtype_series = dtype_series[
				dtype_series.apply(lambda s: any(token in s.lower() for token in tokens))
			]
		print('DataFrame dtypes:')
		if dtype_series.empty:
			print('(no columns match dtype filter)' if args.dtype_filter else '(no columns)')
		else:
			print(dtype_series.to_string())

		overall_default = ['total_score', 'player10_score', 'player10_individual', 'player10_rank']
		overall_cols = [col for col in (analysis_cols or overall_default) if col in df.columns]
		print('=== OVERALL ===')
		if overall_cols:
			overall = df[overall_cols].agg(['mean', 'std'])
			print(overall.to_string())
		else:
			print('(no numeric columns available)')

		group_cols = [
			c
			for c in ['altruism_prob', 'tau_margin', 'epsilon_fresh', 'epsilon_mono']
			if c in df.columns
		]
		metric_candidates = [col for col in (analysis_cols or ['total_score']) if col in df.columns]
		if group_cols and metric_candidates:
			agg_dict = {col: ['mean', 'std'] for col in metric_candidates}
			grouped = df.groupby(group_cols).agg(agg_dict)
			grouped.columns = [f'{col}_{stat}' for col, stat in grouped.columns.to_flat_index()]
			grouped = grouped.reset_index()
			counts = df.groupby(group_cols).size().reset_index(name='count')
			grouped = grouped.merge(counts, on=group_cols, how='left')
			sort_col = f'{metric_candidates[0]}_mean'
			if sort_col in grouped.columns:
				grouped = grouped.sort_values(sort_col, ascending=False)
			_print_table(grouped.head(10), 'Top configurations (group means)')
		else:
			print('\n=== Top configurations by total_score ===\n(no data)')

	if args.ci:
		if pd is None:
			print('pandas is required for bootstrap CI analysis.')
		else:
			try:
				ci_df = bootstrap_ci(
					df,
					[col.strip() for col in args.ci_group if col.strip()],
					args.ci_metric,
					iterations=args.ci_iterations,
					confidence=args.ci_confidence,
					random_state=args.seed,
				)
			except Exception as exc:
				print(f'Failed to compute bootstrap CI: {exc}')
			else:
				_print_table(ci_df, 'Bootstrap confidence intervals')

	if args.pairwise:
		if pd is None:
			print('pandas is required for pairwise delta analysis.')
		else:
			try:
				pairwise_df = pairwise_deltas(
					df,
					group_col=args.pairwise_group,
					metric=args.pairwise_metric,
				)
			except Exception as exc:
				print(f'Failed to compute pairwise deltas: {exc}')
			else:
				_print_table(pairwise_df, 'Pairwise deltas')

	if args.plot:
		_plot_with_matplotlib(args, df, results_raw)


if __name__ == '__main__':
	main()
