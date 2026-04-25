# Statistics Summary: Customer Churn Hypothesis Tests

Dataset: `data/processed/model_dataset.csv`  
Rows: 7,032 customers  
Significance level: alpha = 0.05

This report summarizes bivariate statistical tests used to validate the strongest EDA findings before modeling. These results show association only. They do not establish causality.

## Test Summary

| # | Business question | Test | p-value | Decision | Business takeaway |
|---|---|---|---:|---|---|
| 1 | Is churn significantly associated with contract type? | Chi-square test of independence | 7.326e-257 | Reject H0 | Contract type is strongly associated with churn. Month-to-month customers churn much more often than one-year and two-year customers, so contract type should be a core retention segmentation variable. |
| 2 | Do churned and non-churned customers differ significantly in monthly charges? | Mann-Whitney U test | 8.467e-54 | Reject H0 | Churned customers have higher monthly charges in this dataset, with median monthly charges of $79.65 versus $64.45 for non-churned customers. |
| 3 | Is churn significantly associated with `has_tech_support`? | Chi-square test of independence | 3.233e-43 | Reject H0 | Customers with the tech-support flag have lower observed churn than customers without it. Treat this as a useful service-engagement signal before modeling. |
| 4 | Is churn significantly associated with `has_online_security`? | Chi-square test of independence | 1.374e-46 | Reject H0 | Customers with the online-security flag have lower observed churn than customers without it. Treat this as a meaningful service or bundle signal before modeling. |

## Test Details

### 1. Contract Type And Churn

- Null hypothesis, H0: Churn and contract type are independent.
- Alternative hypothesis, H1: Churn and contract type are associated.
- Test choice: Chi-square test of independence, because both variables are categorical.
- Result: p = 7.326e-257, so reject H0 at alpha = 0.05.
- Business interpretation: Month-to-month customers have much higher observed churn than one-year and two-year contract customers. This validates contract type as one of the strongest churn-related segments from EDA.
- Association warning: This does not prove that contract type causes churn.

### 2. Monthly Charges And Churn

- Null hypothesis, H0: The distribution of `monthly_charges` is the same for churned and non-churned customers.
- Alternative hypothesis, H1: The distribution of `monthly_charges` differs between churned and non-churned customers.
- Test choice: Mann-Whitney U test, because `monthly_charges` is numeric and churn creates two independent groups. This avoids assuming normality.
- Result: p = 8.467e-54, so reject H0 at alpha = 0.05.
- Business interpretation: Churned customers have higher observed monthly charges than non-churned customers. This supports investigating pricing, plan mix, value perception, and service bundle composition before modeling.
- Association warning: This does not prove that higher monthly charges cause churn.

### 3. Tech Support And Churn

- Null hypothesis, H0: Churn and `has_tech_support` are independent.
- Alternative hypothesis, H1: Churn and `has_tech_support` are associated.
- Test choice: Chi-square test of independence, because both variables are categorical.
- Result: p = 3.233e-43, so reject H0 at alpha = 0.05.
- Business interpretation: Customers with the tech-support flag show lower observed churn than customers without it. This may indicate service engagement, bundle maturity, customer type, or support availability.
- Association warning: This does not prove that tech support prevents churn.

### 4. Online Security And Churn

- Null hypothesis, H0: Churn and `has_online_security` are independent.
- Alternative hypothesis, H1: Churn and `has_online_security` are associated.
- Test choice: Chi-square test of independence, because both variables are categorical.
- Result: p = 1.374e-46, so reject H0 at alpha = 0.05.
- Business interpretation: Customers with the online-security flag show lower observed churn than customers without it. This should be reviewed as a service-engagement or bundle signal.
- Association warning: This does not prove that online security prevents churn.

## Limitations

- These are bivariate tests and do not control for confounding variables such as tenure, internet service type, payment method, contract type, or bundle composition.
- The dataset is observational, so all findings are associations, not causal effects.
- Large samples can produce very small p-values. Business decisions should also consider effect size, segment size, operational feasibility, and customer value.
- The engineered service flags use `0` for customers who do not have the flag. Before modeling, compare these features with the raw service columns and `internet_service` to avoid hiding important category differences.
- Multiple hypothesis tests were run. The p-values here are extremely small, but broader future testing should define multiple-comparison handling in advance.
- No modeling was performed in this step.
