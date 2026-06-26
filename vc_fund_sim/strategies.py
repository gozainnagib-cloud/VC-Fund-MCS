from __future__ import annotations

from dataclasses import dataclass

from vc_fund_sim.engine import (
    FundAssumptions,
    OutcomeDistribution,
    SimulationConfig,
    SimulationSummary,
    run_simulations,
    summarize_simulations,
)


@dataclass(frozen=True)
class StrategyComparison:
    strategy_name: str
    summary: SimulationSummary
    fund: FundAssumptions


def default_strategies() -> dict[str, FundAssumptions]:
    return {
        "Concentrated Seed": FundAssumptions(
            fund_size=50_000_000,
            portfolio_size=18,
            target_ownership=0.12,
            dilution_per_round=0.22,
            average_future_rounds=2,
            reserve_ratio=0.35,
            follow_on_success_quality=0.65,
        ),
        "Diversified Seed": FundAssumptions(
            fund_size=50_000_000,
            portfolio_size=45,
            target_ownership=0.07,
            dilution_per_round=0.20,
            average_future_rounds=2,
            reserve_ratio=0.25,
            follow_on_success_quality=0.55,
        ),
        "Reserve Heavy": FundAssumptions(
            fund_size=50_000_000,
            portfolio_size=28,
            target_ownership=0.10,
            dilution_per_round=0.20,
            average_future_rounds=2,
            reserve_ratio=0.50,
            follow_on_success_quality=0.70,
        ),
        "Series A Ownership": FundAssumptions(
            fund_size=100_000_000,
            portfolio_size=14,
            target_ownership=0.18,
            dilution_per_round=0.16,
            average_future_rounds=2,
            reserve_ratio=0.40,
            follow_on_success_quality=0.60,
        ),
    }


def compare_strategies(
    simulation_count: int = 5_000,
    seed: int = 1,
    distribution: OutcomeDistribution | None = None,
) -> list[StrategyComparison]:
    outcome_distribution = distribution or OutcomeDistribution.seed_stage_default()
    comparisons = []
    for offset, (name, fund) in enumerate(default_strategies().items()):
        results = run_simulations(
            SimulationConfig(
                fund=fund,
                outcome_distribution=outcome_distribution,
                simulation_count=simulation_count,
                seed=seed + offset,
            )
        )
        comparisons.append(StrategyComparison(name, summarize_simulations(results), fund))
    return sorted(comparisons, key=lambda item: item.summary.mean_multiple, reverse=True)
