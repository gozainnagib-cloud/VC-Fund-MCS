from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from vc_fund_sim.engine import (
    OUTCOME_MULTIPLES,
    FundAssumptions,
    OutcomeDistribution,
    SimulationConfig,
    run_simulations,
    summarize_simulations,
)
from vc_fund_sim.presets import scenario_presets
from vc_fund_sim.sensitivity import run_sensitivity_analysis
from vc_fund_sim.strategies import compare_strategies


st.set_page_config(
    page_title="VC Fund Monte Carlo Simulator",
    page_icon="VC",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #08090b;
        --bg-soft: #0d1015;
        --surface: #12161d;
        --surface-strong: #171c24;
        --surface-muted: #1e242d;
        --line: #2a3039;
        --line-soft: rgba(244, 241, 234, 0.08);
        --text: #f4f1ea;
        --text-soft: #d7d1c4;
        --muted: #9aa3ad;
        --gold: #c9a35b;
        --gold-soft: rgba(201, 163, 91, 0.14);
        --emerald: #6b8f80;
        --red: #b26b5f;
        --blue-gray: #74869c;
    }

    html, body, [data-testid="stAppViewContainer"] {
        color-scheme: dark;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.025), transparent 160px),
            radial-gradient(circle at 50% -20%, rgba(201, 163, 91, 0.10), transparent 36rem),
            var(--bg);
        color: var(--text);
        font-family: "Avenir Next", "Inter", "Helvetica Neue", Arial, sans-serif;
    }

    [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    .stMarkdown, p, li, label, button, input, select, textarea {
        font-family: "Avenir Next", "Inter", "Helvetica Neue", Arial, sans-serif;
    }

    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stWidgetLabel"] *,
    [data-testid="stNumberInputField"],
    [data-baseweb] {
        font-family: "Avenir Next", "Inter", "Helvetica Neue", Arial, sans-serif;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--text);
        letter-spacing: 0;
    }

    h1 {
        max-width: 940px;
        font-weight: 600;
        font-size: clamp(2.3rem, 4.8vw, 4.75rem);
        line-height: 0.98;
        margin: 0;
    }

    h2 {
        font-size: 1.25rem;
        font-weight: 600;
    }

    h3 {
        font-size: 1rem;
        font-weight: 600;
    }

    p, li, label, span {
        color: var(--text-soft);
    }

    code, pre, [data-testid="stJson"] {
        font-family: "SF Mono", "Menlo", "Consolas", monospace;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0c10, #10141a);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text);
        font-size: 0.78rem;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding-top: 0.35rem;
    }

    [data-testid="stSidebar"] .stMetric {
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.7rem 0.8rem;
        background: rgba(255, 255, 255, 0.025);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 42px;
        padding: 0 1rem;
        background: transparent;
        border-radius: 0;
        color: var(--muted);
    }

    .stTabs [aria-selected="true"] {
        color: var(--text);
        box-shadow: inset 0 -2px 0 var(--gold);
    }

    .stSlider [data-baseweb="slider"] > div {
        color: var(--gold);
    }

    [data-testid="stRadio"] {
        margin: 0.35rem 0 1.2rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid var(--line);
    }

    [data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.35rem;
        flex-wrap: wrap;
    }

    [data-testid="stRadio"] label {
        min-height: 38px;
        padding: 0.25rem 0.55rem;
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.018);
        transition: border-color 150ms ease, background 150ms ease;
    }

    [data-testid="stRadio"] label:has(input:checked) {
        border-color: rgba(201, 163, 91, 0.70);
        background: rgba(201, 163, 91, 0.10);
    }

    .executive-header {
        display: grid;
        grid-template-columns: minmax(0, 1.18fr) minmax(320px, 0.62fr);
        gap: 2rem;
        align-items: end;
        padding: 0.55rem 0 1.65rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1rem;
    }

    .eyebrow {
        color: var(--gold);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.75rem;
    }

    .executive-subtitle {
        max-width: 780px;
        color: var(--muted);
        font-size: 1.03rem;
        line-height: 1.65;
        margin-top: 0.95rem;
    }

    .summary-panel {
        border-left: 1px solid var(--line);
        padding-left: 1.35rem;
    }

    .summary-label {
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }

    .summary-value {
        color: var(--text);
        font-size: clamp(2.4rem, 5vw, 4.4rem);
        font-weight: 600;
        line-height: 1;
        margin: 0.5rem 0 0.35rem;
        font-variant-numeric: tabular-nums;
    }

    .summary-caption {
        color: var(--text-soft);
        line-height: 1.55;
    }

    .meta-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1.15rem;
    }

    .meta-pill {
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 0.38rem 0.65rem;
        color: var(--text-soft);
        background: rgba(255, 255, 255, 0.025);
        font-size: 0.76rem;
        white-space: nowrap;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 1rem 0 1.2rem;
    }

    .kpi-card {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.015));
        padding: 0.95rem;
        min-height: 118px;
    }

    .kpi-label {
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .kpi-value {
        color: var(--text);
        font-size: clamp(1.45rem, 2.5vw, 2.25rem);
        line-height: 1.08;
        margin-top: 0.45rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }

    .kpi-note {
        color: var(--muted);
        font-size: 0.78rem;
        line-height: 1.35;
        margin-top: 0.45rem;
    }

    .section-label {
        color: var(--gold);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0.35rem 0 0.85rem;
    }

    .spec-panel, .attribution-panel {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.025);
        margin-bottom: 0.9rem;
        overflow: hidden;
    }

    .interpretation-panel {
        border: 1px solid var(--line);
        border-left: 3px solid var(--gold);
        border-radius: 6px;
        background: linear-gradient(90deg, rgba(201, 163, 91, 0.08), rgba(255, 255, 255, 0.02));
        padding: 1rem 1.1rem;
        margin: 0.2rem 0 1.15rem;
    }

    .scope-panel {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin: 0.1rem 0 1rem;
    }

    .scope-card {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.018);
        padding: 0.9rem 1rem;
    }

    .scope-card strong {
        display: block;
        color: var(--text);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }

    .scope-card span {
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.45;
    }

    .guide-panel {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0.9rem 0 1rem;
    }

    .guide-step {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.018);
        padding: 0.85rem 0.95rem;
    }

    .guide-step strong {
        display: block;
        color: var(--text);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }

    .guide-step span {
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.4;
    }

    .interpretation-title {
        color: var(--text);
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .interpretation-copy {
        color: var(--text-soft);
        font-size: 0.96rem;
        line-height: 1.55;
    }

    .spec-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 1rem;
        padding: 0.72rem 0.9rem;
        border-bottom: 1px solid var(--line-soft);
    }

    .spec-row:last-child {
        border-bottom: 0;
    }

    .spec-label {
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    .spec-value {
        color: var(--text);
        font-size: 0.98rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }

    .attribution-row {
        display: grid;
        grid-template-columns: 62px 1fr 96px 96px;
        gap: 0.8rem;
        padding: 0.62rem 0.9rem;
        border-bottom: 1px solid var(--line-soft);
        font-size: 0.84rem;
        align-items: center;
    }

    .attribution-row:last-child {
        border-bottom: 0;
    }

    .muted { color: var(--muted); }
    .gold { color: var(--gold); }
    .emerald { color: var(--emerald); }
    .risk { color: var(--red); }
    .nowrap { white-space: nowrap; }

    .stDataFrame {
        border: 1px solid var(--line);
        border-radius: 6px;
        overflow: hidden;
    }

    div[data-testid="stJson"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
    }

    @media (max-width: 980px) {
        .executive-header, .kpi-grid, .guide-panel, .scope-panel {
            grid-template-columns: 1fr;
        }

        .summary-panel {
            border-left: 0;
            padding-left: 0;
            border-top: 1px solid var(--line);
            padding-top: 1rem;
        }

        .attribution-row {
            grid-template-columns: 50px 1fr;
        }

        .attribution-row span:nth-child(3), .attribution-row span:nth-child(4) {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

INSTITUTIONAL_SEQUENCE = ["#c9a35b", "#6b8f80", "#74869c", "#b26b5f", "#d7d1c4", "#8c7b62"]


def style_chart(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.018)",
        font={"family": "Avenir Next, Inter, Helvetica Neue, Arial, sans-serif", "color": "#d7d1c4", "size": 12},
        margin={"l": 22, "r": 18, "t": 42, "b": 28},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    fig.update_xaxes(gridcolor="rgba(244,241,234,0.07)", zerolinecolor="rgba(244,241,234,0.14)")
    fig.update_yaxes(gridcolor="rgba(244,241,234,0.07)", zerolinecolor="rgba(244,241,234,0.14)")
    return fig


def fmt_money(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def mean_tvpi_confidence_interval(summary) -> tuple[float, float]:
    margin = 1.96 * summary.mean_multiple_standard_error
    return max(0.0, summary.mean_multiple - margin), summary.mean_multiple + margin


def expected_outcome_counts(fund: FundAssumptions, distribution: OutcomeDistribution) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Outcome": name.replace("_", " ").title(),
                "Probability": probability,
                "Expected companies": probability * fund.portfolio_size,
                "Base multiple": OUTCOME_MULTIPLES[name],
            }
            for name, probability in zip(OUTCOME_MULTIPLES, distribution.probabilities, strict=True)
        ]
    )


def build_distribution(default: OutcomeDistribution, preset_key: str) -> OutcomeDistribution:
    st.sidebar.header("Outcome Probabilities")
    st.sidebar.caption("The first five buckets are user-set. The 100x fund-maker bucket is the residual needed to sum to 100%.")
    write_off = st.sidebar.slider(
        "Write-off",
        0.0,
        0.9,
        default.write_off,
        0.01,
        key=f"{preset_key}_write_off",
        help="Probability an individual company returns 0x invested capital.",
    )
    return_capital = st.sidebar.slider(
        "Return capital",
        0.0,
        0.6,
        default.return_capital,
        0.01,
        key=f"{preset_key}_return_capital",
        help="Probability an individual company returns approximately 1x.",
    )
    small_win = st.sidebar.slider(
        "Small win",
        0.0,
        0.4,
        default.small_win,
        0.01,
        key=f"{preset_key}_small_win",
        help="Probability an individual company returns approximately 3x.",
    )
    breakout = st.sidebar.slider(
        "10x breakout",
        0.0,
        0.2,
        default.breakout,
        0.005,
        key=f"{preset_key}_breakout",
        help="Probability an individual company reaches the 10x outcome tier.",
    )
    home_run = st.sidebar.slider(
        "50x home run",
        0.0,
        0.1,
        default.home_run,
        0.005,
        key=f"{preset_key}_home_run",
        help="Probability an individual company reaches the 50x outcome tier.",
    )
    allocated_probability = write_off + return_capital + small_win + breakout + home_run
    fund_maker = 1.0 - allocated_probability
    st.sidebar.metric("Allocated probability", pct(allocated_probability))
    st.sidebar.metric("Implied 100x outcome", pct(max(fund_maker, 0.0)))
    if fund_maker < 0:
        st.sidebar.error(
            f"Outcome probabilities exceed 100% by {pct(abs(fund_maker))}. "
            "Lower one or more buckets so the residual 100x outcome is non-negative."
        )
        st.stop()
    if fund_maker > 0.025:
        st.sidebar.warning("The implied 100x rate is very high for an early-stage venture model. Treat outputs as an aggressive tail case.")
    try:
        return OutcomeDistribution(
            write_off=write_off,
            return_capital=return_capital,
            small_win=small_win,
            breakout=breakout,
            home_run=home_run,
            fund_maker=fund_maker,
        )
    except ValueError:
        st.sidebar.error("Probabilities are invalid. Adjust sliders so the implied 100x outcome is non-negative.")
        st.stop()


def build_fund(default: FundAssumptions, preset_key: str) -> FundAssumptions:
    st.sidebar.header("Fund Construction")
    fund_size = st.sidebar.number_input(
        "Fund size ($M)",
        5,
        500,
        int(default.fund_size / 1_000_000),
        5,
        key=f"{preset_key}_fund_size",
        help="Committed capital. TVPI is calculated against this full fund size.",
    ) * 1_000_000
    management_fee_rate = st.sidebar.slider(
        "Lifetime management fees",
        0.0,
        0.35,
        default.management_fee_rate,
        0.01,
        key=f"{preset_key}_fees",
        help="Share of committed capital assumed unavailable for investment.",
    )
    portfolio_size = st.sidebar.slider(
        "Portfolio companies",
        5,
        80,
        default.portfolio_size,
        1,
        key=f"{preset_key}_portfolio",
        help="Number of initial investments in each simulated fund.",
    )
    target_ownership = st.sidebar.slider(
        "Entry ownership",
        0.01,
        0.30,
        default.target_ownership,
        0.01,
        key=f"{preset_key}_ownership",
        help="Initial ownership target before future dilution.",
    )
    dilution_per_round = st.sidebar.slider(
        "Dilution per future round",
        0.0,
        0.40,
        default.dilution_per_round,
        0.01,
        key=f"{preset_key}_dilution",
        help="Ownership dilution applied for each modeled future financing round.",
    )
    average_future_rounds = st.sidebar.slider(
        "Average future rounds",
        0,
        5,
        default.average_future_rounds,
        1,
        key=f"{preset_key}_rounds",
        help="Number of future rounds used to estimate final ownership.",
    )
    reserve_ratio = st.sidebar.slider(
        "Reserve ratio",
        0.0,
        0.70,
        default.reserve_ratio,
        0.01,
        key=f"{preset_key}_reserve",
        help="Deployable capital held back for follow-on investments.",
    )
    follow_on_success_quality = st.sidebar.slider(
        "Follow-on selection quality",
        0.1,
        1.0,
        default.follow_on_success_quality,
        0.05,
        key=f"{preset_key}_follow_on",
        help="How efficiently reserves are allocated into eventual outliers.",
    )
    holding_period_years = st.sidebar.slider(
        "Terminal holding period",
        3,
        15,
        default.holding_period_years,
        1,
        key=f"{preset_key}_holding_period",
        help="Years used to convert terminal TVPI into an implied annualized return proxy.",
    )
    deployable_capital = fund_size * (1 - management_fee_rate)
    initial_capital = deployable_capital * (1 - reserve_ratio)
    initial_check_size = initial_capital / portfolio_size
    if reserve_ratio >= 0.60:
        st.sidebar.warning("Reserve ratio is above 60%. This can starve initial ownership unless follow-on selection is very strong.")
    if initial_check_size < 150_000:
        st.sidebar.warning("Initial check size is below $150k. That can be unrealistic for many institutional VC strategies.")
    return FundAssumptions(
        fund_size=fund_size,
        management_fee_rate=management_fee_rate,
        portfolio_size=portfolio_size,
        target_ownership=target_ownership,
        dilution_per_round=dilution_per_round,
        average_future_rounds=average_future_rounds,
        reserve_ratio=reserve_ratio,
        follow_on_success_quality=follow_on_success_quality,
        holding_period_years=holding_period_years,
    )


@st.cache_data(show_spinner=False)
def cached_runs(fund: FundAssumptions, distribution: OutcomeDistribution, simulation_count: int, seed: int):
    config = SimulationConfig(
        fund=fund,
        outcome_distribution=distribution,
        simulation_count=simulation_count,
        seed=seed,
    )
    return run_simulations(config)


@st.cache_data(show_spinner=False)
def cached_sensitivity(fund: FundAssumptions, distribution: OutcomeDistribution, simulation_count: int, seed: int):
    return run_sensitivity_analysis(
        fund=fund,
        distribution=distribution,
        simulation_count=min(simulation_count, 2_500),
        seed=seed,
    )


def runs_frame(results) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fund_multiple": run.fund_multiple,
            "annualized_return": run.annualized_return,
            "outlier_count": run.outlier_count,
            "top_company_share": run.top_company_share,
            "top_three_share": run.top_three_share,
        }
        for run in results
    )


