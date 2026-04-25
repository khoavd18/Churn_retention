# EDA Summary: Customer Churn

Dataset: `data/processed/model_dataset.csv`  
Rows: 7,032 customers  
Overall churn rate: 26.6% (1,869 churned customers)

This summary is descriptive EDA only. It does not include hypothesis testing, modeling, or causal claims.

## Business Insights

1. **Overall churn is a meaningful business problem.**  
   26.6% of customers churned. This baseline helps identify segments where churn is materially above average.

2. **Month-to-month contracts are the clearest contract risk segment.**  
   Month-to-month customers churn at 42.7%, compared with 11.3% for one-year contracts and 2.8% for two-year contracts. The segment is also large: 3,875 customers and 1,655 churned customers.

3. **The `0-11 months` tenure group is the most vulnerable lifecycle segment.**  
   Customers in the `0-11 months` tenure group churn at 48.5%, compared with 9.6% for customers in the `48+ months` group. This points to onboarding and retention work during the exact `0-11 months` bucket used in the dataset.

4. **Churned customers have higher monthly charges.**  
   Churned customers have average monthly charges of $74.44 versus $61.31 for retained customers. This is an association, not evidence that higher charges cause churn; the pattern may be confounded by plan mix, contract type, or internet-service composition. Follow-up should use segmented analysis and later modeling to see whether the relationship remains after accounting for those factors.

5. **Electronic check is the highest-risk payment method.**  
   Electronic check customers churn at 45.3%, compared with 15.3% for credit card autopay customers. This is a strong descriptive signal for billing journey review and retention targeting.

6. **Fiber optic customers show elevated churn.**  
   Fiber optic customers churn at 41.9%, versus 19.0% for DSL and 7.4% for customers with no internet service. This segment is large, with 3,096 customers and 1,297 churned customers.

7. **Among internet customers, online security and tech support are associated with lower churn.**  
   Internet customers without online security churn at 41.8% versus 14.6% with online security. Internet customers without tech support churn at 41.6% versus 15.2% with tech support. This is association only, not causality; these flags may proxy for bundle maturity, customer engagement, or customer type. Streaming TV and streaming movies show smaller differences after filtering to internet customers.

## Recommendation Notes

- For retention strategy, prioritize customers in the `0-11 months` tenure group who are also month-to-month, especially those using electronic check or fiber optic service.
- Review the billing experience for electronic check customers and consider autopay migration campaigns.
- Review fiber optic customer experience together with monthly charges, support availability, and perceived value.
- Treat online security and tech support as useful service-engagement signals that may proxy for bundle maturity, engagement, or customer type; they are not proven causes of lower churn.
- For later modeling, exclude `customer_id`; keep it only for traceability.
- Drop or ignore `is_total_charges_missing` later because Step 5 identified it as constant.
- Review overlapping raw and derived feature pairs before modeling, such as `contract` with `is_month_to_month` and service categories with `has_*` flags.

## Figures Generated

- `reports/figures/churn_distribution.png`
- `reports/figures/churn_rate_by_contract.png`
- `reports/figures/churn_rate_by_tenure_group.png`
- `reports/figures/monthly_charges_distribution_by_churn.png`
- `reports/figures/churn_rate_by_payment_method.png`
- `reports/figures/churn_rate_by_internet_service.png`
- `reports/figures/churn_rate_by_service_flags.png`
