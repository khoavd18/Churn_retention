# Final Report: Churn Retention Intelligence

## 1. Executive Decision

The recommended retention operating setup is `GradientBoostingClassifier` with a churn-probability threshold of `0.40`.

This setup contacts 419 customers in the held-out test set, captures 252 observed churners, and produces an expected net value of `$5,465` under the current business assumptions. A secondary top 10% targeting strategy is available for smaller fixed-capacity campaigns.

## 2. Project Objective

The project was designed as a practical churn intelligence workflow for a Growth, CRM, or Customer Success team. The objective was to:

- predict which customers are most likely to churn,
- identify customer segments and features associated with churn,
- compare baseline and stronger models,
- tune operating thresholds for campaign use,
- explain the model's main risk drivers,
- estimate the expected value of retention targeting.

The target variable is `churn`, where the positive class is customer churn.

## 3. Data And Modeling Dataset

The project starts from processed customer data split into four business tables:

| Table | Business content |
| --- | --- |
| `customers` | Customer profile and tenure |
| `subscriptions` | Contract type, paperless billing, and churn |
| `services` | Phone, internet, support, security, and streaming services |
| `billing` | Monthly charges, total charges, payment method, and missing-charge flag |

SQL scripts join these tables and create model features in `sql/02_feature_engineering.sql`. The final modeling table is `data/processed/model_dataset.csv`.

Modeling dataset summary:

- Raw processed rows before modeling filter: 7,043
- Final model rows: 7,032
- Dropped rows: 11 rows with missing `total_charges`
- Final columns: 34 before excluding modeling-only fields
- Target distribution: 5,163 non-churners and 1,869 churners
- Overall churn rate: 26.6%

Data quality checks found no missing values, no duplicate `customer_id` values, no unexpected churn labels, and no negative tenure or charge values in the final model dataset. Before modeling, `customer_id` is excluded and `is_total_charges_missing` is dropped because it is constant after the missing-charge rows are removed.

## 4. Feature Engineering

The SQL feature layer creates business-readable features that can support both modeling and stakeholder discussion:

- `tenure_group`
- `is_new_customer`
- `is_month_to_month`
- `is_paperless_billing`
- service flags such as `has_online_security`, `has_tech_support`, and `has_streaming_movies`
- `monthly_charge_band`
- `is_electronic_check`
- `is_total_charges_missing`

The feature set intentionally includes both raw categorical columns and derived flags during the project review. This helps compare business interpretation with model behavior, but future production work should reduce overlap.

## 5. Exploratory Findings

The EDA identified several high-risk customer patterns:

- Overall churn rate is 26.6%.
- Month-to-month customers churn at 42.7%, compared with 11.3% for one-year contracts and 2.8% for two-year contracts.
- Customers in the `0-11 months` tenure group churn at 48.5%, compared with 9.6% for customers in the `48+ months` group.
- Churned customers have higher average monthly charges: `$74.44` versus `$61.31` for retained customers.
- Electronic check customers churn at 45.3%, compared with 15.3% for credit card autopay customers.
- Fiber optic customers churn at 41.9%, compared with 19.0% for DSL and 7.4% for customers with no internet service.
- Internet customers without online security or tech support show materially higher churn than customers with those services.

These findings point to a practical retention focus: newer month-to-month customers, especially those with higher monthly charges, electronic check payment, and fiber optic service.

## 6. Hypothesis Testing

Bivariate hypothesis tests were used to validate the strongest EDA patterns before modeling. All tests are associative, not causal.

| Business question | Test | p-value | Result |
| --- | --- | ---: | --- |
| Is churn associated with contract type? | Chi-square | `7.326e-257` | Reject H0 |
| Do monthly charges differ by churn status? | Mann-Whitney U | `8.467e-54` | Reject H0 |
| Is churn associated with tech support? | Chi-square | `3.233e-43` | Reject H0 |
| Is churn associated with online security? | Chi-square | `1.374e-46` | Reject H0 |

The tests support the project story that contract commitment, billing level, and service engagement are meaningful churn-related signals in this dataset.

## 7. Modeling Approach

The modeling process used a stratified train/test split with `test_size=0.20` and `random_state=42`.

Split details:

- Training rows: 5,625
- Test rows: 1,407
- Test-set churners: 374
- Feature count: 32 after excluding target and identifier fields
- Numeric features: 15
- Categorical features: 17

Models compared:

- Logistic Regression baseline
- Random Forest
- Gradient Boosting

The same preprocessing pipeline and held-out split were used for all models.

## 8. Model Comparison

At the default `0.50` classification threshold, model performance was:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| GradientBoostingClassifier | 0.796 | 0.642 | 0.527 | 0.579 | 0.839 |
| LogisticRegression | 0.794 | 0.633 | 0.535 | 0.580 | 0.835 |
| RandomForestClassifier | 0.784 | 0.618 | 0.489 | 0.546 | 0.813 |

