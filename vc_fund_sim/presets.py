from __future__ import annotations

from dataclasses import dataclass

from vc_fund_sim.engine import FundAssumptions, OutcomeDistribution


@dataclass(frozen=True)
class ScenarioPreset:
    name: str
    description: str
    fund: FundAssumptions
    distribution: OutcomeDistribution


def scenario_presets() -> dict[str, ScenarioPreset]:
    return {
        "Conservative": ScenarioPreset(
            name="Conservative",
            description="Lower outlier frequency, more dilution, and moderate portfolio breadth.",
            fund=FundAssumptions(
                fund_size=50_000_000,
                management_fee_rate=0.20,
                portfolio_size=32,
                target_ownership=0.08,
                dilution_per_round=0.24,
                average_future_rounds=3,
                reserve_ratio=0.30,
                follow_on_success_quality=0.55,
                holding_period_years=9,
            ),
            distribution=OutcomeDistribution(
                write_off=0.64,
                return_capital=0.22,
                small_win=0.09,
                breakout=0.035,
                home_run=0.012,
                fund_maker=0.003,
            ),
        ),
        "Base Case": ScenarioPreset(
            name="Base Case",
            description="Seed-style portfolio with broad loss rates and a small number of power-law outcomes.",
            fund=FundAssumptions(
                fund_size=50_000_000,
                management_fee_rate=0.20,
                portfolio_size=30,
                target_ownership=0.10,
                dilution_per_round=0.20,
                average_future_rounds=2,
                reserve_ratio=0.35,
                follow_on_success_quality=0.65,
                holding_period_years=8,
            ),
            distribution=OutcomeDistribution.seed_stage_default(),
        ),
        "Aggressive": ScenarioPreset(
            name="Aggressive",
            description="Higher ownership and follow-on quality with a smaller, more concentrated portfolio.",
            fund=FundAssumptions(
                fund_size=50_000_000,
                management_fee_rate=0.20,
                portfolio_size=22,
                target_ownership=0.13,
                dilution_per_round=0.18,
                average_future_rounds=2,
                reserve_ratio=0.42,
                follow_on_success_quality=0.75,
                holding_period_years=8,
            ),
            distribution=OutcomeDistribution(
                write_off=0.55,
                return_capital=0.22,
                small_win=0.13,
                breakout=0.065,
                home_run=0.027,
                fund_maker=0.008,
            ),
        ),
        "Power Law": ScenarioPreset(
            name="Power Law",
            description="Extreme dispersion case with more failures and slightly more tail exposure.",
            fund=FundAssumptions(
                fund_size=50_000_000,
                management_fee_rate=0.20,
                portfolio_size=40,
                target_ownership=0.09,
                dilution_per_round=0.22,
                average_future_rounds=3,
                reserve_ratio=0.38,
                follow_on_success_quality=0.70,
                holding_period_years=10,
            ),
            distribution=OutcomeDistribution(
                write_off=0.68,
                return_capital=0.17,
                small_win=0.08,
                breakout=0.045,
                home_run=0.018,
                fund_maker=0.007,
            ),
        ),
    }
