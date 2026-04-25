from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.preprocess import get_feature_columns, split_features_target
from src.models.evaluate import calculate_binary_metrics, ensure_output_dirs
from src.models.train_compare_models import (
    DATA_PATH,
    METRICS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    build_pipeline,
    dataframe_to_markdown,
    load_data,
)


REPORTS_DIR = PROJECT_ROOT / "reports"
FEATURE_IMPORTANCE_PATH = METRICS_DIR / "feature_importance.csv"
SUMMARY_PATH = REPORTS_DIR / "explainability_summary.md"

MODEL_NAME = "GradientBoostingClassifier"
SCORING = "roc_auc"
N_REPEATS = 20


def calculate_feature_importance(pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    result = permutation_importance(
        pipeline,
        X_test,
        y_test,
        scoring=SCORING,
        n_repeats=N_REPEATS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    importance_df = pd.DataFrame(
        {
            "feature": X_test.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    ).sort_values(
        ["importance_mean", "importance_std", "feature"],
        ascending=[False, True, True],
    )

    importance_df.insert(3, "rank", range(1, len(importance_df) + 1))
    return importance_df


def write_summary(
    importance_df: pd.DataFrame,
    metrics: dict[str, float],
    train_rows: int,
    test_rows: int,
    numeric_feature_count: int,
    categorical_feature_count: int,
    output_path: Path,
) -> None:
    top_10 = importance_df.head(10).copy()
    top_10["importance_mean"] = top_10["importance_mean"].round(6)
    top_10["importance_std"] = top_10["importance_std"].round(6)

    top_feature_names = top_10["feature"].tolist()
    top_feature_text = ", ".join(f"`{feature}`" for feature in top_feature_names[:5])

    lines = [
        "# Explainability Summary",
        "",
        f"Dataset: `data/processed/model_dataset.csv`",
        f"Model explained: `{MODEL_NAME}`",
        f"Split: same stratified train/test split as prior modeling, test_size={TEST_SIZE}, random_state={RANDOM_STATE}",
        f"Importance method: permutation importance on the held-out test set using `{SCORING}` scoring",
        f"Permutation repeats: {N_REPEATS}",
        "",
        "## Model Check",
        "",
        (
            f"The model was trained on {train_rows:,} rows and evaluated on {test_rows:,} test rows. "
            f"On this split, it achieved ROC-AUC {metrics['roc_auc']:.3f}, recall {metrics['recall']:.3f}, "
            f"precision {metrics['precision']:.3f}, and accuracy {metrics['accuracy']:.3f}."
        ),
        "",
        (
            f"The feature set contains {numeric_feature_count} numeric features and "
            f"{categorical_feature_count} categorical features before preprocessing."
        ),
        "",
        "## Top 10 Features",
        "",
        dataframe_to_markdown(top_10[["rank", "feature", "importance_mean", "importance_std"]]),
        "",
        "## What The Pattern Suggests",
        "",
        (
            f"The largest drops in model performance came from {top_feature_text}. "
            "In business terms, the model is relying most on contract commitment, customer lifecycle stage, "
            "billing level, and internet-service context to separate higher-risk customers "
            "from lower-risk customers."
        ),
        "",
        (
            "The importance values fall quickly after the strongest features, which suggests that a relatively "
            "small set of customer relationship and billing signals is doing much of the useful ranking work. "
            "Features near zero should not be over-interpreted; shuffling them did not materially change test-set "
            "ROC-AUC for this trained model."
        ),
        "",
        "## Comparison With Earlier EDA And Statistics",
        "",
        (
            "This pattern is consistent with the earlier EDA finding that month-to-month customers had much higher "
            "observed churn than one-year and two-year contract customers. It also lines up with the statistical "
            "test showing contract type was strongly associated with churn."
        ),
        "",
        (
            "The model also gives meaningful importance to billing and plan context, which supports the earlier "
            "EDA and Mann-Whitney test finding that churned customers tended to have higher monthly charges."
        ),
        "",
        (
            "Service and engagement fields such as online security and tech support appear in the broader ranking, "
            "but their model importance is shared with related raw service columns and engineered flags. This is "
            "expected because the dataset intentionally includes overlapping raw and derived service features."
        ),
        "",
        (
            "Electronic check was a strong segment in EDA, but `payment_method` and `is_electronic_check` are not "
            "in the top 10 permutation importances here. A practical read is that the model may be capturing much "
            "of that same risk through contract, tenure, internet service, and monthly charges."
        ),
        "",
        "## Review Notes",
        "",
        (
            "These are model importances, not causal evidence. A high importance means the trained model needed "
            "that feature to keep its test-set ranking performance, not that changing the feature would cause a "
            "customer to stay or churn."
        ),
        "",
        (
            "`contract` and `is_month_to_month`, `paperless_billing` and `is_paperless_billing`, service categories "
            "and `has_*` flags, and `payment_method` and `is_electronic_check` are overlapping representations. "
            "They are useful for this v1 review, but future iterations should decide whether to keep raw fields, "
            "derived flags, or both."
        ),
        "",
        (
            "`is_total_charges_missing` is a constant quality flag in this dataset after missing total charges were "
            "removed, so it should not be expected to add predictive value."
        ),
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_output_dirs(METRICS_DIR, REPORTS_DIR)

    df = load_data(DATA_PATH)
    X, y, customer_ids = split_features_target(df)
    numeric_features, categorical_features = get_feature_columns(X)

    X_train, X_test, y_train, y_test, _customer_ids_train, _customer_ids_test = train_test_split(
        X,
        y,
        customer_ids,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    pipeline = build_pipeline(
        X_train,
        GradientBoostingClassifier(random_state=RANDOM_STATE),
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    metrics = calculate_binary_metrics(y_test, y_pred, y_proba)

    importance_df = calculate_feature_importance(pipeline, X_test, y_test)
    importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)

    write_summary(
        importance_df=importance_df,
        metrics=metrics,
        train_rows=len(y_train),
        test_rows=len(y_test),
        numeric_feature_count=len(numeric_features),
        categorical_feature_count=len(categorical_features),
        output_path=SUMMARY_PATH,
    )

    print("Model explainability completed.")
    print(f"Feature importance: {FEATURE_IMPORTANCE_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {SUMMARY_PATH.relative_to(PROJECT_ROOT)}")
    print(importance_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
