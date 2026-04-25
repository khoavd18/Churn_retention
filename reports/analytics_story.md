# Analytics Story: Churn Retention Intelligence

## Curated Storytelling Flow

This project tells a practical churn story for Growth, CRM, and Customer Success teams:

1. **Size the problem.** Churn affects 26.6% of the modeling dataset, or 1,869 of 7,032 customers.
2. **Find the concentration.** Churn is not evenly distributed. It concentrates in low-commitment, early-tenure, high-risk billing and service segments.
3. **Validate the ranking signal.** Gradient Boosting is the strongest risk-ranking model, with ROC-AUC 0.839 on the held-out test set.
4. **Choose an operating setup.** The threshold 0.40 setup creates the strongest expected net value in the current simulation.
5. **Translate into action.** Use threshold targeting for the primary pilot and top-k targeting when campaign capacity is fixed.

## Visual Story Highlights

### 1. Churn Is Material Enough To Prioritize

![Overall churn rate](figures/eda/overall_churn_rate.png)

The dataset shows a 26.6% observed churn rate. This is high enough to justify a dedicated retention workflow rather than treating churn as a background KPI.

### 2. Contract And Tenure Define The Core Risk Pattern

![Churn rate by contract](figures/eda/churn_rate_by_contract.png)

Month-to-month customers churn at 42.7%, compared with 11.3% for one-year contracts and 2.8% for two-year contracts.

![Churn rate by tenure group](figures/eda/churn_rate_by_tenure_group.png)

Customers in the 0-11 month tenure group churn at 48.5%, while customers with 48+ months of tenure churn at 9.6%. The clearest retention window is early lifecycle intervention.

![Contract by tenure heatmap](figures/eda/churn_rate_heatmap_contract_tenure.png)

The heatmap combines both ideas: early-tenure, month-to-month customers form the highest-risk pocket. This is the strongest segment-level visual for stakeholder storytelling.

### 3. Billing And Service Context Add Useful Targeting Clues

![Churn rate by payment method](figures/eda/churn_rate_by_payment_method.png)

Electronic check customers churn at 45.3%, making payment method a useful operational signal for billing journey review or autopay migration campaigns.

![Churn rate by internet service](figures/eda/churn_rate_by_internet_service.png)

Fiber optic customers churn at 41.9%, well above DSL and no-internet customers. This pattern should be interpreted as service and plan context, not proof that fiber service causes churn.

![Churn rate by online security](figures/eda/churn_rate_by_online_security.png)

![Churn rate by tech support](figures/eda/churn_rate_by_tech_support.png)

Customers without online security or tech support show much higher observed churn. These fields are useful engagement and bundle signals, but they remain associative.

### 4. Charges Show A Retention Economics Pattern

![Monthly charges distribution by churn](figures/eda/monthly_charges_distribution_by_churn.png)

Churned customers have higher average monthly charges: $74.44 versus $61.31 for retained customers.

![Total charges distribution by churn](figures/eda/total_charges_distribution_by_churn.png)

Churned customers have lower average total charges because many churn earlier in the lifecycle. Together, these charts suggest a group that pays more per month but does not stay long enough to accumulate long-term value.

## Modeling Story

![ROC curve model comparison](figures/modeling/roc_curve_model_comparison.png)

Gradient Boosting has the strongest ROC-AUC at 0.839, making it the best model for ranking churn risk across possible thresholds.

![Precision-recall curve model comparison](figures/modeling/precision_recall_curve_model_comparison.png)

The precision-recall curve shows that high-risk score bands are materially richer in churners than the base churn rate. This matters because retention campaigns act on ranked customer lists.

![Feature importance](figures/modeling/feature_importance_top10.png)

The model relies most on tenure, month-to-month status, contract type, internet service, monthly charges, and total charges. This is consistent with the EDA story and supports a coherent analytics-to-model narrative.

![Threshold comparison](figures/modeling/threshold_comparison_gb.png)

For Gradient Boosting, threshold 0.40 is the strongest F1-oriented operating point in the evaluated threshold table. It balances recall and precision better than lower-recall default scoring or broader lower-threshold outreach.

![Confusion matrix](figures/modeling/confusion_matrix_gb_threshold_040.png)

At threshold 0.40, the model captures 252 of 374 observed churners in the held-out test set, with 167 false alerts and 866 correctly retained non-churners.

![Top-k capture comparison](figures/modeling/topk_capture_comparison.png)

Top-k targeting is useful when campaign size is fixed. The Gradient Boosting top 10% list selects 141 customers and captures 106 churners.

## Business Interpretation

![Operating setup comparison](figures/business/operating_setup_comparison.png)

The threshold 0.40 setup targets more customers, captures more churners, and recovers more expected customers than the top 10% setup.

![Expected net value by setup](figures/business/expected_net_value_by_setup.png)

Under the current assumptions, threshold 0.40 produces $5,465 expected net value, compared with $2,475 for top 10% targeting.

![Customers targeted vs churners captured](figures/business/customers_targeted_vs_churners_captured.png)

The broader threshold campaign contacts more non-churners, but the incremental churners captured make it more valuable under the stated economics.

![Precision and recall at k](figures/business/precision_recall_topk_summary.png)

Top-k lists become less precise as capacity expands, but they capture more churners. This chart is useful for campaign planning when the team has a fixed number of outreach slots.

![Scenario economics comparison](figures/business/scenario_economics_comparison.png)

The business case is not simply that threshold 0.40 creates more retained value. It also remains stronger after subtracting campaign cost.

## Final Recommended Operating Setup

Use **Gradient Boosting at threshold 0.40** as the primary retention pilot setup.

This setup contacts 419 customers in the held-out test set, captures 252 observed churners, and produces $5,465 expected net value under the current assumptions:

- Outreach cost per customer: $5
- Save success rate among observed churners contacted: 15%
- Retained value per recovered customer: $200

Use **top 10% targeting** as the secondary option when the retention team has stricter capacity limits. It is more selective and cheaper to operate, but it captures fewer churners and produces lower expected net value in the current simulation.

These results should be treated as historical and simulated, not causal. The next validation step is a controlled retention pilot or A/B test to measure actual save rate, offer cost, customer response, and incremental retained value.

## Recommended Portfolio Visuals

The strongest visuals for a README or portfolio case study are:

- `reports/figures/eda/churn_rate_heatmap_contract_tenure.png`
- `reports/figures/modeling/roc_curve_model_comparison.png`
- `reports/figures/modeling/threshold_comparison_gb.png`
- `reports/figures/business/expected_net_value_by_setup.png`
- `reports/figures/business/scenario_economics_comparison.png`
