from vc_fund_sim.presets import scenario_presets


def test_scenario_presets_cover_recruiter_friendly_cases():
    presets = scenario_presets()

    assert {"Conservative", "Base Case", "Aggressive", "Power Law"}.issubset(presets)


def test_scenario_presets_have_valid_fund_and_distribution_assumptions():
    for preset in scenario_presets().values():
        assert preset.fund.fund_size > 0
        assert preset.fund.portfolio_size > 0
        assert abs(sum(preset.distribution.probabilities) - 1.0) < 0.000001
