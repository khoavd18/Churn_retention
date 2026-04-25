# Explainability Summary

Dataset: `data/processed/model_dataset.csv`
Model explained: `GradientBoostingClassifier`
Split: same stratified train/test split as prior modeling, test_size=0.2, random_state=42
Importance method: permutation importance on the held-out test set using `roc_auc` scoring
Permutation repeats: 20

## Model Check

The model was trained on 5,625 rows and evaluated on 1,407 test rows. On this split, it achieved ROC-AUC 0.839, recall 0.527, precision 0.642, and accuracy 0.796.

The feature set contains 15 numeric features and 17 categorical features before preprocessing.

## Top 10 Features

| rank | feature | importance_mean | importance_std |
| --- | --- | --- | --- |
| 1 | tenure | 0.043204 | 0.004993 |
| 2 | is_month_to_month | 0.021754 | 0.005486 |
| 3 | contract | 0.016381 | 0.004271 |
| 4 | internet_service | 0.013899 | 0.004017 |
| 5 | monthly_charges | 0.012779 | 0.002774 |
| 6 | total_charges | 0.010527 | 0.002763 |
| 7 | online_security | 0.004445 | 0.002284 |
| 8 | tech_support | 0.004141 | 0.001740 |
| 9 | paperless_billing | 0.002113 | 0.001216 |
| 10 | senior_citizen | 0.001465 | 0.000910 |

## What The Pattern Suggests

The largest drops in model performance came from `tenure`, `is_month_to_month`, `contract`, `internet_service`, `monthly_charges`. In business terms, the model is relying most on contract commitment, customer lifecycle stage, billing level, and internet-service context to separate higher-risk customers from lower-risk customers.

The importance values fall quickly after the strongest features, which suggests that a relatively small set of customer relationship and billing signals is doing much of the useful ranking work. Features near zero should not be over-interpreted; shuffling them did not materially change test-set ROC-AUC for this trained model.

## Comparison With Earlier EDA And Statistics

This pattern is consistent with the earlier EDA finding that month-to-month customers had much higher observed churn than one-year and two-year contract customers. It also lines up with the statistical test showing contract type was strongly associated with churn.

The model also gives meaningful importance to billing and plan context, which supports the earlier EDA and Mann-Whitney test finding that churned customers tended to have higher monthly charges.

Service and engagement fields such as online security and tech support appear in the broader ranking, but their model importance is shared with related raw service columns and engineered flags. This is expected because the dataset intentionally includes overlapping raw and derived service features.

Electronic check was a strong segment in EDA, but `payment_method` and `is_electronic_check` are not in the top 10 permutation importances here. A practical read is that the model may be capturing much of that same risk through contract, tenure, internet service, and monthly charges.

## Review Notes

These are model importances, not causal evidence. A high importance means the trained model needed that feature to keep its test-set ranking performance, not that changing the feature would cause a customer to stay or churn.

`contract` and `is_month_to_month`, `paperless_billing` and `is_paperless_billing`, service categories and `has_*` flags, and `payment_method` and `is_electronic_check` are overlapping representations. They are useful for this v1 review, but future iterations should decide whether to keep raw fields, derived flags, or both.

`is_total_charges_missing` is a constant quality flag in this dataset after missing total charges were removed, so it should not be expected to add predictive value.