# BI Dashboard Plan: Churn Retention Intelligence

## Dashboard Objective

Build a business-facing churn dashboard for Growth, CRM, and Customer Success teams. The dashboard should help users monitor churn concentration, inspect high-risk segments, and choose a retention campaign operating setup.

## Recommended Pages

### 1. Executive Overview

Purpose: summarize the business decision in one screen.

Core visuals:

- Overall churn rate KPI
- Customers, churners, and retained customers KPI cards
- Churn rate by contract
- Churn rate by tenure group
- Recommended operating setup card: Gradient Boosting threshold 0.40
- Expected net value by setup

Suggested filters:

- Contract
- Tenure group
- Internet service
- Payment method

### 2. Segment Diagnostics

Purpose: identify where churn is concentrated.

Core visuals:

- Churn rate by payment method
- Churn rate by internet service
- Churn rate by online security
- Churn rate by tech support
- Contract x tenure churn-rate heatmap
- Monthly charges distribution by churn

Suggested interactions:

- Click a segment to cross-filter all visuals
- Tooltip with customers, churners, churn rate, average monthly charges, and average total charges

### 3. Model Performance

Purpose: explain whether the model is strong enough for targeting.

Core visuals:

- ROC curve
- Precision-recall curve
- Confusion matrix at threshold 0.40
- Feature importance bar chart
- Threshold comparison chart

Suggested filters:

- Model
- Threshold

### 4. Campaign Planner

Purpose: compare operating setups and campaign trade-offs.

Core visuals:

- Customers targeted vs churners captured
- Precision@k and recall@k
- Expected net value by setup
- Scenario economics comparison

Recommended what-if inputs:

- Outreach cost per customer
- Save success rate
- Retained value per recovered customer
- Campaign capacity

## Implementation Notes

- Use `data/processed/model_dataset.csv` for segment and EDA pages.
- Use `outputs/predictions/model_comparison_predictions.csv` for model-score views.
- Use `outputs/metrics/threshold_comparison.csv`, `outputs/metrics/topk_comparison.csv`, and `outputs/metrics/retention_simulation.csv` for operating setup and business-value pages.
- Keep churn color logic consistent: churn risk in coral/red, retained/customer base in teal/blue, recommended setup in navy.
- Prioritize clear labels, percentage formatting, and short business-oriented titles over decorative styling.
