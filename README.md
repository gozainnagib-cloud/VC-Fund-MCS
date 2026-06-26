# Venture Fund Monte Carlo Simulator

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A7EA4)](https://docs.pytest.org/)

An institutional-style VC analytics dashboard that models how portfolio construction, ownership, dilution, reserves, and power-law outcomes shape venture fund returns.

**Live app:** [vc-fund-mcs.streamlit.app](https://vc-fund-mcs.streamlit.app)  
**Project memo:** [docs/project_memo.md](docs/project_memo.md)  
**Status:** Public portfolio project using synthetic assumptions only. No API keys, paid datasets, market-data feeds, private VC databases, or external authentication are required.

## Core Question

How do fund construction decisions change the probability that a venture fund returns capital, clears a 3x target, or becomes dependent on one breakout company?

## Why This Project Exists

Venture returns are dominated by rare outcomes, so averages alone can be misleading. This simulator turns VC portfolio construction into an auditable probabilistic model: users can change ownership, dilution, reserve policy, portfolio size, follow-on quality, and outlier rates to see how fund-level TVPI, downside risk, and winner dependency move.

## What A Recruiter Should Notice

- Quantitative modeling: Monte Carlo simulation, probability thresholds, percentile analysis, severe-loss probability, and sensitivity analysis.
- Finance reasoning: VC power-law outcomes, ownership dilution, follow-on reserves, fund-level TVPI, outlier dependency, and terminal annualized return proxy.
- Product sense: an interactive dashboard that explains the model, not just a notebook or static chart.
- Engineering quality: typed dataclasses, deterministic seeded simulations, tested core logic, scenario presets, and no external services.

## Key Features

- Scenario presets: Conservative, Base Case, Aggressive, and Power Law.
- Configurable fund assumptions: fund size, fees, portfolio size, entry ownership, dilution, reserves, follow-on selection quality, and terminal holding period.
- Configurable outcome distribution: write-off, return-capital, small-win, 10x breakout, 50x home run, and implied 100x fund-maker rates.
- Executive KPI strip: median TVPI, mean TVPI, implied annualized return, 1x/3x/5x probabilities, severe-loss probability, and average outlier count.
- Model-boundary and confidence panel: states what the simulator does not include and shows the mean TVPI standard error / approximate confidence interval.
- Return distribution: histogram with 1x, 3x, and 5x threshold annotations.
- Sensitivity analysis: tornado-style view showing which assumptions move the probability of a 3x fund.
- Power-law underwriting table: converts synthetic outcome probabilities into expected company counts per fund.
- Strategy comparison: compares venture portfolio archetypes.
- Outlier dependency analysis: shows how much fund value is driven by the top company and top three companies.
- Investment committee notes: concise interpretation of what the simulation is modeling and what it does not claim.

## Model Definition

Each simulated fund draws company outcomes from a synthetic power-law distribution:

| Outcome tier | Base multiple |
|---|---:|
| Write-off | 0x |
| Return capital | 1x |
| Small win | 3x |
| Breakout | 10x |
| Home run | 50x |
| Fund-maker | 100x |

Fund-level proceeds are adjusted for:

- deployable capital after management fees
- initial check size across the portfolio
- target entry ownership
- dilution across future rounds
- reserve allocation into simulated outliers
- follow-on selection quality

The dashboard reports terminal TVPI as gross simulated distributions divided by committed fund size. The annualized return is not a real cash-flow IRR. It is clearly labeled as a terminal TVPI proxy.

The model still does not include carry, recycling, capital-call timing, NAV marks, exit-year dispersion, taxes, or real company-level data.

## Metrics

- **TVPI:** Terminal fund multiple, calculated as simulated gross distributions divided by committed fund size.
- **Mean TVPI:** Average terminal fund multiple across simulated funds. This can be pulled upward by rare outliers.
- **Median TVPI:** Middle simulated fund outcome. Often more informative than mean in power-law settings.
- **P >= 1x / 3x / 5x:** Probability that the simulated fund clears those terminal TVPI thresholds.
- **Severe loss probability:** Probability that terminal TVPI is below 0.5x.
- **Top-company dependency:** Median share of distributions contributed by the top company.
- **Implied annualized return:** Terminal TVPI converted into an annualized return over the selected holding period. This is not a real cash-flow IRR. It is a terminal TVPI proxy.
- **Mean standard error:** Sampling error estimate for mean TVPI across simulation paths.

## Run Locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Run Tests

```bash
.venv/bin/python -m pytest
```

Current tests cover:

- outcome probability validation
- deterministic seeded simulations
- return threshold and concentration metrics
- terminal annualized return calculation
- invalid holding-period validation
- scenario presets
- sensitivity-analysis ranking
- default VC strategy presets
- ranked strategy comparison

## Project Structure

```text
app.py                    Streamlit dashboard
vc_fund_sim/engine.py     Core Monte Carlo simulation model
vc_fund_sim/presets.py    Scenario presets for dashboard defaults
vc_fund_sim/sensitivity.py Sensitivity-analysis engine
vc_fund_sim/strategies.py Strategy archetype comparison
tests/                    Unit tests for simulation, presets, sensitivity, and strategy logic
docs/project_memo.md      Finance memo explaining the model and caveats
```

## What This Is Not

This is not a real fund model, cash-flow waterfall, or investment recommendation engine. It does not claim to predict startup outcomes. The goal is to demonstrate quantitative thinking, VC portfolio intuition, and product-quality communication in a clean public project.

## Caveats

This is an educational and portfolio model. It is designed to demonstrate probabilistic VC portfolio thinking, not to forecast real startup outcomes or recommend investments. Real venture performance depends on sourcing, selection, entry valuation, follow-on rights, pro-rata access, fund timing, recycling, fees, carry, LP agreements, market cycles, exit timing, capital-call timing, NAV marks, and exit-year dispersion.
