"""Experiment framework for Player10 Monte Carlo runs."""

from .planner import (
    ExperimentRunner,
    ParameterRange,
    ExperimentPlanBuilder,
    ExperimentPlan,
)

# Backwards compatibility aliases with clearer naming.
TestBuilder = ExperimentPlanBuilder
TestConfiguration = ExperimentPlan
FlexibleTestRunner = ExperimentRunner

__all__ = [
    "ExperimentRunner",
    "ExperimentPlan",
    "ExperimentPlanBuilder",
    "FlexibleTestRunner",
    "ParameterRange",
    "TestBuilder",
    "TestConfiguration",
]
