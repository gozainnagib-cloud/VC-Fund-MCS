from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from vc_fund_sim.engine import (
    FundAssumptions,
    OutcomeDistribution,
    SimulationConfig,
    SimulationSummary,
    run_simulations,
    summarize_simulations,
)


@dataclass(frozen=True)
class SensitivityResult:
    driver: str
    lower_label: str
    upper_label: str
    lower_median_tvpi: float
    base_median_tvpi: float
    upper_median_tvpi: float
    lower_probability_3x: float
    base_probability_3x: float
    upper_probability_3x: float

    @property
    def lower_delta_3x(self) -> float:
        return self.lower_probability_3x - self.base_probability_3x

    @property
    def upper_delta_3x(self) -> float:
        return self.upper_probability_3x - self.base_probability_3x

    @property
    def max_abs_delta_3x(self) -> float:
        return max(abs(self.lower_delta_3x), abs(self.upper_delta_3x))

    @property
    def lower_delta_tvpi(self) -> float:
        return self.lower_median_tvpi - self.base_median_tvpi

    @property
    def upper_delta_tvpi(self) -> float:
        return self.upper_median_tvpi - self.base_median_tvpi


@dataclass(frozen=True)
class SensitivityCase:
    driver: str
    lower_label: str
    upper_label: str
    lower_fund: FundAssumptions
    lower_distribution: OutcomeDistribution
    upper_fund: FundAssumptions
    upper_distribution: OutcomeDistribution


def run_sensitivity_analysis(
    fund: FundAssumptions,
    distribution: OutcomeDistribution,
    simulation_count: int = 2_500,
    seed: int = 1,
) -> list[SensitivityResult]:
    base_summary = _summarize(fund, distribution, simulation_count, seed)
    results = [
        _run_case(case, base_summary, simulation_count, seed)
        for case in _build_cases(fund, distribution)
    ]
    return sorted(results, key=lambda result: result.max_abs_delta_3x, reverse=True)


def _run_case(
    case: SensitivityCase,
    base_summary: SimulationSummary,
    simulation_count: int,
    seed: int,
) -> SensitivityResult:
    lower_summary = _summarize(case.lower_fund, case.lower_distribution, simulation_count, seed)
    upper_summary = _summarize(case.upper_fund, case.upper_distribution, simulation_count, seed)
    return SensitivityResult(
        driver=case.driver,
        lower_label=case.lower_label,
        upper_label=case.upper_label,
        lower_median_tvpi=lower_summary.median_multiple,
        base_median_tvpi=base_summary.median_multiple,
        upper_median_tvpi=upper_summary.median_multiple,
        lower_probability_3x=lower_summary.probability_return_3x,
        base_probability_3x=base_summary.probability_return_3x,
        upper_probability_3x=upper_summary.probability_return_3x,
    )


def _summarize(
    fund: FundAssumptions,
    distribution: OutcomeDistribution,
    simulation_count: int,
    seed: int,
) -> SimulationSummary:
    return summarize_simulations(
        run_simulations(
            SimulationConfig(
                fund=fund,
                outcome_distribution=distribution,
                simulation_count=simulation_count,
                seed=seed,
            )
        )
    )


def _build_cases(fund: FundAssumptions, distribution: OutcomeDistribution) -> list[SensitivityCase]:
    return [
        _fund_case(
            "Entry ownership",
            "25% lower ownership",
            "25% higher ownership",
            fund,
            distribution,
            lambda item: replace(item, target_ownership=_clamp(item.target_ownership * 0.75, 0.01, 0.30)),
            lambda item: replace(item, target_ownership=_clamp(item.target_ownership * 1.25, 0.01, 0.30)),
        ),
        _fund_case(
            "Dilution",
            "5 pp more dilution",
            "5 pp less dilution",
            fund,
            distribution,
            lambda item: replace(item, dilution_per_round=_clamp(item.dilution_per_round + 0.05, 0.0, 0.40)),
            lambda item: replace(item, dilution_per_round=_clamp(item.dilution_per_round - 0.05, 0.0, 0.40)),
        ),
        _fund_case(
            "Reserve ratio",
            "15 pp lower reserve",
            "15 pp higher reserve",
            fund,
            distribution,
            lambda item: replace(item, reserve_ratio=_clamp(item.reserve_ratio - 0.15, 0.0, 0.70)),
            lambda item: replace(item, reserve_ratio=_clamp(item.reserve_ratio + 0.15, 0.0, 0.70)),
        ),
        _fund_case(
            "Portfolio size",
            "20% fewer companies",
            "20% more companies",
            fund,
            distribution,
            lambda item: replace(item, portfolio_size=max(5, round(item.portfolio_size * 0.80))),
            lambda item: replace(item, portfolio_size=min(80, round(item.portfolio_size * 1.20))),
        ),
        _distribution_case(
            "Home-run probability",
            "1 pp lower 50x rate",
            "1 pp higher 50x rate",
            fund,
            distribution,
            lambda item: _shift_home_run_rate(item, -0.01),
            lambda item: _shift_home_run_rate(item, 0.01),
        ),
        _fund_case(
            "Follow-on selection quality",
            "20 pp lower quality",
            "20 pp higher quality",
            fund,
            distribution,
            lambda item: replace(item, follow_on_success_quality=_clamp(item.follow_on_success_quality - 0.20, 0.1, 1.0)),
            lambda item: replace(item, follow_on_success_quality=_clamp(item.follow_on_success_quality + 0.20, 0.1, 1.0)),
        ),
    ]


def _fund_case(
    driver: str,
    lower_label: str,
    upper_label: str,
    fund: FundAssumptions,
    distribution: OutcomeDistribution,
    lower: Callable[[FundAssumptions], FundAssumptions],
    upper: Callable[[FundAssumptions], FundAssumptions],
) -> SensitivityCase:
    return SensitivityCase(
        driver=driver,
        lower_label=lower_label,
        upper_label=upper_label,
        lower_fund=lower(fund),
        lower_distribution=distribution,
        upper_fund=upper(fund),
        upper_distribution=distribution,
    )


def _distribution_case(
    driver: str,
    lower_label: str,
    upper_label: str,
    fund: FundAssumptions,
    distribution: OutcomeDistribution,
    lower: Callable[[OutcomeDistribution], OutcomeDistribution],
    upper: Callable[[OutcomeDistribution], OutcomeDistribution],
) -> SensitivityCase:
    return SensitivityCase(
        driver=driver,
        lower_label=lower_label,
        upper_label=upper_label,
        lower_fund=fund,
        lower_distribution=lower(distribution),
        upper_fund=fund,
        upper_distribution=upper(distribution),
    )


def _shift_home_run_rate(distribution: OutcomeDistribution, requested_delta: float) -> OutcomeDistribution:
    if requested_delta >= 0:
        delta = min(requested_delta, distribution.write_off)
    else:
        delta = max(requested_delta, -distribution.home_run)
    return replace(
        distribution,
        write_off=distribution.write_off - delta,
        home_run=distribution.home_run + delta,
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)
