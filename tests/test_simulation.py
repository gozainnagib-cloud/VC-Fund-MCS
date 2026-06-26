import pytest

from vc_fund_sim.engine import (
    FundAssumptions,
    OutcomeDistribution,
    SimulationConfig,
    run_simulations,
    summarize_simulations,
)


def test_outcome_distribution_probabilities_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        OutcomeDistribution(
            write_off=0.5,
            return_capital=0.2,
            small_win=0.2,
            breakout=0.2,
            home_run=0.05,
            fund_maker=0.01,
        )


def test_seeded_simulation_is_deterministic():
    config = SimulationConfig(
        fund=FundAssumptions(fund_size=50_000_000, portfolio_size=25),
        outcome_distribution=OutcomeDistribution.seed_stage_default(),
        simulation_count=100,
        seed=42,
    )

    first = run_simulations(config)
    second = run_simulations(config)

    assert [run.fund_multiple for run in first] == [run.fund_multiple for run in second]


def test_simulation_summary_reports_return_thresholds_and_outlier_dependency():
    results = run_simulations(
        SimulationConfig(
            fund=FundAssumptions(fund_size=25_000_000, portfolio_size=20),
            outcome_distribution=OutcomeDistribution.seed_stage_default(),
            simulation_count=250,
            seed=7,
        )
    )

    summary = summarize_simulations(results)

    assert 0 <= summary.probability_return_1x <= 1
    assert 0 <= summary.probability_return_3x <= 1
    assert 0 <= summary.top_company_dependency_median <= 1
    assert summary.mean_multiple > 0
    assert summary.percentile_90 >= summary.percentile_10
    assert -1 <= summary.median_annualized_return <= 10
    assert 0 <= summary.severe_loss_probability <= 1
    assert summary.percentile_95 >= summary.percentile_90


def test_higher_entry_ownership_improves_same_outcome_path():
    distribution = OutcomeDistribution.seed_stage_default()
    low_ownership = run_simulations(
        SimulationConfig(
            fund=FundAssumptions(fund_size=50_000_000, portfolio_size=25, target_ownership=0.05),
            outcome_distribution=distribution,
            simulation_count=100,
            seed=99,
        )
    )
    high_ownership = run_simulations(
        SimulationConfig(
            fund=FundAssumptions(fund_size=50_000_000, portfolio_size=25, target_ownership=0.15),
            outcome_distribution=distribution,
            simulation_count=100,
            seed=99,
        )
    )

    assert summarize_simulations(high_ownership).mean_multiple > summarize_simulations(low_ownership).mean_multiple


def test_terminal_annualized_return_uses_holding_period_assumption():
    short_hold = run_simulations(
        SimulationConfig(
            fund=FundAssumptions(
                fund_size=50_000_000,
                portfolio_size=25,
                holding_period_years=5,
            ),
            outcome_distribution=OutcomeDistribution.seed_stage_default(),
            simulation_count=100,
            seed=123,
        )
    )
    long_hold = run_simulations(
        SimulationConfig(
            fund=FundAssumptions(
                fund_size=50_000_000,
                portfolio_size=25,
                holding_period_years=10,
            ),
            outcome_distribution=OutcomeDistribution.seed_stage_default(),
            simulation_count=100,
            seed=123,
        )
    )

    assert [run.fund_multiple for run in short_hold] == [run.fund_multiple for run in long_hold]
    assert summarize_simulations(short_hold).median_annualized_return > summarize_simulations(long_hold).median_annualized_return


def test_fund_assumptions_reject_invalid_holding_period():
    with pytest.raises(ValueError, match="holding_period_years"):
        FundAssumptions(holding_period_years=0)
