# Model Comparison Summary

Dataset: `data/processed/model_dataset.csv`
Split: stratified train/test split with test_size=0.2 and random_state=42

This comparison uses the same preprocessing pipeline and the same held-out test split for all models. No hyperparameter tuning or threshold tuning was performed.

## Results

| model | train_rows | test_rows | feature_count | numeric_feature_count | categorical_feature_count | accuracy | precision | recall | f1 | roc_auc | predicted_positive_rate | true_positives | false_negatives | false_positives | true_negatives |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GradientBoostingClassifier | 5625 | 1407 | 32 | 15 | 17 | 0.796020 | 0.641694 | 0.526738 | 0.578561 | 0.838697 | 0.218195 | 197 | 177 | 110 | 923 |
| LogisticRegression | 5625 | 1407 | 32 | 15 | 17 | 0.793888 | 0.632911 | 0.534759 | 0.579710 | 0.834529 | 0.224591 | 200 | 174 | 116 | 917 |
| RandomForestClassifier | 5625 | 1407 | 32 | 15 | 17 | 0.783937 | 0.618243 | 0.489305 | 0.546269 | 0.813195 | 0.210377 | 183 | 191 | 113 | 920 |

## Current Read

For a churn-retention use case, `LogisticRegression` currently looks most promising because it has the highest recall (0.535) while maintaining a competitive ROC-AUC (0.835). Recall matters here because missed churners are customers the business never gets a chance to retain.

`GradientBoostingClassifier` has the strongest ROC-AUC (0.839), which means it ranks churn risk well across thresholds. This is useful signal for the later threshold-tuning step.

## Notes Before Threshold Tuning

- These are untuned models using the default 0.5 classification threshold.
- Raw categorical features and derived flags are both included for now; redundancy can be reduced later.
- Precision, recall, and predicted positive rate should be reviewed with business capacity and retention-contact costs.
- The next step should tune thresholds and evaluate tradeoffs, not jump straight to production decisions.