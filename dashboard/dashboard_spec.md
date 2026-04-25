# Churn Analysis Dashboard Specification

## Dashboard Objective

Build a business-facing churn analysis dashboard that helps Growth, CRM, Customer Success, and Analytics teams understand where churn is concentrated, evaluate model-driven targeting options, and choose a retention campaign setup.

The dashboard should support both descriptive analytics and action planning:

- Monitor overall churn and high-risk customer segments.
- Explain the main churn drivers in business language.
- Compare model performance and operating thresholds.
- Estimate campaign value under different targeting strategies.
- Support a controlled retention pilot using the recommended setup.

## Target Users

| User group | Primary need |
| --- | --- |
| Growth / CRM managers | Choose which customer groups to target and estimate campaign value. |
| Customer Success leaders | Understand which lifecycle and service segments need intervention. |
| Data Analysts | Explore churn patterns, segment risk, and campaign performance trade-offs. |
| Data Scientists | Communicate model performance, threshold decisions, and feature drivers. |
| Executives / stakeholders | Review the business case and final recommended operating setup. |

## Data Inputs

Recommended source tables or extracts:

- `data/processed/model_dataset.csv`
- `outputs/predictions/model_comparison_predictions.csv`
- `outputs/metrics/model_comparison.csv`
- `outputs/metrics/threshold_comparison.csv`
- `outputs/metrics/topk_comparison.csv`
- `outputs/metrics/feature_importance.csv`
- `outputs/metrics/retention_simulation.csv`

## Global Design Rules

- Use consistent churn color logic:
  - Churn / high risk: coral or red
  - Retained / low risk: teal or blue
  - Recommended setup: navy
  - Secondary setup: gold or muted amber
- Format churn, precision, recall, and capture rates as percentages.
- Format charges, retained value, campaign cost, and net value as dollars.
- Keep chart titles insight-oriented.
- Use tooltips to show customer count, churners, churn rate, and business value.
- Avoid excessive slicers on the executive page; use more detailed filters on diagnostic pages.

## Page Structure

### Page 1: Executive Overview

#### Objective

Give stakeholders a one-page view of churn severity, the recommended retention setup, and expected business value.

#### KPI Cards

- Total customers
- Observed churners
- Overall churn rate
- Recommended model
- Recommended threshold
- Customers targeted by recommended setup
- Churners captured by recommended setup
- Expected net value

#### Filters

- Contract
- Tenure group
- Internet service
- Payment method

#### Charts

| Chart | Purpose |
| --- | --- |
| Overall churn rate stacked bar or KPI gauge | Show the size of the churn problem. |
| Churn rate by contract | Show the strongest high-level risk segment. |
| Churn rate by tenure group | Show lifecycle risk concentration. |
| Expected net value by setup | Compare primary and secondary campaign options. |
| Customers targeted vs churners captured | Show the trade-off between reach and precision. |

#### Interaction Design

- Selecting a contract or tenure group cross-filters the page.
- Hovering over segment bars shows customers, churners, and churn rate.
- Clicking the recommended setup highlights its customer reach and expected value.

#### Business Questions Answered

- How large is the churn problem?
- What is the recommended operating setup?
- How many customers would the campaign contact?
- How much expected net value does the setup create?
- Which broad segments should leadership pay attention to first?

### Page 2: Segment Diagnostics

#### Objective

Help analysts and business teams identify where churn is concentrated across customer lifecycle, billing, and service attributes.

#### KPI Cards

- Selected segment customers
- Selected segment churners
- Selected segment churn rate
- Churn rate lift vs overall
- Average monthly charges
- Average total charges

#### Filters

- Churn status
- Contract
- Tenure group
- Payment method
- Internet service
- Online security
- Tech support
- Monthly charge band
- Senior citizen
- Paperless billing

#### Charts

| Chart | Purpose |
| --- | --- |
| Churn rate by contract | Compare contract risk. |
| Churn rate by tenure group | Identify lifecycle windows for intervention. |
| Churn rate by payment method | Identify billing-related risk patterns. |
| Churn rate by internet service | Compare service-context risk. |
| Churn rate by online security | Show service engagement association. |
| Churn rate by tech support | Show support engagement association. |
| Monthly charges distribution by churn | Compare billing level by churn outcome. |
| Total charges distribution by churn | Show early churn and lifetime-value context. |
| Contract x tenure churn-rate heatmap | Find the highest-risk combined segments. |

#### Interaction Design

- Heatmap selections cross-filter all segment charts.
- Bar chart selections update KPI cards and distribution charts.
- Tooltips show customer count, churners, churn rate, average monthly charges, and average total charges.
- Include a reset-filter button or bookmark.

#### Business Questions Answered

- Which customer segments have the highest churn rates?
- Are newer customers more vulnerable than tenured customers?
- Which contract types are most associated with churn?
- Does billing method or monthly charge level help explain churn concentration?
- Which service engagement signals are associated with lower churn?

### Page 3: Model Performance And Explainability

#### Objective

Explain whether the model is strong enough for targeting and what signals it uses to rank churn risk.

#### KPI Cards

- Best model
- ROC-AUC
- Precision at selected threshold
- Recall at selected threshold
- F1 at selected threshold
- Predicted positive rate
- True positives
- False positives
- False negatives

#### Filters

- Model
- Threshold
- Top-k percentage

