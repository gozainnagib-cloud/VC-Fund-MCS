# Project Memo: Venture Fund Monte Carlo Simulator

## Thesis

Venture capital fund performance is driven by rare outliers, not average company outcomes. A fund can absorb many failed investments and still perform well if it owns enough of one or two exceptional companies. The underwriting question is therefore probabilistic:

> Does this portfolio construction create enough ownership-weighted exposure to rare fund-returning outcomes?

## What The Simulator Tests

The simulator models thousands of possible fund outcomes using configurable assumptions:

- committed fund size
- lifetime management-fee drag
- portfolio size
- entry ownership
- dilution per future round
- expected number of future rounds
- reserve ratio
- follow-on selection quality
- terminal holding period
- company-level outcome probabilities

The model does not require API keys, market data, paid VC data, or external company datasets. It is intentionally assumption-driven so that every result can be audited and discussed.

## Fund-Level Metrics

The dashboard calculates:

- mean TVPI
- median TVPI
- 5th, 10th, 25th, 50th, 75th, 90th, and 95th percentile TVPI
- probability of clearing 1x, 3x, and 5x
- probability of severe loss below 0.5x
- implied annualized return from terminal TVPI
- mean TVPI standard error
- average outlier count
- top-company and top-three-company dependency

The implied annualized return is a terminal-value proxy:

```text
annualized return = TVPI ^ (1 / holding period years) - 1
```

The annualized return is not a real cash-flow IRR. It is clearly labeled as a terminal TVPI proxy.

The model still does not include carry, recycling, capital-call timing, NAV marks, exit-year dispersion, distribution timing, or carry waterfalls.

## Investment Lesson

Mean returns can be misleading in venture capital because rare 50x or 100x outcomes pull the average upward. A stronger analysis compares:

- median TVPI
- downside probability
- severe-loss probability
- probability of clearing LP-relevant thresholds
- how much of the fund is driven by one winner
- sensitivity to ownership, dilution, reserves, and outlier frequency

The sensitivity analysis is especially important. A model that only reports one scenario can look precise while hiding fragility. This dashboard makes the key drivers visible.

## Portfolio Strategy Implications

- Concentrated seed funds can generate strong upside, but they are fragile if they miss outliers.
- Diversified seed funds increase exposure to rare outcomes, but lower ownership can weaken fund-level impact.
- Reserve-heavy funds can work when follow-on selection is strong, but reserves reduce initial breadth.
- Series A-style funds benefit from ownership, but fewer shots reduce exposure to rare extreme outcomes.
- Severe downside risk matters because many plausible VC portfolios do not clear 1x.

## Caveats

This is a simplified educational model. Real VC outcomes depend on sourcing quality, selection skill, entry valuation, pro-rata access, insider allocation rights, market cycles, exit timing, management fees, carry, recycling, capital-call timing, NAV marks, exit-year dispersion, LP agreements, and portfolio company financing paths.

The purpose is not to forecast real funds. The purpose is to demonstrate probabilistic VC portfolio thinking, simulation discipline, and clear communication of model assumptions.
