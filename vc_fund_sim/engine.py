from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import mean, median, stdev


@dataclass(frozen=True)
class FundAssumptions:
    fund_size: float = 50_000_000
    management_fee_rate: float = 0.20
    portfolio_size: int = 30
    target_ownership: float = 0.10
    dilution_per_round: float = 0.20
    average_future_rounds: int = 2
    reserve_ratio: float = 0.35
    follow_on_success_quality: float = 0.65
    holding_period_years: int = 8

    def __post_init__(self) -> None:
        if self.fund_size <= 0:
            raise ValueError("fund_size must be positive")
        if self.portfolio_size <= 0:
            raise ValueError("portfolio_size must be positive")
        if self.holding_period_years <= 0:
            raise ValueError("holding_period_years must be positive")
        for field in [
            "management_fee_rate",
            "target_ownership",
            "dilution_per_round",
            "reserve_ratio",
            "follow_on_success_quality",
        ]:
            value = getattr(self, field)
            if value < 0 or value > 1:
                raise ValueError(f"{field} must be between 0 and 1")

    @property
    def deployable_capital(self) -> float:
        return self.fund_size * (1 - self.management_fee_rate)

    @property
    def initial_capital(self) -> float:
        return self.deployable_capital * (1 - self.reserve_ratio)

    @property
    def reserve_capital(self) -> float:
        return self.deployable_capital * self.reserve_ratio

    @property
    def initial_check_size(self) -> float:
        return self.initial_capital / self.portfolio_size

    @property
    def dilution_factor(self) -> float:
        return (1 - self.dilution_per_round) ** self.average_future_rounds

    @property
    def ownership_factor(self) -> float:
        return self.target_ownership / 0.10


@dataclass(frozen=True)
class OutcomeDistribution:
    write_off: float
    return_capital: float
    small_win: float
    breakout: float
    home_run: float
    fund_maker: float

    def __post_init__(self) -> None:
        total = sum(self.probabilities)
        if abs(total - 1.0) > 0.000001:
            raise ValueError(f"Outcome probabilities must sum to 1.0, got {total:.4f}")
        if any(value < 0 for value in self.probabilities):
            raise ValueError("Outcome probabilities cannot be negative")

    @property
    def probabilities(self) -> tuple[float, ...]:
        return (
            self.write_off,
            self.return_capital,
            self.small_win,
            self.breakout,
            self.home_run,
            self.fund_maker,
        )

    @staticmethod
    def seed_stage_default() -> OutcomeDistribution:
        return OutcomeDistribution(
            write_off=0.58,
            return_capital=0.22,
            small_win=0.12,
            breakout=0.055,
            home_run=0.02,
            fund_maker=0.005,
        )


OUTCOME_MULTIPLES = {
    "write_off": 0.0,
    "return_capital": 1.0,
    "small_win": 3.0,
    "breakout": 10.0,
    "home_run": 50.0,
    "fund_maker": 100.0,
}

OUTCOME_ORDER = tuple(OUTCOME_MULTIPLES)
OUTLIER_OUTCOMES = {"breakout", "home_run", "fund_maker"}


@dataclass(frozen=True)
class SimulationConfig:
    fund: FundAssumptions
    outcome_distribution: OutcomeDistribution
    simulation_count: int = 5_000
    seed: int = 1

    def __post_init__(self) -> None:
        if self.simulation_count <= 0:
            raise ValueError("simulation_count must be positive")


@dataclass(frozen=True)
class CompanyOutcome:
    outcome: str
    initial_return: float
    follow_on_return: float

    @property
    def total_return(self) -> float:
        return self.initial_return + self.follow_on_return


@dataclass(frozen=True)
class SimulationRun:
    fund_multiple: float
    annualized_return: float
    gross_distributions: float
    company_outcomes: tuple[CompanyOutcome, ...]
    outlier_count: int
    top_company_share: float
    top_three_share: float


@dataclass(frozen=True)
class SimulationSummary:
    mean_multiple: float
    median_multiple: float
    mean_annualized_return: float
    median_annualized_return: float
    mean_multiple_standard_error: float
    percentile_5: float
    percentile_10: float
    percentile_25: float
    percentile_75: float
    percentile_90: float
    percentile_95: float
    probability_return_1x: float
    probability_return_3x: float
    probability_return_5x: float
    loss_probability: float
    severe_loss_probability: float
    average_outlier_count: float
    top_company_dependency_median: float
    top_three_dependency_median: float


def run_simulations(config: SimulationConfig) -> list[SimulationRun]:
    rng = random.Random(config.seed)
    return [_run_single_simulation(config.fund, config.outcome_distribution, rng) for _ in range(config.simulation_count)]