#### Charts

| Chart | Purpose |
| --- | --- |
| ROC curve | Compare model ranking performance across thresholds. |
| Precision-recall curve | Show performance in churn-targeting terms. |
| Model comparison table or bar chart | Compare accuracy, precision, recall, F1, and ROC-AUC. |
| Confusion matrix heatmap | Explain model decisions at the selected threshold. |
| Threshold comparison chart | Show precision, recall, and F1 trade-offs. |
| Top-k capture chart | Show churners captured as campaign capacity changes. |
| Feature importance bar chart | Explain the strongest model drivers. |

#### Interaction Design

- Selecting a model updates ROC, PR, threshold, top-k, and feature views.
- Threshold selection updates KPI cards and confusion matrix.
- Hovering over feature importance bars provides business-friendly feature descriptions.
- Use parameter controls for threshold and top-k where supported.

#### Business Questions Answered

- Which model ranks churn risk best?
- How does the recommended model perform on the held-out test set?
- What trade-off do we make when changing the threshold?
- How many churners are captured at different campaign sizes?
- Which customer signals does the model rely on most?

### Page 4: Campaign Planner

#### Objective

Help business users compare targeting setups and understand expected campaign economics.

#### KPI Cards

- Selected operating setup
- Customers targeted
- Churners captured
- Precision
- Recall
- Campaign cost
- Expected recovered customers
- Expected retained value
- Expected net value

#### Filters And Parameters

- Operating setup
- Model
- Threshold
- Top-k percentage
- Outreach cost per customer
- Save success rate
- Retained value per recovered customer
- Campaign capacity

#### Charts

| Chart | Purpose |
| --- | --- |
| Recommended operating setup comparison | Compare threshold targeting and top-k targeting. |
| Expected net value by setup | Identify the most valuable campaign option. |
| Campaign cost vs expected retained value | Show economics before netting cost. |
| Customers targeted vs churners captured | Show reach and efficiency trade-offs. |
| Precision@k / recall@k summary | Plan fixed-capacity campaign lists. |
| Scenario comparison figure | Compare primary and secondary business cases side by side. |

#### Interaction Design

- What-if parameters recalculate campaign cost, expected retained value, and expected net value.
- Selecting an operating setup updates KPI cards and scenario charts.
- Top-k control updates selected customer count, churners captured, precision@k, and recall@k.
- Conditional formatting highlights the highest expected net value setup.

#### Business Questions Answered

- Which targeting setup creates the highest expected net value?
- What happens if campaign capacity is limited?
- How sensitive is the recommendation to outreach cost or save rate?
- How many customers should the team contact?
- Is the broader threshold campaign worth the extra cost?

### Page 5: Customer Targeting List

#### Objective

Provide an operational list for campaign planning and customer review.

#### KPI Cards

- Customers in current target list
- Average churn probability
- Expected churners captured
- Average monthly charges
- Average tenure

#### Filters

- Model
- Threshold
- Top-k percentage
- Contract
- Tenure group
- Payment method
- Internet service
- Churn probability band

#### Charts And Tables

| Visual | Purpose |
| --- | --- |
| Customer table | List customer ID, churn probability, predicted churn, contract, tenure, payment method, internet service, monthly charges, and support/security flags. |
| Churn probability histogram | Show risk-score distribution. |
| Risk band summary | Group customers into low, medium, and high-risk bands. |
| Segment mix of target list | Explain what kinds of customers enter the campaign list. |

#### Interaction Design

- Threshold or top-k controls update the target list.
- Clicking a risk band filters the customer table.
- Tooltips summarize customer context but avoid unsupported causal explanations.
- Export enabled for campaign operations if using BI governance allows it.

#### Business Questions Answered

- Which customers should be reviewed for outreach?
- What are the common characteristics of the target list?
- How does changing the threshold affect the target population?
- Are targeted customers concentrated in specific contracts, tenure groups, or payment methods?

## Recommended Dashboard Navigation

Use a left-side or top navigation structure:

1. Executive Overview
2. Segment Diagnostics
3. Model Performance
4. Campaign Planner
5. Customer Targeting List

For Power BI, use report page buttons and bookmarks for reset states. For Tableau, use dashboard navigation buttons and parameter actions for threshold or top-k controls.

## Core Measures

Suggested measure definitions:

- `Customers = COUNTD(customer_id)`
- `Churners = SUM(churn_flag)`
- `Churn Rate = Churners / Customers`
- `Retained Customers = Customers - Churners`
- `Precision = True Positives / Predicted Positives`
- `Recall = True Positives / Actual Churners`
- `Predicted Positive Rate = Predicted Positives / Test Customers`
- `Campaign Cost = Selected Customers * Outreach Cost`
- `Expected Recovered Customers = Churners Captured * Save Success Rate`
- `Expected Retained Value = Expected Recovered Customers * Retained Value Per Customer`
- `Expected Net Value = Expected Retained Value - Campaign Cost`

## Final Recommendation To Surface

The dashboard should clearly surface the current recommendation:

**Use Gradient Boosting at threshold 0.40 as the primary retention pilot setup.**

This setup contacts 419 customers in the held-out test set, captures 252 observed churners, and produces $5,465 expected net value under the current assumptions.

Use top 10% targeting as the secondary fixed-capacity option when the team needs a smaller, more selective outreach list.
