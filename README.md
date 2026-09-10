# Airbnb-Investment-Intelligence-App-Project-
We are working as part of a data &amp; AI consulting team supporting a property investor who wants to make a more informed Airbnb investment decision. We will design, build, deploy, and present a data-driven Airbnb Investment Intelligence App that helps a user explore where, what, and how to invest in short term rental property across UK cities. 

## Key Features
- City Selector
- Investment Recommendation
- Transparent Scoring Model
- Short-

## Exact Investment Scoring Formula
Investment Score (0-100) ranking areas, property types, and listings is calcullated dynamically using a transparent 5-factor weighting model:

1) Gross Revenue Proxy (30%): Estimated annual revenue dervied from nightly prices multiplied by unavailiable calendar days
2) Occupancy Stability (25%): Minimum availiability consistency across a 12-month snapshot window
3) Guest Sentiment & Rating (20%): Weighted score combining average review ratings and total review volumes
Short-Term vs Long-Term Yield Spread (15%): Outperformance margin against local baseline benchmarks
Regulatory & Planning Risk (10%): Penalty applied to areas with strict short-term let enforcement or caps

## Investor Personas
The platform dynamically adapts its metric framing, weighting logic and recommendations based on three distinct user profiles:

- Revenue Maximiser: Prioritises top-line gross yield potential and highest Average Daily Rate (ADR)
- Risk-Averse Investor: Focuses heavily on consistent occupancy proxises, high review volumes and strict regulatory compliance
- Balanced Investor: Applies an equalised weighting across occupancy stability, nightly yield, guest sentiment and regulatory risks

## Data Sources
- Primary Dataset: Inside Airbnb
