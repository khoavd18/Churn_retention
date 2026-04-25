# Business Recommendation

## Assumptions

- Outreach cost per customer: $5
- Save success rate among observed churners contacted: 15%
- Retained value per recovered customer: $200
- Inputs reuse `outputs/metrics/threshold_comparison.csv` and `outputs/metrics/topk_comparison.csv`.

## Scenarios

| scenario | selected_customers | observed_churners_captured | expected_recovered_customers | campaign_cost | expected_retained_value | expected_net_value |
| --- | --- | --- | --- | --- | --- | --- |
| Threshold 0.40 | 419 | 252 | 37.80 | $2,095.00 | $7,560.00 | $5,465.00 |
| Top 10% targeting | 141 | 106 | 15.90 | $705.00 | $3,180.00 | $2,475.00 |

## Recommended Operating Setup

Primary recommendation: use `Threshold 0.40`. It has the higher expected net value ($5,465.00) and captures more observed churners (252) under the stated assumptions.

Secondary option: use `Top 10% targeting` when campaign capacity or budget is tighter. It contacts fewer customers (141) and has lower total campaign cost ($705.00), but it also produces a lower expected net value ($2,475.00).

## Business Trade-Offs

The threshold setup reaches a larger group, so it costs more to operate but recovers more expected customers and produces the stronger expected net value in this scenario.

The top 10% setup is easier to use as a fixed-capacity campaign list. It is the cleaner choice when the retention team can only contact a small number of high-risk customers.

These are scenario-based estimates from held-out model results. They are not observed causal outcomes from an experiment, so the next business validation step should be a controlled campaign or A/B test.