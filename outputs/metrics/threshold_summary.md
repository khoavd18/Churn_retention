# Threshold Tuning Summary

Dataset: `data/processed/model_dataset.csv`
Split: same stratified train/test split as prior modeling, test_size=0.2, random_state=42

This step evaluates business-friendly operating points for the two finalist models. No hyperparameter tuning was performed.

## Best Threshold Candidates

| model | threshold | precision | recall | f1 | predicted_positive_rate | true_positives | false_positives | false_negatives | true_negatives | selection_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GradientBoostingClassifier | 0.400000 | 0.601432 | 0.673797 | 0.635561 | 0.297797 | 252 | 167 | 122 | 866 | best_f1_for_model |
| LogisticRegression | 0.400000 | 0.569161 | 0.671123 | 0.615951 | 0.313433 | 251 | 190 | 123 | 843 | best_f1_for_model |
| GradientBoostingClassifier | 0.200000 | 0.469027 | 0.850267 | 0.604563 | 0.481876 | 318 | 360 | 56 | 673 | highest_recall_for_model |
| LogisticRegression | 0.200000 | 0.455172 | 0.882353 | 0.600546 | 0.515281 | 330 | 395 | 44 | 638 | highest_recall_for_model |

## Best Top-K Candidates

| model | top_k | selected_count | churners_captured | precision_at_k | recall_at_k |
| --- | --- | --- | --- | --- | --- |
| GradientBoostingClassifier | 0.050000 | 71 | 60 | 0.845070 | 0.160428 |
| GradientBoostingClassifier | 0.100000 | 141 | 106 | 0.751773 | 0.283422 |
| LogisticRegression | 0.200000 | 282 | 186 | 0.659574 | 0.497326 |

## Recommendation

For a recall-sensitive retention program, start with `GradientBoostingClassifier` at a 0.30 threshold. This captures 285 churners out of 374 on the test set, with recall 0.762, precision 0.515, and a predicted positive rate of 0.393.

If the business prefers a fixed contact list, use the top 20% list from `LogisticRegression`. It selects 282 customers and captures 186 churners, with precision@k 0.660 and recall@k 0.497.

## Trade-Off

Lowering the threshold catches more likely churners, which is useful for retention, but it also increases false positives and the number of customers the business must contact. Top-k targeting is easier to align with campaign capacity, but it may miss churners outside the selected group. The right operating point depends on retention team capacity, contact cost, offer cost, and the value of saving a customer.