from vc_fund_sim.engine import FundAssumptions, OutcomeDistribution
from vc_fund_sim.sensitivity import run_sensitivity_analysis


def test_sensitivity_analysis_returns_ranked_core_vc_drivers():
    results = run_sensitivity_analysis(
        fund=FundAssumptions(fund_size=50_000_000, portfolio_size=25),
        distribution=OutcomeDistribution.seed_stage_default(),
        simulation_count=120,
        seed=22,
    )

    drivers = {result.driver for result in results}

    assert {
        "Entry ownership",
        "Dilution",
        "Reserve ratio",
        "Portfolio size",
        "Home-run probability",
        "Follow-on selection quality",
    }.issubset(drivers)
    assert results == sorted(results, key=lambda result: result.max_abs_delta_3x, reverse=True)


def test_sensitivity_result_keeps_base_case_constant_across_drivers():
    results = run_sensitivity_analysis(
        fund=FundAssumptions(fund_size=25_000_000, portfolio_size=20),
        distribution=OutcomeDistribution.seed_stage_default(),
        simulation_count=100,
        seed=7,
    )

    base_probabilities = {result.base_probability_3x for result in results}
    base_medians = {result.base_median_tvpi for result in results}

    assert len(base_probabilities) == 1
    assert len(base_medians) == 1


def test_sensitivity_bounds_keep_perturbed_assumptions_valid():
    results = run_sensitivity_analysis(
        fund=FundAssumptions(
            fund_size=10_000_000,
            portfolio_size=5,
            target_ownership=0.01,
            reserve_ratio=0.0,
            follow_on_success_quality=1.0,
        ),
        distribution=OutcomeDistribution.seed_stage_default(),
        simulation_count=80,
        seed=9,
    )

    assert len(results) >= 6
    assert all(0 <= result.lower_probability_3x <= 1 for result in results)
    assert all(0 <= result.upper_probability_3x <= 1 for result in results)
