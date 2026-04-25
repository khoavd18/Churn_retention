# Churn Retention Intelligence

Customer churn analytics project built as an end-to-end company-style data science workflow. The project turns subscription, service, and billing data into a retention targeting recommendation that a Growth, CRM, or Customer Success team could review before launching a campaign.

## Project Overview

The project predicts which customers are most likely to churn, identifies the main churn drivers, and estimates the expected business value of targeting high-risk customers. It includes data processing, SQL feature engineering, EDA, hypothesis testing, baseline and stronger model comparison, threshold tuning, top-k targeting, explainability, and a retention value simulation.

Final recommendation:

- Primary: `GradientBoostingClassifier` with a churn-probability threshold of `0.40`
- Secondary: top 10% highest-risk customers from the same Gradient Boosting model

## Business Problem

The company has a limited retention budget and needs to prioritize outreach. A good churn model should do more than classify customers: it should rank risk, show which customer attributes drive churn, and translate model choices into campaign trade-offs such as contact volume, captured churners, and expected net value.

Key stakeholder questions:

- Which customers are most likely to churn?
- Which segments have the highest observed churn?
- Which model operating point creates the strongest expected retention value?

## Dataset

The project uses processed customer data split into four business tables and then joined into a model-ready dataset.

| Asset | Description |
| --- | --- |
| `customers.csv` | Demographics and tenure |
| `subscriptions.csv` | Contract, billing preference, and churn target |
| `services.csv` | Phone, internet, support, security, and streaming services |
| `billing.csv` | Monthly charges, total charges, and missing-charge flag |
| `model_dataset.csv` | Final joined and engineered modeling table |

Modeling dataset:

- Rows: 7,032 customers
- Columns: 34 before model feature exclusion
- Target: `churn`
- Churn rate: 26.6% (`1,869` churned customers)
- Data quality: no missing values in the final model dataset; `customer_id` is excluded from modeling; `is_total_charges_missing` is constant after rows with missing total charges are removed

## Workflow

```bash
pip install -r requirements.txt

python src/data/load_data.py
python src/data/build_features.py
python src/data/validate_model_dataset.py

python src/models/train_baseline.py
python src/models/train_compare_models.py
python src/models/threshold_tuning.py
python src/models/explain_model.py

python src/business/retention_simulator.py
```

Main artifacts:

- SQL feature engineering: `sql/`
- EDA and hypothesis testing notebooks: `notebooks/`
- Model and business metrics: `outputs/metrics/`
- Business summaries: `reports/`
- Figures: `reports/figures/`

## Key Findings

- Overall churn is 26.6%, making retention a meaningful business problem.
- Month-to-month customers churn at 42.7%, compared with 11.3% for one-year contracts and 2.8% for two-year contracts.
- Customers in the `0-11 months` tenure group churn at 48.5%, compared with 9.6% for customers in the `48+ months` group.
- Churned customers have higher average monthly charges: `$74.44` versus `$61.31` for retained customers.
- Electronic check customers churn at 45.3%, compared with 15.3% for credit card autopay customers.
- Fiber optic customers churn at 41.9%, compared with 19.0% for DSL and 7.4% for customers with no internet service.
- Online security and tech support are associated with lower churn among internet customers.

Hypothesis tests support the strongest EDA patterns:

- Contract type and churn: chi-square p-value `7.326e-257`
- Monthly charges by churn group: Mann-Whitney U p-value `8.467e-54`
- Tech support and churn: chi-square p-value `3.233e-43`
- Online security and churn: chi-square p-value `1.374e-46`

These findings are associations, not causal proof.

## Modeling Results

All models used the same stratified train/test split (`test_size=0.20`, `random_state=42`) and the same preprocessing pipeline. The test set contains 1,407 customers, including 374 observed churners.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| GradientBoostingClassifier | 0.796 | 0.642 | 0.527 | 0.579 | 0.839 |
| LogisticRegression | 0.794 | 0.633 | 0.535 | 0.580 | 0.835 |
| RandomForestClassifier | 0.784 | 0.618 | 0.489 | 0.546 | 0.813 |

Gradient Boosting had the strongest ROC-AUC, making it the best risk-ranking model for threshold and top-k campaign design.

## Final Recommendation

Use `GradientBoostingClassifier` at threshold `0.40` as the primary operating setup.

| Scenario | Customers Contacted | Churners Captured | Precision | Recall | Expected Net Value |
| --- | ---: | ---: | ---: | ---: | ---: |
| Threshold 0.40 | 419 | 252 | 0.601 | 0.674 | `$5,465` |
| Top 10% targeting | 141 | 106 | 0.752 | 0.283 | `$2,475` |

The threshold strategy has higher expected net value under the current assumptions: `$5` outreach cost per customer, `15%` save success rate among observed churners contacted, and `$200` retained value per recovered customer.

Use the top 10% strategy when the retention team needs a smaller, fixed-capacity list. It contacts fewer customers and has higher precision, but it captures fewer total churners and produces lower expected net value.

## Explainability

Permutation importance on the held-out test set shows the Gradient Boosting model relies most on:

1. `tenure`
2. `is_month_to_month`
3. `contract`
4. `internet_service`
5. `monthly_charges`
6. `total_charges`
7. `online_security`
8. `tech_support`
9. `paperless_billing`
10. `senior_citizen`

The model's strongest signals align with the EDA and hypothesis tests: customer lifecycle stage, contract commitment, internet-service context, and billing level are the main risk-ranking drivers.

## Limitations

- The dataset is observational, so findings are not causal.
- Business value is simulated from held-out model results, not measured from a live campaign.
- The save rate, outreach cost, and retained value assumptions should be validated with a controlled test.
- Models were compared on one stratified split without hyperparameter tuning.
- Some raw and engineered features overlap, such as `contract` and `is_month_to_month`; future iterations should simplify the feature set.
- The model does not include temporal validation, campaign history, customer lifetime value, or intervention-response data.

## Reports

- Business summary: `reports/executive_summary.md`
- Full case study: `reports/final_report.md`
- EDA summary: `reports/eda_summary.md`
- Hypothesis testing summary: `reports/statistics_summary.md`
- Explainability summary: `reports/explainability_summary.md`
- Business recommendation: `reports/business_recommendation.md`
