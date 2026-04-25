# Executive Summary: Churn Retention Intelligence

## Decision

Use the `GradientBoostingClassifier` at a churn-probability threshold of `0.40` as the primary retention targeting setup. Use top 10% targeting from the same model when the retention team needs a smaller fixed-capacity campaign list.

## Business Context

The company needs to identify customers most likely to churn and prioritize outreach under a limited retention budget. The model should help the Growth, CRM, and Customer Success teams decide who to contact, why those customers are high risk, and what value the campaign could create.

The final modeling dataset contains 7,032 customers. The observed churn rate is 26.6%, or 1,869 churned customers.

## Main Findings

- Month-to-month contracts are the clearest risk segment: 42.7% churn versus 11.3% for one-year contracts and 2.8% for two-year contracts.
- Newer customers are much more vulnerable: the `0-11 months` tenure group churns at 48.5%, compared with 9.6% for the `48+ months` group.
- Churned customers have higher average monthly charges: `$74.44` versus `$61.31` for retained customers.
- Electronic check customers churn at 45.3%, and fiber optic customers churn at 41.9%.
- Online security and tech support are associated with lower observed churn among internet customers.

## Model Performance

The best risk-ranking model is `GradientBoostingClassifier`, with ROC-AUC `0.839` on the held-out test set. At the final `0.40` threshold, it captures 252 of 374 observed churners in the test set.

| Operating setup | Customers contacted | Churners captured | Precision | Recall | Expected net value |
| --- | ---: | ---: | ---: | ---: | ---: |
| Threshold 0.40 | 419 | 252 | 0.601 | 0.674 | `$5,465` |
| Top 10% targeting | 141 | 106 | 0.752 | 0.283 | `$2,475` |

The business simulation assumes a `$5` outreach cost per customer, `15%` save success rate among observed churners contacted, and `$200` retained value per recovered customer.

## Recommendation

Launch a controlled retention pilot using the Gradient Boosting threshold `0.40` list as the primary campaign population. This setup creates the highest expected net value in the current simulation while still capturing a large share of likely churners.

Use the top 10% list if the team has strict capacity limits. It is more selective and cheaper to run, but it recovers fewer expected customers.

## Risks And Next Steps

These results are based on historical observational data and simulated retention economics. They should not be treated as proof that outreach will cause customers to stay. The next step is a controlled campaign or A/B test to measure actual save rate, offer cost, customer response, and incremental retained value.