def outcome_frame(results) -> pd.DataFrame:
    rows = []
    for run_index, run in enumerate(results):
        for outcome in run.company_outcomes:
            rows.append(
                {
                    "simulation": run_index,
                    "outcome": outcome.outcome.replace("_", " ").title(),
                    "total_return": outcome.total_return,
                }
            )
    return pd.DataFrame(rows)


def render_executive_header(summary, fund: FundAssumptions, simulation_count: int) -> None:
    st.markdown(
        f"""
        <div class="executive-header">
            <div>
                <div class="eyebrow">Institutional venture portfolio model</div>
                <h1>VC Fund Monte Carlo Simulator</h1>
                <div class="executive-subtitle">
                    Analyze how ownership, dilution, reserve policy, and power-law outcomes determine
                    whether a venture fund returns capital, clears 3x, or becomes dependent on a single company.
                </div>
                <div class="meta-strip">
                    <span class="meta-pill">No API keys</span>
                    <span class="meta-pill">Local synthetic simulation</span>
                    <span class="meta-pill">{simulation_count:,} fund paths</span>
                    <span class="meta-pill">{fund.portfolio_size} companies</span>
                    <span class="meta-pill">{pct(fund.target_ownership)} entry ownership</span>
                </div>
            </div>
            <div class="summary-panel">
                <div class="summary-label">Probability of 3x fund</div>
                <div class="summary-value">{pct(summary.probability_return_3x)}</div>
                <div class="summary-caption">
                    Median TVPI is {summary.median_multiple:.2f}x. Loss probability is {pct(summary.loss_probability)}.
                    Median terminal TVPI proxy is {pct(summary.median_annualized_return)} annualized over {fund.holding_period_years} years.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary(summary, fund: FundAssumptions) -> None:
    ci_low, ci_high = mean_tvpi_confidence_interval(summary)
    cards = [
        ("Median TVPI", f"{summary.median_multiple:.2f}x", "Typical terminal fund multiple"),
        ("Mean TVPI", f"{summary.mean_multiple:.2f}x", f"Approx. 95% CI {ci_low:.2f}x-{ci_high:.2f}x"),
        ("Ann. TVPI Proxy", pct(summary.median_annualized_return), f"Not cash-flow IRR, {fund.holding_period_years}-year terminal proxy"),
        ("P >= 1x", pct(summary.probability_return_1x), "Capital return probability"),
        ("P >= 3x", pct(summary.probability_return_3x), "Institutional venture target"),
        ("P >= 5x", pct(summary.probability_return_5x), "Exceptional fund probability"),
        ("Severe Loss", pct(summary.severe_loss_probability), "Probability of <0.5x TVPI"),
        ("Avg Outliers", f"{summary.average_outlier_count:.2f}", "10x+ companies per fund"),
    ]
    html = '<div class="kpi-grid">'
    for label, value, note in cards:
        html += (
            '<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-note">{note}</div>'
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_reading_guide() -> None:
    st.markdown(
        """
        <div class="guide-panel">
            <div class="guide-step">
                <strong>1. Read the KPI strip</strong>
                <span>Start with median TVPI, downside probability, and probability of a 3x fund.</span>
            </div>
            <div class="guide-step">
                <strong>2. Check distribution</strong>
                <span>Use the return distribution and outcome map to see downside, upside, and winner dependency.</span>
            </div>
            <div class="guide-step">
                <strong>3. Stress the thesis</strong>
                <span>Use sensitivity analysis to identify which assumptions actually drive the fund result.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_executive_interpretation(summary) -> None:
    if summary.probability_return_3x >= 0.30:
        return_profile = "a credible venture-scale return profile"
    elif summary.probability_return_3x >= 0.15:
        return_profile = "a plausible but selective venture return profile"
    else:
        return_profile = "a fragile fund-return profile"

    if summary.top_company_dependency_median >= 0.50:
        dependency_profile = "high single-winner dependency"
    elif summary.top_company_dependency_median >= 0.35:
        dependency_profile = "moderate winner concentration"
    else:
        dependency_profile = "more distributed return contribution"

    st.markdown(
        f"""
        <div class="interpretation-panel">
            <div class="interpretation-title">Executive interpretation</div>
            <div class="interpretation-copy">
                Current assumptions indicate {return_profile}: median TVPI is
                <span class="gold">{summary.median_multiple:.2f}x</span>, probability of 3x is
                <span class="gold">{pct(summary.probability_return_3x)}</span>, and loss probability is
                <span class="risk">{pct(summary.loss_probability)}</span>. The model shows
                {dependency_profile}, with the median top company contributing
                <span class="gold">{pct(summary.top_company_dependency_median)}</span> of gross distributions.
                Annualized return is a terminal TVPI proxy, not a cash-flow IRR.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_model_scope(summary, simulation_count: int) -> None:
    ci_low, ci_high = mean_tvpi_confidence_interval(summary)
    st.markdown(
        f"""
        <div class="scope-panel">
            <div class="scope-card">
                <strong>Model boundary</strong>
                <span>
                    Uses synthetic terminal outcome buckets. It does not model carry, recycling,
                    capital-call timing, NAV marks, exit-year dispersion, taxes, or real startup data.
                </span>
            </div>
            <div class="scope-card">
                <strong>Simulation confidence</strong>
                <span>
                    {simulation_count:,} paths. Mean TVPI standard error is
                    <span class="nowrap">{summary.mean_multiple_standard_error:.3f}x</span>,
                    with an approximate 95% interval of
                    <span class="nowrap">{ci_low:.2f}x-{ci_high:.2f}x</span>.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assumptions(fund: FundAssumptions, distribution: OutcomeDistribution) -> None:
    rows = [
        ("Fund size", fmt_money(fund.fund_size)),
        ("Deployable capital", fmt_money(fund.deployable_capital)),
        ("Portfolio companies", f"{fund.portfolio_size}"),
        ("Initial check size", fmt_money(fund.initial_check_size)),
        ("Reserve capital", fmt_money(fund.reserve_capital)),
        ("Entry ownership", pct(fund.target_ownership)),
        ("Estimated final ownership", pct(fund.target_ownership * fund.dilution_factor)),
        ("Dilution factor", pct(fund.dilution_factor)),
        ("Terminal holding period", f"{fund.holding_period_years} years"),
    ]
    distribution_rows = [
        ("Write-off", pct(distribution.write_off)),
        ("Return capital", pct(distribution.return_capital)),
        ("Small win", pct(distribution.small_win)),
        ("10x breakout", pct(distribution.breakout)),
        ("50x home run", pct(distribution.home_run)),
        ("100x fund-maker", pct(distribution.fund_maker)),
    ]
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section-label">Fund construction</div>', unsafe_allow_html=True)
        st.markdown(_spec_table(rows), unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section-label">Outcome distribution</div>', unsafe_allow_html=True)
        st.markdown(_spec_table(distribution_rows), unsafe_allow_html=True)
    st.caption(
        "The 100x fund-maker rate is intentionally residual: changing the first five probability buckets makes the rarest tail event explicit."
    )


def _spec_table(rows: list[tuple[str, str]]) -> str:
    html = '<div class="spec-panel">'
    for label, value in rows:
        html += (
            '<div class="spec-row">'
            f'<span class="spec-label">{label}</span>'
            f'<span class="spec-value">{value}</span>'
            "</div>"
        )
    html += "</div>"
    return html


def render_portfolio_outcome_map(results) -> None:
    df = runs_frame(results)
    sampled = df.sample(min(900, len(df)), random_state=3).copy()
    sampled["fund_path"] = sampled.index.astype(str)
    sampled["position_size"] = sampled["fund_multiple"].clip(upper=8)
    chart = px.scatter(
        sampled,
        x="top_company_share",
        y="fund_multiple",
        size="position_size",
        color="outlier_count",
        color_continuous_scale=["#313844", "#6b8f80", "#c9a35b"],
        hover_data={
            "fund_path": True,
            "fund_multiple": ":.2f",
            "top_company_share": ":.1%",
            "outlier_count": True,
            "position_size": False,
        },
        labels={
            "top_company_share": "Top-company dependency",
            "fund_multiple": "Fund multiple",
            "outlier_count": "Outliers",
        },
    )
    chart.update_traces(marker={"line": {"width": 0.4, "color": "rgba(244,241,234,0.22)"}, "opacity": 0.68})
    chart.add_hline(y=1, line_dash="dash", line_color="#6b8f80", annotation_text="1x capital returned")
    chart.add_hline(y=3, line_dash="dash", line_color="#c9a35b", annotation_text="3x venture target")
    chart.update_xaxes(tickformat=".0%")
    st.markdown('<div class="section-label">Portfolio outcome map</div>', unsafe_allow_html=True)
    st.plotly_chart(style_chart(chart, height=490), width="stretch")


def render_scenario_attribution(results) -> None:
    top_runs = sorted(results, key=lambda run: run.fund_multiple, reverse=True)[:7]
    rows = ""
    for index, run in enumerate(top_runs, start=1):
        rows += (
            '<div class="attribution-row">'
            f'<span class="muted">#{index:02d}</span>'
            f'<span>Top-decile path at <span class="gold">{run.fund_multiple:.2f}x TVPI</span></span>'
            f'<span class="emerald">{run.outlier_count} outliers</span>'
            f'<span class="muted">{pct(run.top_company_share)} top co.</span>'
            "</div>"
        )
    st.markdown(
        '<div class="attribution-panel">'
        '<div style="padding:0.8rem 0.9rem 0;"><div class="section-label">Scenario attribution</div></div>'
        f"{rows}"
        "</div>",
        unsafe_allow_html=True,
    )


def render_results(results) -> None:
    df = runs_frame(results)
    st.subheader("Terminal TVPI Distribution")
    chart = px.histogram(
        df,
        x="fund_multiple",
        nbins=60,
        labels={"fund_multiple": "Fund multiple (TVPI)"},
        color_discrete_sequence=["#6b8f80"],
    )
    chart.update_traces(marker_line_color="rgba(244,241,234,0.14)", marker_line_width=0.5, opacity=0.88)
    chart.add_vline(x=1, line_dash="dash", line_color="#6b8f80", annotation_text="1x")
    chart.add_vline(x=3, line_dash="dash", line_color="#c9a35b", annotation_text="3x")
    chart.add_vline(x=5, line_dash="dot", line_color="#74869c", annotation_text="5x")
    st.plotly_chart(style_chart(chart), width="stretch")
    st.caption(
        "TVPI is modeled as terminal gross distributions divided by committed fund size. "
        "Threshold lines show common LP-facing outcomes: capital returned, 3x target, and 5x exceptional fund."
    )

    percentile_table = (
        df[["fund_multiple", "annualized_return"]]
        .quantile([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
        .reset_index()
    )
    percentile_table.columns = ["Percentile", "Fund multiple", "Implied annualized return"]
    percentile_table["Percentile"] = percentile_table["Percentile"].map(lambda value: f"{int(value * 100)}th")
    st.dataframe(
        percentile_table,
        hide_index=True,
        width="stretch",
        column_config={
            "Fund multiple": st.column_config.NumberColumn(format="%.2fx"),
            "Implied annualized return": st.column_config.NumberColumn(format="percent"),
        },
    )


def render_power_law(results, fund: FundAssumptions, distribution: OutcomeDistribution) -> None:
    st.subheader("Power-Law Outcome Mix")
    outcomes = outcome_frame(results)
    outcome_counts = outcomes["outcome"].value_counts(normalize=True).rename_axis("Outcome").reset_index(name="Share")
    chart = px.bar(
        outcome_counts,
        x="Outcome",
        y="Share",
        text="Share",
        color="Outcome",
        color_discrete_sequence=INSTITUTIONAL_SEQUENCE,
    )
    chart.update_traces(texttemplate="%{text:.1%}", marker_line_width=0)
    chart.update_yaxes(tickformat=".0%")
    st.plotly_chart(style_chart(chart), width="stretch")
    st.caption(
        "Outcome tiers are synthetic return buckets. They are scaled by ownership, dilution, and reserve behavior rather than real company data."
    )

    st.markdown('<div class="section-label">Underwriting math by outcome tier</div>', unsafe_allow_html=True)
    multiple_table = expected_outcome_counts(fund, distribution)
    st.dataframe(
        multiple_table,
        hide_index=True,
        width="stretch",
        column_config={
            "Probability": st.column_config.NumberColumn(format="percent"),
            "Expected companies": st.column_config.NumberColumn(format="%.2f"),
            "Base multiple": st.column_config.NumberColumn(format="%.1fx"),
        },
    )
    st.caption(
        "Expected company counts translate abstract probabilities into portfolio construction terms. "
        "Base multiples are calibrated to a 10% ownership reference point, then adjusted by current ownership and dilution assumptions."
    )


def render_strategy_comparison(simulation_count: int, distribution: OutcomeDistribution) -> None:
    st.subheader("Strategy Comparison")
    comparison = compare_strategies(simulation_count=simulation_count, distribution=distribution)
    rows = [
        {
            "Strategy": item.strategy_name,
            "Mean TVPI": item.summary.mean_multiple,
            "Median TVPI": item.summary.median_multiple,
            "P(>=1x)": item.summary.probability_return_1x,
            "P(>=3x)": item.summary.probability_return_3x,
            "Top company dependency": item.summary.top_company_dependency_median,
            "Portfolio size": item.fund.portfolio_size,
            "Reserve ratio": item.fund.reserve_ratio,
        }
        for item in comparison
    ]
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
        column_config={
            "P(>=1x)": st.column_config.NumberColumn(format="percent"),
            "P(>=3x)": st.column_config.NumberColumn(format="percent"),
            "Top company dependency": st.column_config.NumberColumn(format="percent"),
        },
    )
    chart = px.scatter(
        df,
        x="Median TVPI",
        y="P(>=3x)",
        size="Portfolio size",
        color="Strategy",
        hover_data=["Mean TVPI", "Reserve ratio", "Top company dependency"],
        color_discrete_sequence=INSTITUTIONAL_SEQUENCE,
    )
    chart.update_yaxes(tickformat=".0%")
    chart.update_traces(marker={"line": {"width": 0.5, "color": "rgba(244,241,234,0.24)"}, "opacity": 0.82})
    st.plotly_chart(style_chart(chart), width="stretch")
    st.caption(
        "The comparison changes fund construction while holding the selected outcome distribution constant. "
        "This separates portfolio-design effects from startup-selection assumptions."
    )


def render_sensitivity(fund: FundAssumptions, distribution: OutcomeDistribution, simulation_count: int, seed: int) -> None:
    st.subheader("Sensitivity Analysis")
    sensitivity = cached_sensitivity(fund, distribution, simulation_count, seed)
    chart_rows = []
    table_rows = []
    for result in sensitivity:
        chart_rows.extend(
            [
                {
                    "Driver": result.driver,
                    "Case": result.lower_label,
                    "Change in P(>=3x)": result.lower_delta_3x,
                    "Change in median TVPI": result.lower_delta_tvpi,
                },
                {
                    "Driver": result.driver,
                    "Case": result.upper_label,
                    "Change in P(>=3x)": result.upper_delta_3x,
                    "Change in median TVPI": result.upper_delta_tvpi,
                },
            ]
        )
        table_rows.append(
            {
                "Driver": result.driver,
                "Lower case": result.lower_label,
                "Upper case": result.upper_label,
                "Lower P(>=3x)": result.lower_probability_3x,
                "Base P(>=3x)": result.base_probability_3x,
                "Upper P(>=3x)": result.upper_probability_3x,
                "Max change": result.max_abs_delta_3x,
                "Base median TVPI": result.base_median_tvpi,
                "Low median TVPI": result.lower_median_tvpi,
                "High median TVPI": result.upper_median_tvpi,
            }
        )

    chart_df = pd.DataFrame(chart_rows)
    chart = px.bar(
        chart_df,
        y="Driver",
        x="Change in P(>=3x)",
        color="Case",
        orientation="h",
        text="Change in P(>=3x)",
        hover_data={"Change in median TVPI": ":.2f", "Change in P(>=3x)": ":.1%"},
        color_discrete_sequence=["#b26b5f", "#6b8f80"],
        labels={"Change in P(>=3x)": "Change in probability of 3x fund"},
    )
    chart.update_traces(texttemplate="%{text:+.1%}", textposition="outside", cliponaxis=False)
    chart.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor="rgba(244,241,234,0.28)")
    chart.update_yaxes(categoryorder="array", categoryarray=[item.driver for item in reversed(sensitivity)])
    st.plotly_chart(style_chart(chart, height=470), width="stretch")

    st.caption(
        "This isolates the fund variables most likely to change the probability of clearing a 3x fund. "
        "The simulation count is capped at 2,500 for this tab to keep the interface responsive. "
        "Each case uses the same random seed so deltas are easier to compare."
    )
    st.dataframe(
        pd.DataFrame(table_rows),
        hide_index=True,
        width="stretch",
        column_config={
            "Lower P(>=3x)": st.column_config.NumberColumn(format="percent"),
            "Base P(>=3x)": st.column_config.NumberColumn(format="percent"),
            "Upper P(>=3x)": st.column_config.NumberColumn(format="percent"),
            "Max change": st.column_config.NumberColumn(format="percent"),
            "Base median TVPI": st.column_config.NumberColumn(format="%.2fx"),
            "Low median TVPI": st.column_config.NumberColumn(format="%.2fx"),
            "High median TVPI": st.column_config.NumberColumn(format="%.2fx"),
        },
    )


def render_dependency(results) -> None:
    st.subheader("Outlier Dependency")
    df = runs_frame(results)
    col1, col2 = st.columns(2)
    with col1:
        concentration = df[["top_company_share", "top_three_share"]].rename(
            columns={
                "top_company_share": "Top company",
                "top_three_share": "Top three companies",
            }
        )
        concentration = concentration.melt(var_name="Return concentration", value_name="Share of distributions")
        chart = px.box(
            concentration,
            x="Return concentration",
            y="Share of distributions",
            color="Return concentration",
            color_discrete_sequence=["#c9a35b", "#74869c"],
        )
        chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(style_chart(chart), width="stretch")
    with col2:
        chart = px.scatter(
            df.sample(min(1_000, len(df)), random_state=1),
            x="outlier_count",
            y="fund_multiple",
            opacity=0.42,
            labels={"outlier_count": "Outliers in fund", "fund_multiple": "Fund multiple"},
            color_discrete_sequence=["#6b8f80"],
        )
        chart.update_traces(marker={"line": {"width": 0.4, "color": "rgba(244,241,234,0.18)"}})
        st.plotly_chart(style_chart(chart), width="stretch")
    st.caption(
        "High top-company dependency is normal in venture, but it is a risk signal: the fund may need one company to carry most of the distributions."
    )


def render_memo() -> None:
    st.subheader("Investment Committee Notes")
    st.markdown(
        """
        ### Core Lesson
        A venture fund is not a normal diversified portfolio. The median company can fail and the fund can still work if the portfolio owns enough of a rare outlier. The underwriting problem is that outlier exposure is probabilistic, not guaranteed.

        ### What This Simulator Tests
        The model shows how fund outcomes move when the investor changes portfolio size, entry ownership, dilution, reserve policy, follow-on quality, holding period, and outlier frequency. It is designed to answer practical VC questions:

        - How many companies are needed to create credible exposure to a fund-returning outcome?
        - Does a reserve-heavy strategy improve or reduce the probability of a 3x fund?
        - How dependent is the fund on a single winner?
        - What happens when dilution is worse than expected?
        - How fragile is the fund to a lower home-run rate?

        ### Metric Definitions
        TVPI is terminal simulated gross distributions divided by committed fund size. The annualized return is not a real cash-flow IRR. It is clearly labeled as a terminal TVPI proxy.

        ### Interpretation
        A strong fund strategy is not simply the one with the highest mean return. Mean TVPI can be pulled upward by rare 100x outcomes. A better IC view compares median TVPI, severe-loss probability, probability of clearing 1x/3x/5x, sensitivity to assumptions, and top-company dependency.

        ### Caveat
        This is an educational model using simplified assumptions and synthetic return distributions. The model still does not include carry, recycling, capital-call timing, NAV marks, exit-year dispersion, real company data, or LP terms. It is not investment advice and does not predict real startup outcomes.
        """
    )


def main() -> None:
    presets = scenario_presets()
    preset_name = st.sidebar.selectbox(
        "Scenario preset",
        list(presets),
        index=list(presets).index("Base Case"),
        help="Use a preset as a starting point, then adjust individual assumptions below.",
    )
    preset = presets[preset_name]
    preset_key = preset_name.lower().replace(" ", "_")
    st.sidebar.caption(preset.description)

    fund = build_fund(preset.fund, preset_key)
    distribution = build_distribution(preset.distribution, preset_key)
    st.sidebar.header("Simulation")
    simulation_count = st.sidebar.slider("Simulation count", 500, 20_000, 5_000, 500)
    seed = st.sidebar.number_input("Random seed", 1, 999_999, 42, 1)

    results = cached_runs(fund, distribution, simulation_count, seed)
    summary = summarize_simulations(results)

    render_executive_header(summary, fund, simulation_count)
    render_summary(summary, fund)
    render_executive_interpretation(summary)
    render_model_scope(summary, simulation_count)
    render_reading_guide()
    section = st.radio(
        "Dashboard section",
        [
            "Assumptions",
            "Outcome Map",
            "Return Distribution",
            "Sensitivity",
            "Power Law",
            "Strategy Comparison",
            "Outlier Dependency",
            "IC Notes",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if section == "Assumptions":
        st.subheader("Current Assumptions")
        render_assumptions(fund, distribution)
        render_scenario_attribution(results)
    elif section == "Outcome Map":
        render_portfolio_outcome_map(results)
    elif section == "Return Distribution":
        render_results(results)
    elif section == "Sensitivity":
        render_sensitivity(fund, distribution, simulation_count, seed)
    elif section == "Power Law":
        render_power_law(results, fund, distribution)
    elif section == "Strategy Comparison":
        render_strategy_comparison(simulation_count, distribution)
    elif section == "Outlier Dependency":
        render_dependency(results)
    elif section == "IC Notes":
        render_memo()


if __name__ == "__main__":
    main()