Logistic Regression had slightly higher recall at the default threshold, but Gradient Boosting had the strongest ROC-AUC. Because retention campaigns depend on ranking customers by risk and choosing an operating threshold, Gradient Boosting was selected for final threshold and business-value evaluation.

## 9. Threshold And Top-K Evaluation

The project evaluated probability thresholds and top-k targeting to translate model scores into campaign lists.

Final candidate results:

| Scenario | Model | Customers selected | Churners captured | Precision | Recall |
| --- | --- | ---: | ---: | ---: | ---: |
| Threshold 0.40 | GradientBoostingClassifier | 419 | 252 | 0.601 | 0.674 |
| Top 10% targeting | GradientBoostingClassifier | 141 | 106 | 0.752 | 0.283 |

The threshold approach reaches more customers, captures more churners, and creates higher expected net value. The top 10% approach is better when campaign capacity is tight and the business needs a smaller, higher-precision list.

## 10. Explainability

Permutation importance was calculated for the Gradient Boosting model on the held-out test set using ROC-AUC scoring.

Top features:

| Rank | Feature | Interpretation |
| ---: | --- | --- |
| 1 | `tenure` | Customer lifecycle stage |
| 2 | `is_month_to_month` | Low contract commitment |
| 3 | `contract` | Contract structure |
| 4 | `internet_service` | Plan or service context |
| 5 | `monthly_charges` | Billing level |
| 6 | `total_charges` | Customer value and tenure-related billing history |
| 7 | `online_security` | Service engagement or bundle signal |
| 8 | `tech_support` | Service engagement or support signal |
| 9 | `paperless_billing` | Billing behavior |
| 10 | `senior_citizen` | Customer profile signal |

The explainability results are consistent with the EDA and hypothesis tests. The model primarily uses customer tenure, contract commitment, service context, and billing amount to rank churn risk.

These importances should not be interpreted causally. They show which features the trained model used to preserve test-set ranking performance.

## 11. Business Simulation

The final recommendation uses a simple retention economics simulation based on held-out model results.

Assumptions:

- Outreach cost per customer: `$5`
- Save success rate among observed churners contacted: `15%`
- Retained value per recovered customer: `$200`

Simulation results:

| Scenario | Selected customers | Observed churners captured | Expected recovered customers | Campaign cost | Expected retained value | Expected net value |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Threshold 0.40 | 419 | 252 | 37.80 | `$2,095` | `$7,560` | `$5,465` |
| Top 10% targeting | 141 | 106 | 15.90 | `$705` | `$3,180` | `$2,475` |

The threshold `0.40` strategy has the higher expected net value and captures more churners. The top 10% strategy is cheaper and more selective, but it creates lower expected value under the current assumptions.

## 12. Final Recommendation

Use the Gradient Boosting model at threshold `0.40` for the primary retention pilot.

Recommended operating plan:

- Score active customers with the Gradient Boosting pipeline.
- Contact customers with predicted churn probability greater than or equal to `0.40`.
- Prioritize messaging around the strongest business signals: early tenure, month-to-month contract, high monthly charges, fiber optic context, and billing/payment friction.
- Track contacted customers, offers, response, retention outcome, and incremental value.
- Run a controlled campaign or A/B test before treating simulated value as realized business impact.

If capacity is constrained, use the top 10% highest-risk customers instead of the threshold list.

## 13. Limitations

- The data is observational, so the analysis identifies associations rather than causal churn drivers.
- The business simulation is based on assumptions, not observed intervention results.
- The model was evaluated on one stratified train/test split; cross-validation and temporal validation would make the estimate more robust.
- No hyperparameter tuning was performed.
- Raw and engineered features overlap, which is useful for review but should be simplified in a production feature set.
- The model does not include customer lifetime value, prior contact history, offer eligibility, customer complaints, or recent product usage.
- The final operating threshold should be recalibrated if retention costs, offer values, or campaign capacity change.

## 14. Project Artifacts

| Artifact | Location |
| --- | --- |
| Problem statement | `docs/problem_statement.md` |
| Schema | `docs/schema.md` |
| SQL feature engineering | `sql/` |
| EDA summary | `reports/eda_summary.md` |
| Hypothesis testing summary | `reports/statistics_summary.md` |
| Model comparison | `outputs/metrics/model_comparison.csv` |
| Threshold comparison | `outputs/metrics/threshold_comparison.csv` |
| Top-k comparison | `outputs/metrics/topk_comparison.csv` |
| Explainability | `reports/explainability_summary.md` |
| Business recommendation | `reports/business_recommendation.md` |
| Retention simulation | `outputs/metrics/retention_simulation.csv` |
