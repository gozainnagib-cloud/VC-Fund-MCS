from vc_fund_sim.strategies import compare_strategies, default_strategies


def test_default_strategies_cover_core_vc_portfolio_archetypes():
    strategies = default_strategies()

    assert {"Concentrated Seed", "Diversified Seed", "Reserve Heavy", "Series A Ownership"}.issubset(
        set(strategies)
    )


def test_strategy_comparison_returns_ranked_summaries():
    comparison = compare_strategies(simulation_count=120, seed=11)

    assert len(comparison) >= 4
    assert comparison[0].summary.mean_multiple >= comparison[-1].summary.mean_multiple
    assert all(item.strategy_name for item in comparison)
