from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.preprocess import build_preprocessor, get_feature_columns, split_features_target
from src.models.evaluate import (
    build_classification_report,
    build_confusion_matrix,
    build_prediction_frame,
    calculate_binary_metrics,
    ensure_output_dirs,
)


DATA_PATH = PROJECT_ROOT / "data" / "processed" / "model_dataset.csv"
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions"

RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Model dataset not found: {path}")

    return pd.read_csv(path)


def build_baseline_pipeline(X: pd.DataFrame) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(X)),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def save_metrics(metrics: dict[str, object]) -> Path:
    output_path = METRICS_DIR / "baseline_metrics.json"
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return output_path


def save_classification_report(report: str) -> Path:
    output_path = METRICS_DIR / "baseline_classification_report.txt"
    output_path.write_text(report, encoding="utf-8")
    return output_path


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

    pipeline = build_baseline_pipeline(X_train)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    model_metrics = calculate_binary_metrics(y_test, y_pred, y_proba)
    metrics_output = {
        "model": "LogisticRegression",
        "target": "churn",
        "positive_class": "Yes",
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "feature_count": int(X.shape[1]),
        "numeric_feature_count": len(numeric_features),
        "categorical_feature_count": len(categorical_features),
        **{metric: round(float(value), 6) for metric, value in model_metrics.items()},
    }

    metrics_path = save_metrics(metrics_output)

    report = build_classification_report(y_test, y_pred)
    report_path = save_classification_report(report)

    confusion_matrix_df = build_confusion_matrix(y_test, y_pred)
    confusion_matrix_path = METRICS_DIR / "baseline_confusion_matrix.csv"
    confusion_matrix_df.to_csv(confusion_matrix_path)

    predictions_df = build_prediction_frame(customer_ids_test, y_test, y_pred, y_proba)
    predictions_path = PREDICTIONS_DIR / "baseline_test_predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)

    print("Baseline training completed.")
    print(f"Metrics: {metrics_path.relative_to(PROJECT_ROOT)}")
    print(f"Classification report: {report_path.relative_to(PROJECT_ROOT)}")
    print(f"Confusion matrix: {confusion_matrix_path.relative_to(PROJECT_ROOT)}")
    print(f"Predictions: {predictions_path.relative_to(PROJECT_ROOT)}")
    print(json.dumps(metrics_output, indent=2))


if __name__ == "__main__":
    main()