def summarize_simulations(results: list[SimulationRun]) -> SimulationSummary:
    if not results:
        raise ValueError("results cannot be empty")
    multiples = sorted(run.fund_multiple for run in results)
    annualized_returns = sorted(run.annualized_return for run in results)
    top_company_shares = [run.top_company_share for run in results]
    top_three_shares = [run.top_three_share for run in results]
    outlier_counts = [run.outlier_count for run in results]

    return SimulationSummary(
        mean_multiple=round(mean(multiples), 2),
        median_multiple=round(median(multiples), 2),
        mean_annualized_return=round(mean(annualized_returns), 4),
        median_annualized_return=round(median(annualized_returns), 4),
        mean_multiple_standard_error=round(_standard_error(multiples), 4),
        percentile_5=round(_percentile(multiples, 5), 2),
        percentile_10=round(_percentile(multiples, 10), 2),
        percentile_25=round(_percentile(multiples, 25), 2),
        percentile_75=round(_percentile(multiples, 75), 2),
        percentile_90=round(_percentile(multiples, 90), 2),
        percentile_95=round(_percentile(multiples, 95), 2),
        probability_return_1x=round(_probability_at_least(multiples, 1.0), 3),
        probability_return_3x=round(_probability_at_least(multiples, 3.0), 3),
        probability_return_5x=round(_probability_at_least(multiples, 5.0), 3),
        loss_probability=round(1 - _probability_at_least(multiples, 1.0), 3),
        severe_loss_probability=round(1 - _probability_at_least(multiples, 0.5), 3),
        average_outlier_count=round(mean(outlier_counts), 2),
        top_company_dependency_median=round(median(top_company_shares), 3),
        top_three_dependency_median=round(median(top_three_shares), 3),
    )


def _run_single_simulation(
    fund: FundAssumptions,
    distribution: OutcomeDistribution,
    rng: random.Random,
) -> SimulationRun:
    outcomes = [_draw_outcome(distribution, rng) for _ in range(fund.portfolio_size)]
    outlier_count = sum(1 for outcome in outcomes if outcome in OUTLIER_OUTCOMES)
    initial_returns = [
        fund.initial_check_size * OUTCOME_MULTIPLES[outcome] * fund.dilution_factor * fund.ownership_factor
        for outcome in outcomes
    ]
    follow_on_returns = _allocate_follow_on_returns(outcomes, fund)
    company_outcomes = tuple(
        CompanyOutcome(outcome, initial, follow_on)
        for outcome, initial, follow_on in zip(outcomes, initial_returns, follow_on_returns, strict=True)
    )
    company_returns = sorted((company.total_return for company in company_outcomes), reverse=True)
    gross_distributions = sum(company_returns) + _uninvested_reserves(fund, outlier_count)
    fund_multiple = gross_distributions / fund.fund_size
    annualized_return = _terminal_annualized_return(fund_multiple, fund.holding_period_years)

    if gross_distributions > 0:
        top_company_share = company_returns[0] / gross_distributions
        top_three_share = sum(company_returns[:3]) / gross_distributions
    else:
        top_company_share = 0.0
        top_three_share = 0.0

    return SimulationRun(
        fund_multiple=round(fund_multiple, 4),
        annualized_return=round(annualized_return, 4),
        gross_distributions=round(gross_distributions, 2),
        company_outcomes=company_outcomes,
        outlier_count=outlier_count,
        top_company_share=top_company_share,
        top_three_share=top_three_share,
    )


def _allocate_follow_on_returns(outcomes: list[str], fund: FundAssumptions) -> list[float]:
    returns = [0.0 for _ in outcomes]
    winner_indexes = [index for index, outcome in enumerate(outcomes) if outcome in OUTLIER_OUTCOMES]
    if not winner_indexes or fund.reserve_capital == 0:
        return returns

    follow_on_check = fund.reserve_capital / len(winner_indexes)
    for index in winner_indexes:
        base_multiple = OUTCOME_MULTIPLES[outcomes[index]]
        returns[index] = follow_on_check * base_multiple * fund.follow_on_success_quality * fund.ownership_factor
    return returns


def _uninvested_reserves(fund: FundAssumptions, outlier_count: int) -> float:
    if outlier_count:
        return 0.0
    return fund.reserve_capital


def _draw_outcome(distribution: OutcomeDistribution, rng: random.Random) -> str:
    draw = rng.random()
    cumulative = 0.0
    for outcome, probability in zip(OUTCOME_ORDER, distribution.probabilities, strict=True):
        cumulative += probability
        if draw <= cumulative:
            return outcome
    return OUTCOME_ORDER[-1]


def _probability_at_least(values: list[float], threshold: float) -> float:
    return sum(1 for value in values if value >= threshold) / len(values)


def _standard_error(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return stdev(values) / (len(values) ** 0.5)


def _terminal_annualized_return(fund_multiple: float, holding_period_years: int) -> float:
    if fund_multiple <= 0:
        return -1.0
    return fund_multiple ** (1 / holding_period_years) - 1


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    index = (len(values) - 1) * percentile / 100
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    weight = index - lower
    return values[lower] * (1 - weight) + values[upper] * weight
