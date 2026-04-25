from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.preprocess import build_preprocessor, get_feature_columns, split_features_target
from src.models.evaluate import calculate_binary_metrics, ensure_output_dirs


DATA_PATH = PROJECT_ROOT / "data" / "processed" / "model_dataset.csv"
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions"

RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Model dataset not found: {path}")

    return pd.read_csv(path)


def build_model_configs() -> dict[str, object]:
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "RandomForestClassifier": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def build_pipeline(X_train: pd.DataFrame, estimator) -> Pipeline:
    preprocessor = build_preprocessor(X_train)
    preprocessor.set_params(sparse_threshold=0)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )


def calculate_model_row(model_name: str, y_true, y_pred, y_proba) -> dict[str, object]:
    metrics = calculate_binary_metrics(y_true, y_pred, y_proba)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    return {
        "model": model_name,
        **{metric: round(float(value), 6) for metric, value in metrics.items()},
        "predicted_positive_rate": round(float(y_pred.mean()), 6),
        "true_positives": int(tp),
        "false_negatives": int(fn),
        "false_positives": int(fp),
        "true_negatives": int(tn),
    }


def build_prediction_rows(model_name: str, customer_ids, y_true, y_pred, y_proba) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "model": model_name,
            "customer_id": customer_ids.values,
            "actual_churn": y_true.values,
            "predicted_churn": y_pred,
            "churn_probability": y_proba,
        }
    )


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display_df = df.copy()
    for column in display_df.select_dtypes(include=["float"]).columns:
        display_df[column] = display_df[column].map(lambda value: f"{value:.6f}")

    headers = display_df.columns.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for _, row in display_df.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in headers) + " |")

    return "\n".join(lines)


def write_summary(comparison_df: pd.DataFrame, output_path: Path) -> None:
    best_recall = comparison_df.sort_values(["recall", "roc_auc"], ascending=False).iloc[0]
    best_auc = comparison_df.sort_values(["roc_auc", "recall"], ascending=False).iloc[0]

    lines = [
        "# Model Comparison Summary",
        "",
        f"Dataset: `data/processed/model_dataset.csv`",
        f"Split: stratified train/test split with test_size={TEST_SIZE} and random_state={RANDOM_STATE}",
        "",
        "This comparison uses the same preprocessing pipeline and the same held-out test split for all models. "
        "No hyperparameter tuning or threshold tuning was performed.",
        "",
        "## Results",
        "",
        dataframe_to_markdown(comparison_df),
        "",
        "## Current Read",
        "",
        (
            f"For a churn-retention use case, `{best_recall['model']}` currently looks most promising "
            f"because it has the highest recall ({best_recall['recall']:.3f}) while maintaining "
            f"a competitive ROC-AUC ({best_recall['roc_auc']:.3f}). Recall matters here because missed "
            "churners are customers the business never gets a chance to retain."
        ),
        "",
        (
            f"`{best_auc['model']}` has the strongest ROC-AUC ({best_auc['roc_auc']:.3f}), which means "
            "it ranks churn risk well across thresholds. This is useful signal for the later threshold-tuning step."
        ),
        "",
        "## Notes Before Threshold Tuning",
        "",
        "- These are untuned models using the default 0.5 classification threshold.",
        "- Raw categorical features and derived flags are both included for now; redundancy can be reduced later.",
        "- Precision, recall, and predicted positive rate should be reviewed with business capacity and retention-contact costs.",
        "- The next step should tune thresholds and evaluate tradeoffs, not jump straight to production decisions.",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_output_dirs(METRICS_DIR, PREDICTIONS_DIR)

    df = load_data()
    X, y, customer_ids = split_features_target(df)
    numeric_features, categorical_features = get_feature_columns(X)

    X_train, X_test, y_train, y_test, _customer_ids_train, customer_ids_test = train_test_split(
        X,
        y,
        customer_ids,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    comparison_rows = []
    prediction_frames = []

    for model_name, estimator in build_model_configs().items():
        pipeline = build_pipeline(X_train, estimator)
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        comparison_rows.append(calculate_model_row(model_name, y_test, y_pred, y_proba))
        prediction_frames.append(build_prediction_rows(model_name, customer_ids_test, y_test, y_pred, y_proba))

    comparison_df = pd.DataFrame(comparison_rows).sort_values("roc_auc", ascending=False)
    comparison_df.insert(1, "train_rows", len(y_train))
    comparison_df.insert(2, "test_rows", len(y_test))
    comparison_df.insert(3, "feature_count", X.shape[1])
    comparison_df.insert(4, "numeric_feature_count", len(numeric_features))
    comparison_df.insert(5, "categorical_feature_count", len(categorical_features))

    comparison_path = METRICS_DIR / "model_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)

    predictions_df = pd.concat(prediction_frames, ignore_index=True)
    predictions_path = PREDICTIONS_DIR / "model_comparison_predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)

    summary_path = METRICS_DIR / "model_comparison_summary.md"
    write_summary(comparison_df, summary_path)

    print("Model comparison completed.")
    print(f"Comparison table: {comparison_path.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {summary_path.relative_to(PROJECT_ROOT)}")
    print(f"Predictions: {predictions_path.relative_to(PROJECT_ROOT)}")
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()
